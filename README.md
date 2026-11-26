# Adaptacyjny zasięg wstawiania w random keys dla PFSP

Kod do projektu z kursu *Algorytmy optymalizacji inspirowane naturą* (Politechnika Wrocławska).
Badamy permutacyjny problem przepływowy (PFSP) z kryterium makespanu, rozwiązywany
algorytmem genetycznym na random keys. Porównujemy dwa sposoby przenoszenia bloków
zadań wyznaczonych przez linkage learning (kopiowanie zwykłe i spójne) oraz kilka
metod sterowania zasięgiem α mutacji przez wstawianie.

## Instalacja

Wymagany Python ≥ 3.10.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

Zależności: NumPy, Numba, pycma, joblib (pytest do testów).

## Dane

Instancje Taillarda [1] pochodzą ze strony autora
([Éric Taillard's page](https://mistic.iict-heig-vd.ch/taillard/problemes.dir/ordonnancement.dir/ordonnancement.html)): 12 plików
`data/taillard/tai<n>_<m>.txt`, po dziesięć instancji w pliku. Instancja
`tai20_5.txt` o indeksie 0 (ta001) ma w kodzie nazwę `tai20_5_0`. Skrypt
`scripts/generate_taillard.py` odtwarza te same macierze generatorem i ziarnami
z [1] (ziarna za OR-Library: https://www.brunel.ac.uk/~mastjjb/jeb/orlib/files/flowshop2.txt);
służy tylko do weryfikacji – wszystkie 120 macierzy jest zgodnych z plikami ze strony.

Wartością referencyjną do RPD dla makespanu jest najlepsze znane górne ograniczenie
z zestawienia Taillarda `data/best_lb_up.txt` (stan z 03.06.2026), przepisane do
`data/best_known_makespan.csv` (kolumny `instance,best_known,lower_bound,status`;
108 instancji ma udowodnione optimum, 12 jest otwartych). Dla TFT wartości wpisuje
się do `data/best_known_tft.csv`. Jeśli instancji nie ma w pliku CSV, używane jest
górne ograniczenie z nagłówka pliku instancji; źródło wartości trafia do kolumny
`ref_source` w wynikach.

## Uruchamianie eksperymentów

```bash
python experiments/run.py \
    --data data/taillard --pattern "tai20_5_[01]" \
    --algorithms neh ga_ox cmaes_rk rk_ga_gauss \
    --objective makespan --budget literature --seeds 20 --jobs -1 \
    --out results/makespan_20x5.csv --history
```

| Argument | Znaczenie |
| --- | --- |
| `--pattern` | filtr nazw instancji (składnia `fnmatch`) |
| `--algorithms` | nazwy z `src/pfsp/algorithms/__init__.py` |
| `--objective` | `makespan` albo `tft` |
| `--budget` | `literature`, `1000n2`, `none` albo liczba FFE |
| `--seeds` | liczba niezależnych uruchomień |
| `--params` | parametry algorytmów w JSON, np. `'{"pop_size": 100}'` |
| `--history` | zapis krzywych zbieżności do `results/history/` |

Każde uruchomienie daje jeden wiersz CSV: instancja, algorytm, parametry, seed,
najlepsza wartość, zużyte FFE, RPD, czas i najlepsza permutacja.

Czas pojedynczej ewaluacji na danej maszynie mierzy `benchmarks/bench_eval.py`.

## Protokół eksperymentalny

**Budżet.** Kryterium stopu jest liczba ewaluacji funkcji celu (FFE). Wariant
`literature` przyjmuje budżety na rozmiar instancji z [2] (pochodzące z GM-EDA),
które stosuje również [3]. Wariant `1000n2` odpowiada [4].

**Liczenie FFE.** Wszystkie algorytmy oceniają rozwiązania wyłącznie przez klasę
`Evaluator`, która zlicza FFE i przerywa działanie po wyczerpaniu budżetu.
Ocena wstawienia zadania na każdą z k+1 pozycji ciągu jest liczona jako k+1 FFE,
także wtedy, gdy makespan obliczany jest metodą przyspieszoną [5].

**Powtarzalność.** Seed każdego uruchomienia wyznaczany jest deterministycznie
z numeru powtórzenia, nazwy algorytmu i nazwy instancji.

**Miary.** RPD = 100 · (C − C\*) / C\*, gdzie C\* to wartość referencyjna.
Raportujemy ARPD (średnia) i MRPD (mediana) z uruchomień, zgodnie z [2].

## Metody

| Nazwa | Opis |
| --- | --- |
| `neh` | heurystyka NEH [6] |
| `random_search` | losowe permutacje |
| `ga_ox`, `ga_pmx` | GA na permutacjach z krzyżowaniem OX / PMX |
| `cmaes_rk` | CMA-ES (pycma [7]) na random keys, z restartami |
| `rk_ga_gauss` | GA na random keys z mutacją gaussowską |
| `plain_*`, `coherent_*` | GA na random keys z kopiowaniem bloków z DSM lub losowych (układ 2 × 2) |
| `rk_ga_alpha_*` | GA na random keys z mutacją przez wstawianie i sterowaniem α |

Model zależności i zwykłe kopiowanie bloków odpowiadają Permutation GOMEA [2].

## Struktura repozytorium

```
src/pfsp/
  instance.py        wczytywanie instancji
  objective.py       makespan, TFT, przyspieszone wstawianie (Numba)
  evaluator.py       ocena rozwiązań i licznik FFE
  random_keys.py     kodowanie, przenumerowanie, operatory na kluczach
  linkage.py         DSM i linkage tree
  alpha.py           sterowanie zasięgiem α
  budgets.py         budżety FFE
  metrics.py         RPD, ARPD, MRPD
  algorithms/        NEH, random search, GA, CMA-ES, GA na random keys
experiments/run.py   uruchamianie eksperymentów
benchmarks/          pomiar czasu ewaluacji
tests/               testy (pytest)
data/                instancje i wartości referencyjne
results/             wyniki
```

## Bibliografia

1. E. Taillard. Benchmarks for basic scheduling problems. *European Journal of Operational Research*, 64(2):278–285, 1993.
2. P. A. N. Bosman, N. H. Luong, D. Thierens. Expanding from discrete Cartesian to permutation gene-pool optimal mixing evolutionary algorithms. *GECCO 2016*. doi:10.1145/2908812.2908917
3. A. Guijt, N. H. Luong, P. A. N. Bosman, M. M. de Weerdt. On the impact of linkage learning, gene-pool optimal mixing, and non-redundant encoding on permutation optimization. *Swarm and Evolutionary Computation*, 70:101044, 2022. doi:10.1016/j.swevo.2022.101044
4. M. Ayodele, J. McCall, O. Regnier-Coudert. RK-EDA: A novel random key based estimation of distribution algorithm. *PPSN 2016*.
5. E. Taillard. Some efficient heuristic methods for the flow shop sequencing problem. *European Journal of Operational Research*, 47(1):65–74, 1990.
6. M. Nawaz, E. E. Enscore, I. Ham. A heuristic algorithm for the m-machine, n-job flow-shop sequencing problem. *Omega*, 11(1):91–95, 1983.
7. N. Hansen i in. pycma – implementacja CMA-ES w Pythonie. https://github.com/CMA-ES/pycma
