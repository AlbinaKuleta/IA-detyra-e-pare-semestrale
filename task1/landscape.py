"""
Kalkulimi i landscape-it per Social Golfers Problem.

1. Madhesia e hapesires se kerkimit (sa gjendje ekzistojne) per reprezentime
   te ndryshme dhe sa e zvogelon thyerja e simetrive.
2. Fitness landscape: shperndarja e objective function f(S) (numri i takimeve
   te perseritura) mbi orare te rastesishme, si dhe struktura e fqinjesise
   (swap i dy lojtareve nga grupe te ndryshme ne te njejten jave).

Perdorimi:
    python landscape.py                  # g=8, p=4, w=10
    python landscape.py -g 8 -p 4 -w 7 --samples 5000
"""

import argparse
import random
from collections import Counter
from math import comb, factorial, log10

from social_golfers import objective, upper_bound_weeks


# ---------------------------------------------------------------------------
# 1. Madhesia e hapesires se kerkimit
# ---------------------------------------------------------------------------

def week_partitions(g, p):
    """Numri i menyrave per ndarjen e n = g*p lojtareve ne g grupe (pa rend)
    me nga p lojtare:  n! / ((p!)^g * g!)."""
    n = g * p
    return factorial(n) // (factorial(p) ** g * factorial(g))


def search_space(g, p, w):
    n = g * p
    P = week_partitions(g, p)
    return {
        # cdo slot (w*n slote) merr cilindo lojtar nga domain-i {0..n-1}
        "naive: n^(n*w)": (n * w) * log10(n),
        # cdo jave eshte nje permutacion i lojtareve
        "permutacione: (n!)^w": w * log10(factorial(n)),
        # cdo jave eshte nje ndarje ne grupe (pa rend brenda/ndermjet grupeve)
        "ndarje: P^w": w * log10(P),
        # java 1 fikse + javet pa rend (w! renditje ekuivalente)
        "me simetri: P^(w-1) / (w-1)!": (w - 1) * log10(P) - log10(factorial(w - 1)),
    }


def pair_count_bound(g, p):
    """Numri i ciftave dhe sa cifte konsumon cdo jave."""
    n = g * p
    return comb(n, 2), g * comb(p, 2)


# ---------------------------------------------------------------------------
# 2. Fitness landscape
# ---------------------------------------------------------------------------

def random_schedule(g, p, w, rng):
    n = g * p
    schedule = []
    for _ in range(w):
        players = list(range(n))
        rng.shuffle(players)
        schedule.append([players[i * p:(i + 1) * p] for i in range(g)])
    return schedule


def neighbours(schedule):
    """Te gjithe fqinjet: swap i dy lojtareve nga grupe te ndryshme ne nje jave."""
    for wi, week in enumerate(schedule):
        g = len(week)
        for a in range(g):
            for b in range(a + 1, g):
                for i in range(len(week[a])):
                    for j in range(len(week[b])):
                        new = [list(map(list, wk)) for wk in schedule]
                        new[wi][a][i], new[wi][b][j] = new[wi][b][j], new[wi][a][i]
                        yield new


def histogram(values, width=50, max_rows=15):
    lo, hi = min(values), max(values)
    step = max(1, -(-(hi - lo + 1) // max_rows))   # ceil
    counts = Counter((v - lo) // step for v in values)
    top = max(counts.values())
    lines = []
    for b in range(max(counts) + 1):
        start = lo + b * step
        label = f"{start}" if step == 1 else f"{start}-{start + step - 1}"
        bar = "#" * round(width * counts[b] / top)
        lines.append(f"   f={label:>9}: {counts[b]:>6}  {bar}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Landscape i Social Golfers Problem")
    ap.add_argument("-g", type=int, default=8)
    ap.add_argument("-p", type=int, default=4)
    ap.add_argument("-w", type=int, default=10)
    ap.add_argument("--samples", type=int, default=2000)
    ap.add_argument("--neigh-samples", type=int, default=30,
                    help="sa orare te rastesishme analizohen per fqinjesine")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    g, p, w = args.g, args.p, args.w
    n = g * p
    rng = random.Random(args.seed)

    print(f"=== Landscape: n={n}, g={g}, p={p}, w={w} ===\n")

    print("1) Madhesia e hapesires se kerkimit (log10 e numrit te gjendjeve)")
    print(f"   Ndarje te mundshme per nje jave P = {week_partitions(g, p):,}"
          f"  (~10^{log10(week_partitions(g, p)):.2f})")
    for name, lg in search_space(g, p, w).items():
        print(f"   {name:<32} ~ 10^{lg:.2f}")
    total_pairs, per_week = pair_count_bound(g, p)
    print(f"\n   Cifte gjithsej C(n,2) = {total_pairs}; cdo jave perdor {per_week} cifte")
    print(f"   => w <= {total_pairs}/{per_week} = {total_pairs / per_week:.2f}; "
          f"kufiri per lojtar w <= (n-1)/(p-1) = {upper_bound_weeks(g, p)}")
    print(f"   Me w={w}: perdoren {w * per_week} nga {total_pairs} cifte "
          f"({100 * w * per_week / total_pairs:.1f}%)")

    print(f"\n2) Shperndarja e f(S) mbi {args.samples} orare te rastesishme")
    values = [objective(random_schedule(g, p, w, rng)) for _ in range(args.samples)]
    mean = sum(values) / len(values)
    print(f"   min={min(values)}  max={max(values)}  mesatarja={mean:.2f}")
    print(f"   orare valide (f=0) te gjetura rastesisht: {values.count(0)}")
    print(histogram(values))

    print(f"\n3) Struktura lokale (fqinj = swap ne te njejten jave), "
          f"{args.neigh_samples} orare")
    better = equal = worse = 0
    local_minima = 0
    for _ in range(args.neigh_samples):
        s = random_schedule(g, p, w, rng)
        f0 = objective(s)
        b = e = wr = 0
        for nb in neighbours(s):
            f1 = objective(nb)
            if f1 < f0:
                b += 1
            elif f1 == f0:
                e += 1
            else:
                wr += 1
        better, equal, worse = better + b, equal + e, worse + wr
        if b == 0 and f0 > 0:
            local_minima += 1
    tot = better + equal + worse
    print(f"   fqinje per gjendje: {tot // args.neigh_samples}")
    print(f"   me te mire: {100 * better / tot:.1f}%   te barabarte (plateau): "
          f"{100 * equal / tot:.1f}%   me te keq: {100 * worse / tot:.1f}%")
    print(f"   minimume lokale (pa asnje fqinj me te mire, f>0): "
          f"{local_minima}/{args.neigh_samples}")


if __name__ == "__main__":
    main()
