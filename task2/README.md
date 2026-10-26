# Detyra 2 – Sudoku Solver

**Teknikat e painformuara të kërkimit (Uninformed Search Techniques)**

## 1. Përshkrimi i problemit

Sudoku është një rrjetë 9×9 e ndarë në 9 kuti 3×3. Disa qeliza janë të plotësuara që në fillim (givens). Qëllimi është të plotësohen qelizat bosh me numrat 1–9, ashtu që çdo **rresht**, çdo **kolonë** dhe çdo **kuti 3×3** të përmbajë secilin numër saktësisht një herë.

Programi i zgjidh sudokut në tri nivele: **Easy**, **Medium** dhe **Hard** (shih [puzzles.py](puzzles.py)).

## 2. Modelimi i problemit

Problemi modelohet si **Constraint Satisfaction Problem (CSP)**, i cili zgjidhet me kërkim në hapësirën e gjendjeve:

| Elementi | Në këtë problem |
|---|---|
| **Gjendja** | Rrjeta e plotësuar pjesërisht, pa asnjë konflikt |
| **Gjendja fillestare** | Sudoku i dhënë (vetëm givens) |
| **Veprimi (operatori)** | Vendos një numër 1–9 në një qelizë bosh, nëse nuk bie ndesh me rreshtin, kolonën ose kutinë |
| **Testi i qëllimit** | Nuk ka më qeliza bosh |
| **Kostoja** | Çdo veprim kushton 1. Të gjitha zgjidhjet janë në thellësinë `e` (numri i qelizave bosh) |

### Kufizimet

1. Çdo rresht ka numrat 1–9 pa përsëritje (9 kufizime).
2. Çdo kolonë ka numrat 1–9 pa përsëritje (9 kufizime).
3. Çdo kuti 3×3 ka numrat 1–9 pa përsëritje (9 kufizime).
4. Qelizat e dhëna (givens) nuk ndryshohen.

Kufizimet 1–3 janë 27 kufizime **all-different**.

## 3. Reprezentimi

```
grid = [v0, v1, ..., v80]          grid[r*9 + c] = vlera në rreshtin r, kolonën c
                                   0 = qelizë bosh
```

- **Variablat:** qelizat bosh `X[r][c]`. Numri i tyre `e` është 49–60 te sudokut tona.
- **Domain-i:** `D = {1, 2, …, 9}`. Gjatë kërkimit, domain-i i çdo qelize reduktohet në vlerat që nuk janë ende në rreshtin, kolonën ose kutinë e saj (**forward checking**).
- **Struktura ndihmëse:** për çdo rresht, kolonë dhe kuti mbahet një bitmask me numrat e përdorur, prandaj kandidatët e një qelize janë `ALL & ~(rresht | kolonë | kuti)`.
- **Njësitë:** lista `UNITS` me 27 njësitë (rreshtat, kolonat dhe kutitë), që përdoret nga objective function.

## 4. Objective function

```
f(S) = Σ_{u ∈ 27 njësitë} (9 − |{vlerat e ndryshme në u}|)
```

- Për një rrjetë të plotë, `f(S)` numëron sa përsëritje ka në të gjitha rreshtat, kolonat dhe kutitë.
- `f(S) = 0` vlen atëherë dhe vetëm atëherë kur rrjeta është zgjidhje valide.
- Qëllimi është **minimizimi** i `f(S)` deri në 0.

Implementimi gjendet te `objective()` në [sudoku.py](sudoku.py). Pas çdo zgjidhjeje, programi shtyp `f(S) = 0` dhe `valid = True` si verifikim.

## 5. Landscape

Rezultatet merren me `python landscape.py`.

### Madhësia e hapësirës së kërkimit

Krahasohen tri reprezentime:
- **naive:** çdo qelizë bosh merr 1–9, pra `9^e`;
- **permutacione rreshtash:** çdo rresht plotësohet me një permutacion të numrave që i mungojnë, pra `Π m_r!`;
- **domain-e të reduktuara:** çdo qelizë merr vetëm vlerat e lejuara nga givens, pra `Π |D_i|`.

| Sudoku | Givens | Bosh | Naive `9^e` | Permutacione `Π m_r!` | Domain-e të reduktuara `Π \|D_i\|` |
|---|---|---|---|---|---|
| Easy #1 | 30 | 51 | ~10^48.7 | ~10^23.4 | ~10^22.6 |
| Easy #2 | 32 | 49 | ~10^46.8 | ~10^21.9 | ~10^23.2 |
| Medium #1 | 28 | 53 | ~10^50.6 | ~10^25.1 | ~10^28.6 |
| Medium #2 | 24 | 57 | ~10^54.4 | ~10^28.5 | ~10^32.1 |
| Hard #1 | 21 | 60 | ~10^57.3 | ~10^30.8 | ~10^35.8 |
| Hard #2 | 21 | 60 | ~10^57.3 | ~10^30.8 | ~10^37.0 |

Sa më pak givens, aq më e madhe është hapësira. Megjithatë, secili nga këta sudoku ka **vetëm një zgjidhje**.

### Fitness landscape

Kjo analizë përdor reprezentimin me permutacione rreshtash. Fqinj quhen dy gjendje që dallojnë vetëm nga një swap i dy qelizave jo-fikse në të njëjtin rresht.

- **Gjendjet e rastësishme** kanë `f(S)` mesatarisht 44–52, në intervalin 29–67. Asnjë nga 2000 gjendjet e rastësishme për nivel nuk ka `f = 0`.
- **Fqinjësia:** rreth 38% e fqinjëve janë më të mirë, rreth 24% janë të barabartë (**plateau**) dhe rreth 37% janë më të këqij.
- **Hill climbing** (steepest descent), nisur nga 20 pika të rastësishme për çdo sudoku, **ngec gjithmonë në minimum lokal** me `f = 4–21`, edhe te nivelet Easy.

Landscape-i është pra shumë **i thyer (rugged)**: ka shumë minimume lokale dhe plateau, dhe vetëm një minimum global. Kjo e arsyeton përdorimin e një kërkimi sistematik si BFS, i cili e eksploron hapësirën plotësisht dhe e garanton zgjidhjen.

## 6. Breadth First Search (BFS) me Backtracking

Implementimi gjendet te `bfs_solve()` në [sudoku.py](sudoku.py).

**Algoritmi:**
- Gjendjet ruhen në një radhë **FIFO** (`deque`), prandaj eksplorohen **nivel pas niveli**: të gjitha gjendjet me `k` qeliza të plotësuara para atyre me `k+1`.
- Në çdo nivel plotësohet **një** qelizë: ajo me më së paku vlera të mundshme (**MRV**, Minimum Remaining Values). Kështu degëzimi mbahet sa më i vogël.
- Fëmijët e një gjendjeje janë të gjitha vlerat e lejuara për atë qelizë (forward checking).
- **Backtracking:** nëse një gjendje ka një qelizë pa asnjë vlerë të mundshme (dead end), ajo hidhet poshtë dhe dega nuk vazhdohet më. Kërkimi "kthehet" te gjendjet e tjera në radhë, dhe asnjë gjendje jo-valide nuk ruhet ose zgjerohet.

```
BFS(sudoku):
    radha ← [sudoku]
    përderisa radha nuk është bosh:
        S ← radha.pop_front()
        nëse S nuk ka qeliza bosh → kthe S            (qëllimi)
        qeliza ← qeliza bosh me më së paku kandidatë   (MRV)
        nëse qeliza ka 0 kandidatë → BACKTRACK         (dead end, hidhe S)
        për çdo vlerë v të lejuar:
            radha.push_back(S + {qeliza = v})
    kthe "nuk ka zgjidhje"
```

**Pse BFS dhe backtracking?** Te sudoku, të gjitha zgjidhjet janë në të njëjtën thellësi `e`. Për këtë arsye BFS e gjen zgjidhjen vetëm në nivelin e fundit, pasi i ka eksploruar të gjitha nivelet para tij. Pa backtracking (pa prunim), frontier-i do të rritej deri në `~9^k` gjendje. Me forward checking dhe MRV, frontier-i nuk kalon **~900 gjendje** edhe për sudokun më të vështirë.

## 7. Rezultatet

| Niveli | Sudoku | Gjendje të zgjeruara | Dead ends (backtracks) | Frontier maksimal | Koha |
|---|---|---|---|---|---|
| Easy | #1 | 52 | 0 | 1 | ~0.003 s |
| Easy | #2 | 50 | 0 | 1 | ~0.004 s |
| Medium | #1 | 162 | 11 | 9 | ~0.01 s |
| Medium | #2 | 3,034 | 205 | 186 | ~0.2 s |
| Hard | #1 "Golden Nugget" | 17,148 | 1,377 | 907 | ~1.6 s |
| Hard | #2 Arto Inkala | 18,936 | 1,799 | 888 | ~1.5 s |

- **Easy:** çdo qelizë ka gjithmonë një kandidat të vetëm, prandaj nuk ka degëzim dhe frontier-i mbetet 1.
- **Medium:** ka pak degëzim, me qindra deri në mijëra gjendje.
- **Hard:** degëzimi është i madh. Frontier-i rritet deri në rreth 900 gjendje në mes të pemës dhe pastaj ngushtohet, sepse degët jo-valide eliminohen. Me opsionin `-v` shfaqet numri i gjendjeve në çdo nivel të pemës.

Shembull (Easy #1):

```
Sudoku                     Zgjidhja
5 3 . | . 7 . | . . .      5 3 4 | 6 7 8 | 9 1 2
6 . . | 1 9 5 | . . .      6 7 2 | 1 9 5 | 3 4 8
. 9 8 | . . . | . 6 .      1 9 8 | 3 4 2 | 5 6 7
------+-------+------      ------+-------+------
8 . . | . 6 . | . . 3      8 5 9 | 7 6 1 | 4 2 3
4 . . | 8 . 3 | . . 1      4 2 6 | 8 5 3 | 7 9 1
7 . . | . 2 . | . . 6      7 1 3 | 9 2 4 | 8 5 6
------+-------+------      ------+-------+------
. 6 . | . . . | 2 8 .      9 6 1 | 5 3 7 | 2 8 4
. . . | 4 1 9 | . . 5      2 8 7 | 4 1 9 | 6 3 5
. . . | . 8 . | . 7 9      3 4 5 | 2 8 6 | 1 7 9
```

## 8. Ekzekutimi

Kërkohet Python 3.8+ dhe nuk ka nevojë për librari të jashtme.

```bash
cd task2

# Zgjidh te gjitha nivelet (Easy, Medium, Hard)
python sudoku.py

# Vetem nje nivel
python sudoku.py --level hard

# Shfaq numrin e gjendjeve ne cdo nivel te pemes BFS
python sudoku.py --level medium -v

# Sudoku i dhene nga ti (0 ose . = bosh)
python sudoku.py --puzzle 530070000600195000098000060800060003400803001700020006060000280000419005000080079

# Landscape
python landscape.py
python landscape.py --level hard --samples 5000
```
