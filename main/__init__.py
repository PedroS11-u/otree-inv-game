from otree.api import *
import random

c = cu
doc = ''

class C(BaseConstants):
    NAME_IN_URL = 'main'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 8  # Updated to 8 rounds

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class WaitForOthers(WaitPage):
    wait_for_all_groups = True  # Ensures all participants are synchronized

class WaitForNextRound(WaitPage):
    wait_for_all_groups = True  # Ensures all players wait for each other



class Player(BasePlayer):
    amount = models.IntegerField()
    endowment_change = models.FloatField(initial=0)  # Initialized to 0
    total_funds = models.FloatField(initial=100)  # Starting funds
    rank = models.IntegerField()
    interest_earned = models.FloatField(initial=0)  # Field to store interest earned



def get_endowment(player: Player):
    """Calculate the player's current funds."""
    if player.round_number == 1:
        return 100  # Initial funds
    return player.in_round(player.round_number - 1).total_funds



def amount_choices(player: Player):
    """Generate valid investment options."""
    current_funds = get_endowment(player)
    return list(range(0, int(current_funds) + 1, 10))  # Adjusting step size to 10 for cleaner options




def investment_result(player: Player):
    """Determine the result of the investment, including 5% interest on uninvested money."""
    amount = player.amount
    test = random.random()

    if test <= 0.5:  # 50% chance of success
        player.endowment_change = round(amount, 2)  # Money doubles
    else:
        player.endowment_change = round(-amount, 2)  # Money disappears

    # Calculate interest on uninvested money
    current_funds = get_endowment(player)
    uninvested_money = current_funds - amount
    interest = round(uninvested_money * 0.05, 2)  # 5% interest

    # Update total funds and round it
    player.total_funds = round(current_funds + player.endowment_change + interest, 2)

    # Store interest for display in the round results
    player.interest_earned = interest

    # Debugging output
    print(f"DEBUG: Player {player.id_in_group}, Round {player.round_number}, Invested: {amount}, Interest: {interest}, Total Funds: {player.total_funds}")





class Choose(Page):
    form_model = 'player'
    form_fields = ['amount']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            current_funds=get_endowment(player),
            current_round=player.round_number  # Pass the current round number
        )


    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        print(f"DEBUG: Player {player.id_in_group}, Round {player.round_number}, Submitted Investment: {player.amount}")
        # Call investment result function
        investment_result(player)



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
        earnings = round(player.endowment_change or 0, 2)
        interest = round(player.interest_earned or 0, 2)
        total_funds = round(player.total_funds, 2)

        print(f"DEBUG: RoundResults - Player {player.id_in_group}, Round {player.round_number}, Earnings: {earnings}, Interest: {interest}, Total Funds: {total_funds}")
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




