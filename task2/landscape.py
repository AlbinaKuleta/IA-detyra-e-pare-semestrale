"""
Kalkulimi i landscape-it per Sudoku.

1. Madhesia e hapesires se kerkimit per tre reprezentime:
     a) naive:        cdo qelize bosh merr 1..9            -> 9^e
     b) rreshta:      cdo rresht eshte permutacion i numrave qe i mungojne
                      (kufizimi i rreshtit plotesohet gjithmone) -> prod(m_r!)
     c) domain-e te reduktuara: cdo qelize merr vetem vlerat qe nuk jane
                      ne rreshtin/kolonen/kutine e saj      -> prod(|D_i|)
2. Fitness landscape (reprezentimi b): shperndarja e f(S) per gjendje te
   rastesishme, fqinjesia (swap i dy qelizave jo-fikse ne te njejtin rresht)
   dhe sa shpesh hill climbing ngec ne minimume lokale.

Perdorimi:
    python landscape.py                 # te gjitha nivelet
    python landscape.py --level hard --samples 5000
"""

import argparse
import random
from collections import Counter
from math import factorial, log10

from puzzles import PUZZLES, parse
from sudoku import candidates, objective


# ---------------------------------------------------------------------------
# 1. Madhesia e hapesires se kerkimit
# ---------------------------------------------------------------------------

def missing_per_row(puzzle):
    rows = []
    for r in range(9):
        row = puzzle[r * 9:(r + 1) * 9]
        rows.append([v for v in range(1, 10) if v not in row])
    return rows


def search_space(puzzle):
    e = puzzle.count(0)
    rows = missing_per_row(puzzle)
    cand = candidates(puzzle)
    return {
        "naive: 9^e": e * log10(9),
        "permutacione rreshtash: prod(m_r!)": sum(log10(factorial(len(m))) for m in rows),
        "domain-e te reduktuara: prod(|D_i|)": sum(log10(bin(m).count("1")) for m in cand.values()),
    }


# ---------------------------------------------------------------------------
# 2. Fitness landscape
# ---------------------------------------------------------------------------

def random_state(puzzle, rows, rng):
    """Gjendje e rastesishme: cdo rresht mbushet me nje permutacion
    te rastesishem te numrave qe i mungojne."""
    grid = list(puzzle)
    for r, missing in enumerate(rows):
        vals = missing[:]
        rng.shuffle(vals)
        for c in range(9):
            if grid[r * 9 + c] == 0:
                grid[r * 9 + c] = vals.pop()
    return grid


def swaps(puzzle):
    """Te gjitha levizjet: cifte qelizash jo-fikse ne te njejtin rresht."""
    moves = []
    for r in range(9):
        free = [r * 9 + c for c in range(9) if puzzle[r * 9 + c] == 0]
        moves += [(a, b) for k, a in enumerate(free) for b in free[k + 1:]]
    return moves


def neighbour_stats(grid, moves):
    f0 = objective(grid)
    better = equal = worse = 0
    for a, b in moves:
        grid[a], grid[b] = grid[b], grid[a]
        f1 = objective(grid)
        grid[a], grid[b] = grid[b], grid[a]
        if f1 < f0:
            better += 1
        elif f1 == f0:
            equal += 1
        else:
            worse += 1
    return better, equal, worse


def hill_climb(grid, moves):
    """Steepest descent: gjithmone merr fqinjin me te mire; ndalet kur
    asnje fqinj nuk eshte me i mire (minimum lokal ose zgjidhje)."""
    f = objective(grid)
    while f > 0:
        best, best_move = f, None
        for a, b in moves:
            grid[a], grid[b] = grid[b], grid[a]
            f1 = objective(grid)
            grid[a], grid[b] = grid[b], grid[a]
            if f1 < best:
                best, best_move = f1, (a, b)
        if best_move is None:
            break
        a, b = best_move
        grid[a], grid[b] = grid[b], grid[a]
        f = best
    return f


def analyse(name, puzzle, samples, climbs, rng):
    e = puzzle.count(0)
    print(f"=== {name} | {81 - e} te dhena, {e} qeliza bosh ===")
    print("1) Madhesia e hapesires se kerkimit:")
    for label, lg in search_space(puzzle).items():
        print(f"   {label:<38} ~ 10^{lg:.2f}")

    rows = missing_per_row(puzzle)
    moves = swaps(puzzle)
    values = [objective(random_state(puzzle, rows, rng)) for _ in range(samples)]
    counts = Counter(values)
    print(f"2) f(S) mbi {samples} gjendje te rastesishme: "
          f"min={min(values)} max={max(values)} mesatarja={sum(values) / samples:.2f}")
    mode = counts.most_common(1)[0][0]
    print(f"   vlera me e shpeshte f={mode}; gjendje me f=0: {counts[0]}")

    b = eq = w = 0
    for _ in range(20):
        x, y, z = neighbour_stats(random_state(puzzle, rows, rng), moves)
        b, eq, w = b + x, eq + y, w + z
    tot = b + eq + w
    print(f"3) Fqinjesia ({len(moves)} fqinj per gjendje): me te mire {100 * b / tot:.1f}%, "
          f"plateau {100 * eq / tot:.1f}%, me te keq {100 * w / tot:.1f}%")

    finals = [hill_climb(random_state(puzzle, rows, rng), moves) for _ in range(climbs)]
    solved = finals.count(0)
    stuck = sorted(f for f in finals if f > 0)
    print(f"4) Hill climbing nga {climbs} pika te rastesishme: {solved} arriten f=0, "
          f"{climbs - solved} ngecen ne minimum lokal"
          + (f" (f = {min(stuck)}..{max(stuck)}, mesatarisht {sum(stuck) / len(stuck):.1f})"
             if stuck else ""))
    print()


def main():
    ap = argparse.ArgumentParser(description="Landscape i Sudoku")
    ap.add_argument("--level", choices=["easy", "medium", "hard", "all"], default="all")
    ap.add_argument("--samples", type=int, default=2000)
    ap.add_argument("--climbs", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    levels = ["easy", "medium", "hard"] if args.level == "all" else [args.level]
    for level in levels:
        for k, p in enumerate(PUZZLES[level], 1):
            analyse(f"{level.capitalize()} #{k}", parse(p), args.samples, args.climbs, rng)


if __name__ == "__main__":
    main()
