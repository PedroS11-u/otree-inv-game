This program was made for a project in Experimental Economics using mainly Python: its an investment game with the added twist of being able to see each investor's position in a ranking of wealth.

Its goal was to test the impact of social facilitation and perceived competitiveness on investor's choices.

It was built on top of an already existing otree layout and it works like this:

  Each investor starts with a randomly assigned tier of wealth, each with different values;
  
  In every round (the deafult is 4), the user can choose an amount of their wealth to invest which has a 50/50 chance of either doubling their investment or losing it all, the rest of their wealth earns interest;

  In the begining of the second half of rounds (by default the third and fourth), the investors get to see their position in a ranking of wealth;

With this setup we're able to compare each of the treatments and test the hypothesis of there being a significant change in investors behaviour.
