# Python script replicating the hedge simulation and optimization originally implemented in HTML/JavaScript.
import argparse
from dataclasses import dataclass
from typing import List, Tuple

ROUND_PROMO_BETS = [1500, 3000, 6000]
RTP = 0.95
PLAYTHROUGH_REQUIRED = 45000
INITIAL_PROMO = 1500

@dataclass
class Round:
    promo_bet: float
    hedge: float

def _generate_outcomes() -> List[Tuple[List[str], int]]:
    """Generate unique truncated outcomes and their frequencies."""
    outcome_map = {}
    for i in range(8):
        binary = format(i, "03b")
        result = ["player" if c == "0" else "banker" for c in binary]
        key = []
        for r in result:
            key.append(r)
            if r == "banker":
                break
        key_str = ",".join(key)
        outcome_map[key_str] = outcome_map.get(key_str, 0) + 1
    outcomes = []
    for key_str, freq in outcome_map.items():
        outcomes.append((key_str.split(','), freq))
    return outcomes


def simulate(h1: float, h2: float, h3: float) -> None:
    rounds = [
        Round(ROUND_PROMO_BETS[0], h1),
        Round(ROUND_PROMO_BETS[1], h2),
        Round(ROUND_PROMO_BETS[2], h3),
    ]
    outcomes = _generate_outcomes()

    expected_final = 0.0
    min_final = float("inf")
    max_final = float("-inf")
    output_lines = []
    count = 1

    for result, freq in outcomes:
        probability = freq / 8
        promo_balance = 0.0
        total_hedge = 0.0
        hedge_winnings = 0.0
        promo_wagered = 0.0
        banker_hit = False
        current_hedge = 0.0
        rounds_played = len(result)

        for j, r in enumerate(result):
            promo_bet = rounds[j].promo_bet
            hedge = rounds[j].hedge
            current_hedge = hedge
            promo_wagered += promo_bet
            total_hedge += hedge
            if r == "player":
                promo_balance += promo_bet
            else:
                hedge_winnings = hedge * 0.95
                banker_hit = True
                break

        final_value = 0.0
        out = [f"Outcome {count}: {', '.join(r.upper() for r in result)} ({freq}/8)"]

        if banker_hit:
            net_cash_profit = hedge_winnings - (total_hedge - current_hedge)
            final_value = net_cash_profit
            out.append(f"- Banker won in round {rounds_played}, stopped betting")
            out.append(f"- Hedge Winnings (0.95 x last hedge): ${hedge_winnings:.2f}")
            out.append(
                f"- Hedge Cost Before Banker Win: ${(total_hedge - current_hedge):.2f}")
            out.append(f"- Net Cash Profit: ${net_cash_profit:.2f}\n")
        else:
            remaining_playthrough = PLAYTHROUGH_REQUIRED - promo_wagered
            expected_value = remaining_playthrough * RTP
            net_profit = promo_balance - total_hedge - (
                remaining_playthrough - expected_value)
            final_value = INITIAL_PROMO + net_profit
            out.append(f"- Final Promo Balance: ${promo_balance:.2f}")
            out.append(f"- Total Hedge Cost: ${total_hedge:.2f}")
            out.append(
                f"- Remaining Playthrough: ${remaining_playthrough:.2f}")
            out.append(
                f"- Expected Value of Playthrough: ${expected_value:.2f}")
            out.append(f"- Net Profit: ${net_profit:.2f}")
            out.append(
                f"- Final Profit vs. Initial $1500: ${final_value:.2f}\n")

        expected_final += final_value * probability
        min_final = min(min_final, final_value)
        max_final = max(max_final, final_value)
        output_lines.extend(out)
        count += 1

    output_lines.append("===========================")
    output_lines.append(
        f"Expected Final Value (weighted by probability): ${expected_final:.2f}")
    output_lines.append(f"Minimum Final Value: ${min_final:.2f}")
    output_lines.append(f"Maximum Final Value: ${max_final:.2f}")

    print("\n".join(output_lines))


def _compute_expected_value(h1: float, h2: float, h3: float) -> Tuple[float, float, float]:
    hedges = [h1, h2, h3]
    outcomes = [
        (['player', 'player', 'player'], 1),
        (['player', 'player', 'banker'], 1),
        (['player', 'banker'], 2),
        (['banker'], 4),
    ]
    expected = 0.0
    min_val = float('inf')
    max_val = float('-inf')

    for path, weight in outcomes:
        promo_balance = 0.0
        total_hedge = 0.0
        promo_wagered = 0.0
        hedge_winnings = 0.0
        current_hedge = 0.0
        banker_hit = False
        for i, r in enumerate(path):
            promo_bet = ROUND_PROMO_BETS[i]
            hedge = hedges[i]
            current_hedge = hedge
            promo_wagered += promo_bet
            total_hedge += hedge
            if r == 'player':
                promo_balance += promo_bet
            else:
                hedge_winnings = hedge * 0.95
                banker_hit = True
                break
        if banker_hit:
            value = hedge_winnings - (total_hedge - current_hedge)
        else:
            value = INITIAL_PROMO + (
                promo_balance - total_hedge - (
                    PLAYTHROUGH_REQUIRED - promo_wagered -
                    (PLAYTHROUGH_REQUIRED - promo_wagered) * RTP
                )
            )
        expected += value * (weight / 8)
        min_val = min(min_val, value)
        max_val = max(max_val, value)
    return expected, min_val, max_val


def optimize() -> None:
    h1_base, h2_base, h3_base = 1300, 2650, 5500
    step = 50
    rng = 10
    results = []
    for i in range(-rng, rng + 1):
        for j in range(-rng, rng + 1):
            for k in range(-rng, rng + 1):
                h1 = h1_base + i * step
                h2 = h2_base + j * step
                h3 = h3_base + k * step
                if h1 > 0 and h2 > 0 and h3 > 0:
                    ev, min_v, max_v = _compute_expected_value(h1, h2, h3)
                    results.append((h1, h2, h3, ev, min_v, max_v))
    results.sort(key=lambda x: x[3], reverse=True)
    header = f"{'Hedge 1':>7} {'Hedge 2':>7} {'Hedge 3':>7} {'EV':>12} {'Min':>8} {'Max':>8}"
    print(header)
    for h1, h2, h3, ev, min_v, max_v in results:
        print(f"{h1:7.0f} {h2:7.0f} {h3:7.0f} {ev:12.2f} {min_v:8.2f} {max_v:8.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Baccarat hedge tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sim_parser = subparsers.add_parser("simulate", help="Run simulation")
    sim_parser.add_argument("h1", type=float, nargs="?", default=1300)
    sim_parser.add_argument("h2", type=float, nargs="?", default=2650)
    sim_parser.add_argument("h3", type=float, nargs="?", default=5250)

    subparsers.add_parser("optimize", help="Run grid search optimization")

    args = parser.parse_args()

    if args.command == "simulate":
        simulate(args.h1, args.h2, args.h3)
    elif args.command == "optimize":
        optimize()


if __name__ == "__main__":
    main()
