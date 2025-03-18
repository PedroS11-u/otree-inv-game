from otree.api import *
import random

c = cu
doc = ''

class C(BaseConstants):
    NAME_IN_URL = 'main'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 8  # Updated to 8 rounds

class Subsession(BaseSubsession):
    def creating_session(self):
        print("DEBUG: creating_session method is running.")
        players = self.get_players()

        print(f"DEBUG: Total number of players = {len(players)}")

        # Assign tiers based on player order (id_in_group)
        for p in players:
            if p.id_in_group % 3 == 1:  # 1st in the sequence
                p.tier = 'Low'
                p.total_funds = 50
            elif p.id_in_group % 3 == 2:  # 2nd in the sequence
                p.tier = 'Medium'
                p.total_funds = 100
            else:  # 3rd in the sequence
                p.tier = 'High'
                p.total_funds = 200

            # Debugging output
            print(f"DEBUG: Player {p.id_in_group} -> Tier: {p.tier}, Total Funds: {p.total_funds}")


class Group(BaseGroup):
    pass

class WaitForOthers(WaitPage):
    wait_for_all_groups = True  # Ensures all participants are synchronized

class WaitForNextRound(WaitPage):
    wait_for_all_groups = True  # Ensures all players wait for each other



class Player(BasePlayer):
    amount = models.IntegerField()
    endowment_change = models.FloatField(initial=0)  # Initialized to 0
    total_funds = models.FloatField()  # Starting funds set dynamically
    rank = models.IntegerField()
    interest_earned = models.FloatField(initial=0)  # Field to store interest earned
    tier = models.StringField()  # Field to store the player's tier


def get_endowment(player: Player):
    # Assign tier if it's not already set
    if player.tier is None:
        if player.id_in_group % 3 == 1:
            player.tier = 'Low'
            player.total_funds = 50
        elif player.id_in_group % 3 == 2:
            player.tier = 'Medium'
            player.total_funds = 100
        else:
            player.tier = 'High'
            player.total_funds = 200
        print(f"DEBUG: Lazy assignment -> Player {player.id_in_group}, Tier: {player.tier}, Total Funds: {player.total_funds}")

    # For round 1, return assigned funds
    if player.round_number == 1:
        return player.total_funds

    # Retrieve funds from the prior round
    prior_round_funds = player.in_round(player.round_number - 1).total_funds
    if prior_round_funds is None or prior_round_funds <= 0:
        print(f"ERROR: Player {player.id_in_group}, Round {player.round_number} -> prior round total_funds is invalid ({prior_round_funds}). Assigning default value (100).")
        prior_round_funds = 100

    return prior_round_funds



def amount_choices(player: Player):
    """Generate valid investment options."""
    current_funds = get_endowment(player) or 0  # Fallback to 0 if None
    print(f"DEBUG: Player {player.id_in_group}, Round {player.round_number}, Current Funds: {current_funds}")
    return list(range(0, int(current_funds) + 1, 10))  # Allow increments of 10



def investment_result(player: Player):
    """Determine the result of the investment, including 5% interest on uninvested money."""
    amount = player.amount
    test = random.random()

    # Calculate earnings based on success/failure
    if test <= 0.5:  # 50% chance of success
        player.endowment_change = round(amount, 2)  # Money doubles
    else:
        player.endowment_change = round(-amount, 2)  # Money disappears

    # Calculate interest on uninvested money
    current_funds = get_endowment(player)
    uninvested_money = current_funds - amount
    interest = round(uninvested_money * 0.05, 2)  # 5% interest

    # Update total funds
    player.total_funds = round(current_funds + player.endowment_change + interest, 2)
    player.interest_earned = interest

    # Debugging
    print(f"DEBUG: Player {player.id_in_group}, Tier: {player.tier}, Round: {player.round_number}, Invested: {amount}, Earnings: {player.endowment_change}, Interest: {interest}, Total Funds: {player.total_funds}")


class Choose(Page):
    form_model = 'player'
    form_fields = ['amount']

    @staticmethod
    def vars_for_template(player: Player):
        if player.tier is None:
            print(f"ERROR: Player {player.id_in_group} -> Missing tier. Assigning default 'Medium'.")
            player.tier = 'Medium'  # Assign default tier if missing

        current_funds = get_endowment(player)
        print(f"DEBUG: Player {player.id_in_group}, Round {player.round_number}, Funds: {current_funds}, Tier: {player.tier}")
        return dict(
            current_funds=current_funds,
            current_round=player.round_number,
            tier=player.tier,
        )


    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Validate necessary fields before proceeding
        if not player.tier:
            print(f"ERROR: Player {player.id_in_group}, Round {player.round_number} -> Missing tier. Assigning default 'Medium'.")
            player.tier = 'Medium'
        if player.amount is None:
            print(f"ERROR: Player {player.id_in_group}, Round {player.round_number} -> Missing amount. Setting to 0.")
            player.amount = 0  # Default to 0 if amount is not set

        # Process investment results
        investment_result(player)

        # Debugging: Print relevant details after processing
        print(f"DEBUG: Player {player.id_in_group}, Round {player.round_number}, "
              f"Amount: {player.amount}, Total Funds: {player.total_funds}")


class Leaderboard(Page):
    @staticmethod
    def is_displayed(player: Player):
        """Show the leaderboard only after rounds 5-7."""
        return 5 <= player.round_number <= 7

    @staticmethod
    def vars_for_template(player: Player):
        """Generate the leaderboard."""
        participants = player.subsession.get_players()
        leaderboard = sorted(
            participants,
            key=lambda p: p.total_funds,
            reverse=True
        )
        # Create a list of dicts with ID and funds for the leaderboard
        leaderboard_data = [
            {"id": p.participant.id_in_session, "funds": p.total_funds}
            for p in leaderboard
        ]
        return dict(
            leaderboard=leaderboard_data,
            current_round=player.round_number  # Pass the current round number
        )

    
class RoundResults(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # Calculate earnings and other variables
        earnings = round(player.endowment_change or 0, 2)
        interest = round(player.interest_earned or 0, 2)
        total_funds = round(player.total_funds or 0, 2)

        print(f"DEBUG: Player {player.id_in_group}, Round {player.round_number}, Earnings: {earnings}, Interest: {interest}, Total Funds: {total_funds}")

        # Pass all necessary variables to the template
        return dict(
            earnings=earnings,
            interest=interest,
            total_funds=total_funds,
        )


class End(Page):
    @staticmethod
    def is_displayed(player: Player):
        """Show the end page after the final round."""
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        # Get all players in the session
        participants = player.subsession.get_players()

        # Sort players by their total funds in descending order
        leaderboard = sorted(
            participants, key=lambda p: p.total_funds, reverse=True
        )

        # Assign ranks to players
        for index, p in enumerate(leaderboard, start=1):
            p.rank = index  # Store the rank in the Player field

        # Find the player's own rank
        player_rank = player.rank

        # Return leaderboard and player-specific details to the template
        return dict(
            Funds=player.total_funds,  # Final funds of the player
            Placement=player_rank,     # Player's rank
            Leaderboard=[
                {"rank": p.rank, "id": p.participant.id_in_session, "funds": p.total_funds}
                for p in leaderboard
            ],
        )


page_sequence = [Choose, WaitForOthers, RoundResults, Leaderboard, WaitForNextRound, End]




