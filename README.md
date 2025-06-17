Baccarat Hedge Simulation
=========================

A tool to maximize profitability from a $1500 casino promotion by simulating hedge strategies on baccarat. It calculates the expected cash value of using promo funds while placing opposing real-money bets.

Purpose
-------

The goal is to determine the optimal hedge sizes across 3 baccarat rounds so that:
- If Player A (promo side) wins, the full playthrough is completed.
- If Banker (hedge side) wins at any point, the promo is effectively converted to real money.
- The total strategy yields the highest possible expected profit.

The simulator explores outcomes and calculates:
- Expected final value (EV)
- Minimum and maximum outcomes
- Full path-by-path breakdowns

Features
--------

- Models 3-round baccarat playthroughs  
- Stops once Banker wins (real cash captured)  
- Custom hedge amounts  
- Outputs:  
  - Expected value, min, max  
  - Outcome breakdown for all 4 paths
