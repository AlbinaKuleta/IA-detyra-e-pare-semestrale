"""
Kalkulimi i landscape-it per Latin Square.

1. Madhesia e hapesires se kerkimit:
     a) naive:     cdo qelize merr 1..n            -> n^(n^2)
     b) rreshta:   cdo rresht eshte permutacion    -> (n!)^n
     c) numri i katroreve latin L(n) (zgjidhjet) dhe sa e rralle jane ato.
2. Pema e kerkimit te IDDFS: sa gjendje te vlefshme (pa konflikt) ka ne cdo
   thellesi - kjo eshte puna qe IDDFS klasik e perserit ne cdo iteracion.
3. Fitness landscape (reprezentimi b): shperndarja e f(S) per gjendje te
   rastesishme, fqinjesia (swap i dy qelizave ne te njejtin rresht) dhe sa
   shpesh hill climbing ngec ne minimume lokale.

Perdorimi:
    python landscape.py              # n = 5
    python landscape.py -n 7 --samples 5000
"""

import argparse
import random
from collections import Counter
from math import factorial, log10

from latin_square import objective

# Numri i katroreve latin te rendit n (OEIS A002860)
KNOWN_LATIN_SQUARES = {
    1: 1, 2: 2, 3: 12, 4: 576, 5: 161280, 6: 812851200,
    7: 61479419904000, 8: 108776032459082956800,
    9: 5524751496156892842531225600,
    10: 9982437658213039871725064756920320000,
    11: 776966836171770144107444346734230682311065600000,
}


# ---------------------------------------------------------------------------
# 1-2. Hapesira e kerkimit dhe pema e IDDFS
# ---------------------------------------------------------------------------

def count_tree(n):
    """Numeron gjendjet e vlefshme ne cdo thellesi te pemes (qelizat mbushen
    rresht pas rreshti). Ne thellesine n^2 jane te gjithe katroret latin."""
    per_depth = [0] * (n * n + 1)
    row_used, col_used = [0] * n, [0] * n

    def rec(depth):
        per_depth[depth] += 1
        if depth == n * n:
            return
        r, c = divmod(depth, n)
        used = row_used[r] | col_used[c]
        for v in range(1, n + 1):
            bit = 1 << v
            if not used & bit:
                row_used[r] |= bit
                col_used[c] |= bit
                rec(depth + 1)
                row_used[r] &= ~bit
                col_used[c] &= ~bit

    rec(0)
    return per_depth


def search_space(n):
    print("1) Madhesia e hapesires se kerkimit")
    print(f"   naive: n^(n^2)               ~ 10^{n * n * log10(n):.2f}")
    print(f"   permutacione rreshtash (n!)^n ~ 10^{n * log10(factorial(n)):.2f}")
    if n in KNOWN_LATIN_SQUARES:
        L = KNOWN_LATIN_SQUARES[n]
        ratio = L / factorial(n) ** n
        print(f"   katrore latin L({n}) = {L:,}  (~10^{log10(L):.2f})")
        print(f"   pjesa e gjendjeve (rreshta) qe jane zgjidhje: {ratio:.3e}")


def tree_stats(n):
    print(f"\n2) Pema e kerkimit (gjendje te vlefshme ne cdo thellesi), n = {n}")
    per_depth = count_tree(n)
    total = 0
    for d, cnt in enumerate(per_depth):
        total += cnt
        print(f"   d={d:>3}: {cnt:>10,}")
    # IDDFS klasik: iteracioni L viziton te gjitha gjendjet me thellesi <= L
    iddfs = sum(sum(per_depth[:L + 1]) for L in range(len(per_depth) - 1))
    print(f"   gjendje gjithsej ne peme: {total:,}")
    print(f"   IDDFS klasik viziton (iteracionet L < n^2): {iddfs:,} gjendje "
          f"para iteracionit te fundit")


# ---------------------------------------------------------------------------
# 3. Fitness landscape
# ---------------------------------------------------------------------------

def random_state(n, rng):
    """Cdo rresht eshte permutacion i rastesishem i 1..n, keshtu kufizimi
    i rreshtave plotesohet gjithmone; f(S) mat vetem konfliktet ne kolona."""
    rows = []
    for _ in range(n):
        row = list(range(1, n + 1))
        rng.shuffle(row)
        rows.append(row)
    return rows


def moves(n):
    return [(r, a, b) for r in range(n) for a in range(n) for b in range(a + 1, n)]


def neighbour_stats(grid, mv):
    f0 = objective(grid)
    better = equal = worse = 0
    for r, a, b in mv:
        row = grid[r]
        row[a], row[b] = row[b], row[a]
        f1 = objective(grid)
        row[a], row[b] = row[b], row[a]
        if f1 < f0:
            better += 1
        elif f1 == f0:
            equal += 1
        else:
            worse += 1
    return better, equal, worse


def hill_climb(grid, mv):
    """Steepest descent: ndalet kur asnje fqinj nuk eshte me i mire."""
    f = objective(grid)
    while f > 0:
        best, best_move = f, None
        for r, a, b in mv:
            row = grid[r]
            row[a], row[b] = row[b], row[a]
            f1 = objective(grid)
            row[a], row[b] = row[b], row[a]
            if f1 < best:
                best, best_move = f1, (r, a, b)
        if best_move is None:
            break
        r, a, b = best_move
        grid[r][a], grid[r][b] = grid[r][b], grid[r][a]
        f = best
    return f


def fitness_landscape(n, samples, climbs, rng):
    mv = moves(n)
    values = [objective(random_state(n, rng)) for _ in range(samples)]
    counts = Counter(values)
    print(f"\n3) f(S) mbi {samples} gjendje te rastesishme (n = {n}): "
          f"min={min(values)} max={max(values)} mesatarja={sum(values) / samples:.2f}")
    print(f"   gjendje me f=0 (katror latin i gjetur rastesisht): {counts[0]}")
    b = eq = w = 0
    for _ in range(20):
        x, y, z = neighbour_stats(random_state(n, rng), mv)
        b, eq, w = b + x, eq + y, w + z
    tot = b + eq + w
    print(f"   fqinjesia ({len(mv)} fqinj per gjendje): me te mire {100 * b / tot:.1f}%, "
          f"plateau {100 * eq / tot:.1f}%, me te keq {100 * w / tot:.1f}%")
    finals = [hill_climb(random_state(n, rng), mv) for _ in range(climbs)]
    solved = finals.count(0)
    stuck = [f for f in finals if f > 0]
    print(f"   hill climbing nga {climbs} pika: {solved} arriten f=0, "
          f"{climbs - solved} ngecen ne minimum lokal"
          + (f" (f = {min(stuck)}..{max(stuck)})" if stuck else ""))


def main():
    ap = argparse.ArgumentParser(description="Landscape i Latin Square")
    ap.add_argument("-n", type=int, default=5)
    ap.add_argument("--tree-n", type=int, default=4,
                    help="n per numerimin e pemes se kerkimit (default 4; n=5 zgjat ~30s)")
    ap.add_argument("--samples", type=int, default=2000)
    ap.add_argument("--climbs", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    print(f"=== Landscape: Latin Square, n = {args.n} ===\n")
    search_space(args.n)
    tree_stats(args.tree_n)
    fitness_landscape(args.n, args.samples, args.climbs, rng)


if __name__ == "__main__":
    main()
