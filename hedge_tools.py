# Python script replicating the hedge simulation and optimization originally implemented in HTML/JavaScript.
from dataclasses import dataclass
from itertools import product
from math import inf

# Constants 
ROUNDS = [1500, 3000, 6000]
RTP = 0.95
PLAYTHROUGH_REQUIRED = 45000
INITIAL_PROMO = 1500

# Fixed outcomes used in your optimizer block (with weights summing to 1)
OPT_OUTCOMES = [
    (["player", "player", "player"], 1/8),
    (["player", "player", "banker"], 1/8),
    (["player", "banker"],           2/8),
    (["banker"],                     4/8),
]

@dataclass(frozen=True)
class EvalResult:
    expected: float
    minVal: float
    maxVal: float

def compute_expected_value(h1: float, h2: float, h3: float) -> EvalResult:
    hedges = [h1, h2, h3]

    expected = 0.0
    min_val = inf
    max_val = -inf

    for path, weight in OPT_OUTCOMES:
        promo_balance = 0.0
        total_hedge = 0.0
        promo_wagered = 0.0
        hedge_winnings = 0.0
        current_hedge = 0.0
        banker_hit = False

        for i, r in enumerate(path):
            promo_bet = ROUNDS[i]
            hedge = hedges[i]
            current_hedge = hedge

            promo_wagered += promo_bet
            total_hedge += hedge

            if r == "player":
                promo_balance += promo_bet
            else:
                hedge_winnings = hedge * 0.95
                banker_hit = True
                break

        if banker_hit:
            value = hedge_winnings - (total_hedge - current_hedge)
        else:
            remaining = PLAYTHROUGH_REQUIRED - promo_wagered
            value = INITIAL_PROMO + (
                promo_balance
                - total_hedge
                - (remaining - remaining * RTP)
            )

        expected += value * weight
        min_val = min(min_val, value)
        max_val = max(max_val, value)

    return EvalResult(expected=expected, minVal=min_val, maxVal=max_val)

def run_grid_search(
    h1_base=1300, h2_base=2650, h3_base=5500, step=50, rng=10
):
    results = []
    for i, j, k in product(range(-rng, rng + 1), repeat=3):
        h1 = h1_base + i * step
        h2 = h2_base + j * step
        h3 = h3_base + k * step
        if h1 > 0 and h2 > 0 and h3 > 0:
            ev = compute_expected_value(h1, h2, h3)
            results.append((h1, h2, h3, ev.expected, ev.minVal, ev.maxVal))

    # Sort by EV descending (like your JS)
    results.sort(key=lambda x: x[3], reverse=True)
    return results

def enumerate_stop_on_banker_outcomes():
    """
    Replicates your second HTML block:
    - Enumerate 8 sequences of length 3 (player/banker)
    - Collapse each sequence at first banker
    - Count frequency
    """
    outcome_map = {}
    for bits in product([0, 1], repeat=3):
        seq = ["player" if b == 0 else "banker" for b in bits]
        key = []
        for r in seq:
            key.append(r)
            if r == "banker":
                break
        key_t = tuple(key)
        outcome_map[key_t] = outcome_map.get(key_t, 0) + 1
    return outcome_map  # dict: outcome_tuple -> freq out of 8

def simulate(hedge1: float, hedge2: float, hedge3: float):
    hedges = [hedge1, hedge2, hedge3]
    outcome_map = enumerate_stop_on_banker_outcomes()

    expected_final = 0.0
    min_final = inf
    max_final = -inf

    lines = []
    outcome_num = 1

    for outcome, freq in outcome_map.items():
        prob = freq / 8.0

        promo_balance = 0.0
        total_hedge = 0.0
        hedge_winnings = 0.0
        promo_wagered = 0.0
        banker_hit = False
        current_hedge = 0.0

        for j, r in enumerate(outcome):
            promo_bet = ROUNDS[j]
            hedge = hedges[j]
            current_hedge = hedge

            promo_wagered += promo_bet
            total_hedge += hedge

            if r == "player":
                promo_balance += promo_bet
            else:
                hedge_winnings = hedge * 0.95
                banker_hit = True
                break

        outcome_str = ", ".join(r.upper() for r in outcome)
        lines.append(f"Outcome {outcome_num}: {outcome_str} ({freq}/8)")
        outcome_num += 1

        if banker_hit:
            net_cash_profit = hedge_winnings - (total_hedge - current_hedge)
            final_value = net_cash_profit

            lines.append(f"- Banker won in round {len(outcome)}, stopped betting")
            lines.append(f"- Hedge Winnings (0.95 × last hedge): ${hedge_winnings:.2f}")
            lines.append(f"- Hedge Cost Before Banker Win: ${(total_hedge - current_hedge):.2f}")
            lines.append(f"- Net Cash Profit: ${net_cash_profit:.2f}\n")
        else:
            remaining = PLAYTHROUGH_REQUIRED - promo_wagered
            expected_value = remaining * RTP
            net_profit = promo_balance - total_hedge - (remaining - expected_value)
            final_value = INITIAL_PROMO + net_profit

            lines.append(f"- Final Promo Balance: ${promo_balance:.2f}")
            lines.append(f"- Total Hedge Cost: ${total_hedge:.2f}")
            lines.append(f"- Remaining Playthrough: ${remaining:.2f}")
            lines.append(f"- Expected Value of Playthrough: ${expected_value:.2f}")
            lines.append(f"- Net Profit: ${net_profit:.2f}")
            lines.append(f"- Final Profit vs. Initial $1500: ${final_value:.2f}\n")

        expected_final += final_value * prob
        min_final = min(min_final, final_value)
        max_final = max(max_final, final_value)

    lines.append("===========================")
    lines.append(f"Expected Final Value (weighted by probability): ${expected_final:.2f}")
    lines.append(f"Minimum Final Value: ${min_final:.2f}")
    lines.append(f"Maximum Final Value: ${max_final:.2f}")

    return "\n".join(lines)

if __name__ == "__main__":
    # Example: run grid search and print top 10 rows
    gs = run_grid_search()
    print("Top 10 grid-search results:")
    for row in gs[:10]:
        h1, h2, h3, ev, mn, mx = row
        print(f"h1={h1:>5} h2={h2:>5} h3={h3:>5} | EV=${ev:>8.2f} | min=${mn:>8.2f} | max=${mx:>8.2f}")

    print("\n--- Simulation report ---")
    print(simulate(1300, 2650, 5250))
