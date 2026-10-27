# Detyra 4 – Search Trees

**Përshkrimi:** konstruktimi i Search Tree për problemet **8-Puzzle**, **Missionaries and Cannibals** dhe **Rotating Workforce Scheduling**.

## Si ndërtohet pema

Një **search tree** fillon nga gjendja fillestare, që është rrënja e pemës. Për çdo nyje, gjenerohen fëmijët e saj, një për secilin veprim të mundshëm. Pema ndërtohet **nivel pas niveli** (BFS). Kodi i përbashkët gjendet në [search_tree.py](search_tree.py), ndërsa secili problem ka skedarin e vet me modelin.

Çdo nyje merr një status:

| Statusi | Kuptimi | Ngjyra në diagram |
|---|---|---|
| — | Nyje e zakonshme, zgjerohet | e bardhë |
| `*` | Në rrugën nga rrënja te zgjidhja | blu |
| `GOAL` | Gjendja e qëllimit | jeshile |
| `REPEATED` | Gjendja është parë më parë, prandaj nuk zgjerohet | gri |
| `INVALID` | Gjendja shkel kufizimet, prandaj nuk zgjerohet | e kuqe |
| `LIMIT` | Është arritur thellësia maksimale e vizatimit | e verdhë |

Programi i shtyp pemët si tekst. I ruan gjithashtu në folderin [output/](output/), si `.txt` dhe si `.mmd` (Mermaid). GitHub i vizaton automatikisht diagramet Mermaid më poshtë, dhe ato mund të hapen edhe te [mermaid.live](https://mermaid.live).

---

## 1. 8-Puzzle

### Modelimi

- **Gjendja:** rrjetë 3×3 me pllakat 1–8 dhe një hapësirë bosh (`_`), e ruajtur si tuple me 9 vlera.
- **Gjendja fillestare:** `1 2 3 | _ 4 6 | 7 5 8`.
- **Qëllimi:** `1 2 3 | 4 5 6 | 7 8 _`.
- **Veprimet:** hapësira bosh lëviz **Up**, **Down**, **Left** ose **Right**, nëse nuk del jashtë rrjetës.
- **Faktori i degëzimit:** 2 kur hapësira është në kënd, 3 në buzë dhe 4 në qendër.
- **Gjendjet e përsëritura:** p.sh. lëvizja Up pas Down kthen në gjendjen e mëparshme. Këto shënohen `REPEATED` dhe nuk zgjerohen.

### Pema (thellësia 3)

```
1 2 3 | _ 4 6 | 7 5 8   [*]
├── Up -> _ 2 3 | 1 4 6 | 7 5 8
│   ├── Down -> 1 2 3 | _ 4 6 | 7 5 8   [REPEATED]
│   └── Right -> 2 _ 3 | 1 4 6 | 7 5 8
│       ├── Down -> 2 4 3 | 1 _ 6 | 7 5 8   [LIMIT]
│       ├── Left -> _ 2 3 | 1 4 6 | 7 5 8   [REPEATED]
│       └── Right -> 2 3 _ | 1 4 6 | 7 5 8   [LIMIT]
├── Down -> 1 2 3 | 7 4 6 | _ 5 8
│   ├── Up -> 1 2 3 | _ 4 6 | 7 5 8   [REPEATED]
│   └── Right -> 1 2 3 | 7 4 6 | 5 _ 8
│       ├── Up -> 1 2 3 | 7 _ 6 | 5 4 8   [LIMIT]
│       ├── Left -> 1 2 3 | 7 4 6 | _ 5 8   [REPEATED]
│       └── Right -> 1 2 3 | 7 4 6 | 5 8 _   [LIMIT]
└── Right -> 1 2 3 | 4 _ 6 | 7 5 8   [*]
    ├── Up -> 1 _ 3 | 4 2 6 | 7 5 8
    │   ├── Down -> 1 2 3 | 4 _ 6 | 7 5 8   [REPEATED]
    │   ├── Left -> _ 1 3 | 4 2 6 | 7 5 8   [LIMIT]
    │   └── Right -> 1 3 _ | 4 2 6 | 7 5 8   [LIMIT]
    ├── Down -> 1 2 3 | 4 5 6 | 7 _ 8   [*]
    │   ├── Up -> 1 2 3 | 4 _ 6 | 7 5 8   [REPEATED]
    │   ├── Left -> 1 2 3 | 4 5 6 | _ 7 8   [LIMIT]
    │   └── Right -> 1 2 3 | 4 5 6 | 7 8 _   [*, GOAL]
    ├── Left -> 1 2 3 | _ 4 6 | 7 5 8   [REPEATED]
    └── Right -> 1 2 3 | 4 6 _ | 7 5 8
        ├── Up -> 1 2 _ | 4 6 3 | 7 5 8   [LIMIT]
        ├── Down -> 1 2 3 | 4 6 8 | 7 5 _   [LIMIT]
        └── Left -> 1 2 3 | 4 _ 6 | 7 5 8   [REPEATED]
```

**Pema:** 27 nyje, 9 të zgjeruara, 8 të përsëritura, 9 të ndalura nga kufiri. **Zgjidhja (3 hapa):** Right → Down → Right.

```mermaid
graph TD
    n0["1 2 3<br/>_ 4 6<br/>7 5 8"]
    class n0 path
    n0 -->|"Right"| n3
    n0 -->|"Down"| n2
    n0 -->|"Up"| n1
    n1["_ 2 3<br/>1 4 6<br/>7 5 8"]
    n1 -->|"Right"| n5
    n1 -->|"Down"| n4
    n4["1 2 3<br/>_ 4 6<br/>7 5 8<br/>↺ e perseritur"]
    class n4 repeated
    n5["2 _ 3<br/>1 4 6<br/>7 5 8"]
    n5 -->|"Right"| n14
    n5 -->|"Left"| n13
    n5 -->|"Down"| n12
    n12["2 4 3<br/>1 _ 6<br/>7 5 8"]
    class n12 limit
    n13["_ 2 3<br/>1 4 6<br/>7 5 8<br/>↺ e perseritur"]
    class n13 repeated
    n14["2 3 _<br/>1 4 6<br/>7 5 8"]
    class n14 limit
    n2["1 2 3<br/>7 4 6<br/>_ 5 8"]
    n2 -->|"Right"| n7
    n2 -->|"Up"| n6
    n6["1 2 3<br/>_ 4 6<br/>7 5 8<br/>↺ e perseritur"]
    class n6 repeated
    n7["1 2 3<br/>7 4 6<br/>5 _ 8"]
    n7 -->|"Right"| n17
    n7 -->|"Left"| n16
    n7 -->|"Up"| n15
    n15["1 2 3<br/>7 _ 6<br/>5 4 8"]
    class n15 limit
    n16["1 2 3<br/>7 4 6<br/>_ 5 8<br/>↺ e perseritur"]
    class n16 repeated
    n17["1 2 3<br/>7 4 6<br/>5 8 _"]
    class n17 limit
    n3["1 2 3<br/>4 _ 6<br/>7 5 8"]
    class n3 path
    n3 -->|"Right"| n11
    n3 -->|"Left"| n10
    n3 -->|"Down"| n9
    n3 -->|"Up"| n8
    n8["1 _ 3<br/>4 2 6<br/>7 5 8"]
    n8 -->|"Right"| n20
    n8 -->|"Left"| n19
    n8 -->|"Down"| n18
    n18["1 2 3<br/>4 _ 6<br/>7 5 8<br/>↺ e perseritur"]
    class n18 repeated
    n19["_ 1 3<br/>4 2 6<br/>7 5 8"]
    class n19 limit
    n20["1 3 _<br/>4 2 6<br/>7 5 8"]
    class n20 limit
    n9["1 2 3<br/>4 5 6<br/>7 _ 8"]
    class n9 path
    n9 -->|"Right"| n23
    n9 -->|"Left"| n22
    n9 -->|"Up"| n21
    n21["1 2 3<br/>4 _ 6<br/>7 5 8<br/>↺ e perseritur"]
    class n21 repeated
    n22["1 2 3<br/>4 5 6<br/>_ 7 8"]
    class n22 limit
    n23["1 2 3<br/>4 5 6<br/>7 8 _<br/>✓ QELLIMI"]
    class n23 goal
    n10["1 2 3<br/>_ 4 6<br/>7 5 8<br/>↺ e perseritur"]
    class n10 repeated
    n11["1 2 3<br/>4 6 _<br/>7 5 8"]
    n11 -->|"Left"| n26
    n11 -->|"Down"| n25
    n11 -->|"Up"| n24
    n24["1 2 _<br/>4 6 3<br/>7 5 8"]
    class n24 limit
    n25["1 2 3<br/>4 6 8<br/>7 5 _"]
    class n25 limit
    n26["1 2 3<br/>4 _ 6<br/>7 5 8<br/>↺ e perseritur"]
    class n26 repeated
    classDef goal fill:#2e7d32,color:#fff,stroke:#1b5e20
    classDef path fill:#1565c0,color:#fff,stroke:#0d47a1
    classDef repeated fill:#9e9e9e,color:#fff,stroke:#616161
    classDef invalid fill:#c62828,color:#fff,stroke:#8e0000
    classDef limit fill:#f9a825,color:#000,stroke:#f57f17
```

---

## 2. Missionaries and Cannibals

### Modelimi

- **Gjendja:** `(M, C, B)`, ku `M` dhe `C` janë misionarët dhe kanibalët në bregun e majtë, ndërsa `B = 1` do të thotë që varka është majtas.
- **Gjendja fillestare:** `(3, 3, 1)`. **Qëllimi:** `(0, 0, 0)`.
- **Veprimet:** varka bart `(m, c)` ∈ {1M, 2M, 1C, 2C, 1M1C}. Shigjeta `→` tregon nisjen nga e majta, `←` nisjen nga e djathta.
- **Kufizimi:** në asnjë breg kanibalët nuk mund të jenë më shumë se misionarët, kur ka të paktën një misionar atje. Gjendjet që e shkelin shënohen `INVALID`.
- **Gjendjet e përsëritura:** përdoret graph search, pra çdo gjendje zgjerohet vetëm një herë, dhe pema e plotë është e fundme.

### Pema e plotë

```
(3,3,1)  MMMCCC B~~ -   [*]
├── 1M0C → -> (2,3,0)  MMCCC ~~B M   [INVALID: majtas C > M]
├── 2M0C → -> (1,3,0)  MCCC ~~B MM   [INVALID: majtas C > M]
├── 0M1C → -> (3,2,0)  MMMCC ~~B C
│   └── 0M1C ← -> (3,3,1)  MMMCCC B~~ -   [REPEATED]
├── 0M2C → -> (3,1,0)  MMMC ~~B CC   [*]
│   ├── 0M1C ← -> (3,2,1)  MMMCC B~~ C   [*]
│   │   ├── 1M0C → -> (2,2,0)  MMCC ~~B MC   [REPEATED]
│   │   ├── 2M0C → -> (1,2,0)  MCC ~~B MMC   [INVALID: majtas C > M]
│   │   ├── 0M1C → -> (3,1,0)  MMMC ~~B CC   [REPEATED]
│   │   ├── 0M2C → -> (3,0,0)  MMM ~~B CCC   [*]
│   │   │   ├── 0M1C ← -> (3,1,1)  MMMC B~~ CC   [*]
│   │   │   │   ├── 1M0C → -> (2,1,0)  MMC ~~B MCC   [INVALID: djathtas C > M]
│   │   │   │   ├── 2M0C → -> (1,1,0)  MC ~~B MMCC   [*]
│   │   │   │   │   ├── 1M0C ← -> (2,1,1)  MMC B~~ MCC   [INVALID: djathtas C > M]
│   │   │   │   │   ├── 2M0C ← -> (3,1,1)  MMMC B~~ CC   [REPEATED]
│   │   │   │   │   ├── 0M1C ← -> (1,2,1)  MCC B~~ MMC   [INVALID: majtas C > M]
│   │   │   │   │   ├── 0M2C ← -> (1,3,1)  MCCC B~~ MM   [INVALID: majtas C > M]
│   │   │   │   │   └── 1M1C ← -> (2,2,1)  MMCC B~~ MC   [*]
│   │   │   │   │       ├── 1M0C → -> (1,2,0)  MCC ~~B MMC   [INVALID: majtas C > M]
│   │   │   │   │       ├── 2M0C → -> (0,2,0)  CC ~~B MMMC   [*]
│   │   │   │   │       │   ├── 1M0C ← -> (1,2,1)  MCC B~~ MMC   [INVALID: majtas C > M]
│   │   │   │   │       │   ├── 2M0C ← -> (2,2,1)  MMCC B~~ MC   [REPEATED]
│   │   │   │   │       │   ├── 0M1C ← -> (0,3,1)  CCC B~~ MMM   [*]
│   │   │   │   │       │   │   ├── 0M1C → -> (0,2,0)  CC ~~B MMMC   [REPEATED]
│   │   │   │   │       │   │   └── 0M2C → -> (0,1,0)  C ~~B MMMCC   [*]
│   │   │   │   │       │   │       ├── 1M0C ← -> (1,1,1)  MC B~~ MMCC   [*]
│   │   │   │   │       │   │       │   ├── 1M0C → -> (0,1,0)  C ~~B MMMCC   [REPEATED]
│   │   │   │   │       │   │       │   ├── 0M1C → -> (1,0,0)  M ~~B MMCCC   [INVALID: djathtas C > M]
│   │   │   │   │       │   │       │   └── 1M1C → -> (0,0,0)  - ~~B MMMCCC   [*, GOAL]
│   │   │   │   │       │   │       ├── 2M0C ← -> (2,1,1)  MMC B~~ MCC   [INVALID: djathtas C > M]
│   │   │   │   │       │   │       ├── 0M1C ← -> (0,2,1)  CC B~~ MMMC
│   │   │   │   │       │   │       │   ├── 0M1C → -> (0,1,0)  C ~~B MMMCC   [REPEATED]
│   │   │   │   │       │   │       │   └── 0M2C → -> (0,0,0)  - ~~B MMMCCC   [REPEATED]
│   │   │   │   │       │   │       ├── 0M2C ← -> (0,3,1)  CCC B~~ MMM   [REPEATED]
│   │   │   │   │       │   │       └── 1M1C ← -> (1,2,1)  MCC B~~ MMC   [INVALID: majtas C > M]
│   │   │   │   │       │   └── 1M1C ← -> (1,3,1)  MCCC B~~ MM   [INVALID: majtas C > M]
│   │   │   │   │       ├── 0M1C → -> (2,1,0)  MMC ~~B MCC   [INVALID: djathtas C > M]
│   │   │   │   │       ├── 0M2C → -> (2,0,0)  MM ~~B MCCC   [INVALID: djathtas C > M]
│   │   │   │   │       └── 1M1C → -> (1,1,0)  MC ~~B MMCC   [REPEATED]
│   │   │   │   ├── 0M1C → -> (3,0,0)  MMM ~~B CCC   [REPEATED]
│   │   │   │   └── 1M1C → -> (2,0,0)  MM ~~B MCCC   [INVALID: djathtas C > M]
│   │   │   └── 0M2C ← -> (3,2,1)  MMMCC B~~ C   [REPEATED]
│   │   └── 1M1C → -> (2,1,0)  MMC ~~B MCC   [INVALID: djathtas C > M]
│   └── 0M2C ← -> (3,3,1)  MMMCCC B~~ -   [REPEATED]
└── 1M1C → -> (2,2,0)  MMCC ~~B MC
    ├── 1M0C ← -> (3,2,1)  MMMCC B~~ C   [REPEATED]
    ├── 0M1C ← -> (2,3,1)  MMCCC B~~ M   [INVALID: majtas C > M]
    └── 1M1C ← -> (3,3,1)  MMMCCC B~~ -   [REPEATED]
```

**Pema:** 49 nyje, 14 të zgjeruara, 16 të përsëritura, 18 jo-valide. Ka vetëm 15 gjendje valide të arritshme, prandaj pema e plotë është e vogël.

**Zgjidhja (11 hapa, minimale):** 2C → , 1C ← , 2C → , 1C ← , 2M → , 1M1C ← , 2M → , 1C ← , 2C → , 1M ← , 1M1C →

```mermaid
graph TD
    n0["(3,3,1)<br/>MMMCCC B~~ -"]
    class n0 path
    n0 -->|"1M1C →"| n5
    n0 -->|"0M2C →"| n4
    n0 -->|"0M1C →"| n3
    n0 -->|"2M0C →"| n2
    n0 -->|"1M0C →"| n1
    n1["(2,3,0)<br/>MMCCC ~~B M<br/>✗ majtas C > M"]
    class n1 invalid
    n2["(1,3,0)<br/>MCCC ~~B MM<br/>✗ majtas C > M"]
    class n2 invalid
    n3["(3,2,0)<br/>MMMCC ~~B C"]
    n3 -->|"0M1C ←"| n6
    n6["(3,3,1)<br/>MMMCCC B~~ -<br/>↺ e perseritur"]
    class n6 repeated
    n4["(3,1,0)<br/>MMMC ~~B CC"]
    class n4 path
    n4 -->|"0M2C ←"| n8
    n4 -->|"0M1C ←"| n7
    n7["(3,2,1)<br/>MMMCC B~~ C"]
    class n7 path
    n7 -->|"1M1C →"| n16
    n7 -->|"0M2C →"| n15
    n7 -->|"0M1C →"| n14
    n7 -->|"2M0C →"| n13
    n7 -->|"1M0C →"| n12
    n12["(2,2,0)<br/>MMCC ~~B MC<br/>↺ e perseritur"]
    class n12 repeated
    n13["(1,2,0)<br/>MCC ~~B MMC<br/>✗ majtas C > M"]
    class n13 invalid
    n14["(3,1,0)<br/>MMMC ~~B CC<br/>↺ e perseritur"]
    class n14 repeated
    n15["(3,0,0)<br/>MMM ~~B CCC"]
    class n15 path
    n15 -->|"0M2C ←"| n18
    n15 -->|"0M1C ←"| n17
    n17["(3,1,1)<br/>MMMC B~~ CC"]
    class n17 path
    n17 -->|"1M1C →"| n22
    n17 -->|"0M1C →"| n21
    n17 -->|"2M0C →"| n20
    n17 -->|"1M0C →"| n19
    n19["(2,1,0)<br/>MMC ~~B MCC<br/>✗ djathtas C > M"]
    class n19 invalid
    n20["(1,1,0)<br/>MC ~~B MMCC"]
    class n20 path
    n20 -->|"1M1C ←"| n27
    n20 -->|"0M2C ←"| n26
    n20 -->|"0M1C ←"| n25
    n20 -->|"2M0C ←"| n24
    n20 -->|"1M0C ←"| n23
    n23["(2,1,1)<br/>MMC B~~ MCC<br/>✗ djathtas C > M"]
    class n23 invalid
    n24["(3,1,1)<br/>MMMC B~~ CC<br/>↺ e perseritur"]
    class n24 repeated
    n25["(1,2,1)<br/>MCC B~~ MMC<br/>✗ majtas C > M"]
    class n25 invalid
    n26["(1,3,1)<br/>MCCC B~~ MM<br/>✗ majtas C > M"]
    class n26 invalid
    n27["(2,2,1)<br/>MMCC B~~ MC"]
    class n27 path
    n27 -->|"1M1C →"| n32
    n27 -->|"0M2C →"| n31
    n27 -->|"0M1C →"| n30
    n27 -->|"2M0C →"| n29
    n27 -->|"1M0C →"| n28
    n28["(1,2,0)<br/>MCC ~~B MMC<br/>✗ majtas C > M"]
    class n28 invalid
    n29["(0,2,0)<br/>CC ~~B MMMC"]
    class n29 path
    n29 -->|"1M1C ←"| n36
    n29 -->|"0M1C ←"| n35
    n29 -->|"2M0C ←"| n34
    n29 -->|"1M0C ←"| n33
    n33["(1,2,1)<br/>MCC B~~ MMC<br/>✗ majtas C > M"]
    class n33 invalid
    n34["(2,2,1)<br/>MMCC B~~ MC<br/>↺ e perseritur"]
    class n34 repeated
    n35["(0,3,1)<br/>CCC B~~ MMM"]
    class n35 path
    n35 -->|"0M2C →"| n38
    n35 -->|"0M1C →"| n37
    n37["(0,2,0)<br/>CC ~~B MMMC<br/>↺ e perseritur"]
    class n37 repeated
    n38["(0,1,0)<br/>C ~~B MMMCC"]
    class n38 path
    n38 -->|"1M1C ←"| n43
    n38 -->|"0M2C ←"| n42
    n38 -->|"0M1C ←"| n41
    n38 -->|"2M0C ←"| n40
    n38 -->|"1M0C ←"| n39
    n39["(1,1,1)<br/>MC B~~ MMCC"]
    class n39 path
    n39 -->|"1M1C →"| n46
    n39 -->|"0M1C →"| n45
    n39 -->|"1M0C →"| n44
    n44["(0,1,0)<br/>C ~~B MMMCC<br/>↺ e perseritur"]
    class n44 repeated
    n45["(1,0,0)<br/>M ~~B MMCCC<br/>✗ djathtas C > M"]
    class n45 invalid
    n46["(0,0,0)<br/>- ~~B MMMCCC<br/>✓ QELLIMI"]
    class n46 goal
    n40["(2,1,1)<br/>MMC B~~ MCC<br/>✗ djathtas C > M"]
    class n40 invalid
    n41["(0,2,1)<br/>CC B~~ MMMC"]
    n41 -->|"0M2C →"| n48
    n41 -->|"0M1C →"| n47
    n47["(0,1,0)<br/>C ~~B MMMCC<br/>↺ e perseritur"]
    class n47 repeated
    n48["(0,0,0)<br/>- ~~B MMMCCC<br/>↺ e perseritur"]
    class n48 repeated
    n42["(0,3,1)<br/>CCC B~~ MMM<br/>↺ e perseritur"]
    class n42 repeated
    n43["(1,2,1)<br/>MCC B~~ MMC<br/>✗ majtas C > M"]
    class n43 invalid
    n36["(1,3,1)<br/>MCCC B~~ MM<br/>✗ majtas C > M"]
    class n36 invalid
    n30["(2,1,0)<br/>MMC ~~B MCC<br/>✗ djathtas C > M"]
    class n30 invalid
    n31["(2,0,0)<br/>MM ~~B MCCC<br/>✗ djathtas C > M"]
    class n31 invalid
    n32["(1,1,0)<br/>MC ~~B MMCC<br/>↺ e perseritur"]
    class n32 repeated
    n21["(3,0,0)<br/>MMM ~~B CCC<br/>↺ e perseritur"]
    class n21 repeated
    n22["(2,0,0)<br/>MM ~~B MCCC<br/>✗ djathtas C > M"]
    class n22 invalid
    n18["(3,2,1)<br/>MMMCC B~~ C<br/>↺ e perseritur"]
    class n18 repeated
    n16["(2,1,0)<br/>MMC ~~B MCC<br/>✗ djathtas C > M"]
    class n16 invalid
    n8["(3,3,1)<br/>MMMCCC B~~ -<br/>↺ e perseritur"]
    class n8 repeated
    n5["(2,2,0)<br/>MMCC ~~B MC"]
    n5 -->|"1M1C ←"| n11
    n5 -->|"0M1C ←"| n10
    n5 -->|"1M0C ←"| n9
    n9["(3,2,1)<br/>MMMCC B~~ C<br/>↺ e perseritur"]
    class n9 repeated
    n10["(2,3,1)<br/>MMCCC B~~ M<br/>✗ majtas C > M"]
    class n10 invalid
    n11["(3,3,1)<br/>MMMCCC B~~ -<br/>↺ e perseritur"]
    class n11 repeated
    classDef goal fill:#2e7d32,color:#fff,stroke:#1b5e20
    classDef path fill:#1565c0,color:#fff,stroke:#0d47a1
    classDef repeated fill:#9e9e9e,color:#fff,stroke:#616161
    classDef invalid fill:#c62828,color:#fff,stroke:#8e0000
    classDef limit fill:#f9a825,color:#000,stroke:#f57f17
```

---

## 3. Rotating Workforce Scheduling (RWS)

### Modelimi

`n` punëtorë punojnë sipas të njëjtit **orar ciklik** prej `n` javësh: punëtori `i` në javën `j` ndjek rreshtin `(i + j) mod n` të orarit. Ndërrimet janë: **D** (ditë), **A** (pasdite), **N** (natë) dhe **-** (pushim).

Instanca e përdorur (në [rotating_workforce.py](rotating_workforce.py)):

| Parametri | Vlera |
|---|---|
| Punëtorë / javë në cikël | 4, pra 28 ditë |
| Kërkesa për çdo ditë të javës | 1 D, 1 A, 1 N (dhe 1 pushim) |
| Blloqet e punës (ditë pune radhazi) | 3–6 |
| Blloqet e pushimit | 1–3 |
| Blloqet e të njëjtit ndërrim | 2–5 |
| Sekuenca të ndaluara | N→D, N→A, A→D (pa pushim të mjaftueshëm) |

- **Gjendja:** tuple me ndërrimet e caktuara deri tani (dita 0, 1, 2, …).
- **Gjendja fillestare:** orari bosh `()`.
- **Veprimi:** cakto ndërrimin e ditës së radhës, me domain `{D, A, N, -}`. Degëzimi është 4.
- **Qëllimi:** të 28 ditët janë caktuar dhe të gjitha kufizimet plotësohen, përfshirë kalimin ciklik nga dita 28 te dita 1.
- **INVALID:** sekuencë e ndaluar, më shumë punëtorë se sa kërkohen në një ndërrim, ose bllok shumë i gjatë ose shumë i shkurtër.

### Pema (nivelet e para)

Pema e plotë ka thellësi 28, një nivel për çdo ditë, dhe deri në `4^28 ≈ 7.2·10^16` gjethe. Prandaj vizatohen vetëm nivelet e para:

```
(bosh)   [*]
├── D -> D   [*]
│   ├── D -> DD   [*, LIMIT]
│   ├── A -> DA   [LIMIT]
│   ├── N -> DN   [LIMIT]
│   └── - -> D-   [LIMIT]
├── A -> A
│   ├── D -> AD   [INVALID: A→D e ndaluar]
│   ├── A -> AA   [LIMIT]
│   ├── N -> AN   [LIMIT]
│   └── - -> A-   [LIMIT]
├── N -> N
│   ├── D -> ND   [INVALID: N→D e ndaluar]
│   ├── A -> NA   [INVALID: N→A e ndaluar]
│   ├── N -> NN   [LIMIT]
│   └── - -> N-   [LIMIT]
└── - -> -
    ├── D -> -D   [LIMIT]
    ├── A -> -A   [LIMIT]
    ├── N -> -N   [LIMIT]
    └── - -> --   [LIMIT]
```

Me `python main.py --problem rws --rws-depth 3` (ose më shumë) shfaqen edhe nivele të tjera. Atje dalin edhe arsye të tjera për prerjen e degëve, p.sh. `DAN [INVALID: bllok 'A' < 2]`: ndërrimi A zgjat vetëm një ditë, kurse minimumi është 2.

```mermaid
graph TD
    n0["(bosh)"]
    class n0 path
    n0 -->|"-"| n4
    n0 -->|"N"| n3
    n0 -->|"A"| n2
    n0 -->|"D"| n1
    n1["D"]
    class n1 path
    n1 -->|"-"| n8
    n1 -->|"N"| n7
    n1 -->|"A"| n6
    n1 -->|"D"| n5
    n5["DD"]
    class n5 path
    n6["DA"]
    class n6 limit
    n7["DN"]
    class n7 limit
    n8["D-"]
    class n8 limit
    n2["A"]
    n2 -->|"-"| n12
    n2 -->|"N"| n11
    n2 -->|"A"| n10
    n2 -->|"D"| n9
    n9["AD<br/>✗ A→D e ndaluar"]
    class n9 invalid
    n10["AA"]
    class n10 limit
    n11["AN"]
    class n11 limit
    n12["A-"]
    class n12 limit
    n3["N"]
    n3 -->|"-"| n16
    n3 -->|"N"| n15
    n3 -->|"A"| n14
    n3 -->|"D"| n13
    n13["ND<br/>✗ N→D e ndaluar"]
    class n13 invalid
    n14["NA<br/>✗ N→A e ndaluar"]
    class n14 invalid
    n15["NN"]
    class n15 limit
    n16["N-"]
    class n16 limit
    n4["-"]
    n4 -->|"-"| n20
    n4 -->|"N"| n19
    n4 -->|"A"| n18
    n4 -->|"D"| n17
    n17["-D"]
    class n17 limit
    n18["-A"]
    class n18 limit
    n19["-N"]
    class n19 limit
    n20["--"]
    class n20 limit
    classDef goal fill:#2e7d32,color:#fff,stroke:#1b5e20
    classDef path fill:#1565c0,color:#fff,stroke:#0d47a1
    classDef repeated fill:#9e9e9e,color:#fff,stroke:#616161
    classDef invalid fill:#c62828,color:#fff,stroke:#8e0000
    classDef limit fill:#f9a825,color:#000,stroke:#f57f17
```

### Zgjidhja

Zgjidhja u gjet duke ndjekur të njëjtën pemë me **DFS dhe backtracking**: degët `INVALID` priten menjëherë. U zgjeruan vetëm 281 nyje.

```
Java  Hë Ma Më En Pr Sh Di
  1    D  D  D  D  D  -  A
  2    A  A  N  N  -  D  D
  3    N  N  -  -  N  N  N
  4    -  -  A  A  A  A  -
```

Rruga në pemë: `D D D D D - A | A A N N - D D | N N - - N N N | - - A A A A -`. Çdo kolonë (ditë e javës) ka saktësisht një D, një A, një N dhe një pushim.

---

## Ekzekutimi

Kërkohet Python 3.8+ dhe nuk ka nevojë për librari të jashtme.

```bash
cd task4

# Te tre pemet (shtypen dhe ruhen ne output/)
python main.py

# Vetem nje problem
python main.py --problem puzzle --puzzle-depth 4
python main.py --problem mc
python main.py --problem rws --rws-depth 3
```

| Skedari | Përmbajtja |
|---|---|
| [search_tree.py](search_tree.py) | Ndërtimi i pemës, shënimi i rrugës, shtypja si tekst dhe si Mermaid |
| [eight_puzzle.py](eight_puzzle.py) | Modeli i 8-Puzzle |
| [missionaries_cannibals.py](missionaries_cannibals.py) | Modeli i Missionaries and Cannibals |
| [rotating_workforce.py](rotating_workforce.py) | Modeli i RWS dhe zgjidhja me DFS |
| [main.py](main.py) | Ndërton dhe ruan të tri pemët |
| [output/](output/) | Pemët e gjeneruara (`.txt`, `.mmd`) |
