# AOIN – PFSP + random keys

Projekt na „Algorytmy optymalizacji inspirowane naturą” (PWr): permutacyjny flow shop
(makespan, dodatkowo TFT do porównań), random keys, spójne kopiowanie bloków
i sterowanie zasięgiem α w mutacji przez wstawianie.

## Start

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest                                                 # 26 testów + 6 pominiętych (Wasze TODO)
python benchmarks/bench_eval.py                        # ile trwa ewaluacja na Waszej maszynie
```

Instancje Taillarda wrzućcie do `data/taillard/` – szczegóły w `data/README.md`.

## Co jest gotowe, a co jest do napisania

| Moduł | Status | Co robi |
| --- | --- | --- |
| `pfsp/instance.py` | gotowe | wczytywanie Taillarda (oba formaty), losowe instancje do testów |
| `pfsp/objective.py` | gotowe | makespan i TFT w Numbie, przyspieszenie Taillarda dla wstawiania |
| `pfsp/evaluator.py` | gotowe | **jedyne** miejsce liczenia celu: licznik FFE, budżet, najlepsze rozwiązanie, historia |
| `pfsp/budgets.py` | gotowe | budżety FFE z Bosmana 2016 / Guijta 2022, 1000·n² (RK-EDA 2016) |
| `pfsp/metrics.py` | gotowe | RPD, ARPD, MRPD |
| `pfsp/random_keys.py` | częściowo | gotowe: decode, encode, reencode. **TODO:** `insert_with_alpha`, `plain_block_copy`, `coherent_block_copy` |
| `pfsp/linkage.py` | **TODO** | DSM wg Bosmana, linkage tree, losowe bloki (kontrola) |
| `pfsp/alpha.py` | częściowo | gotowe: stałe α. **TODO:** α malejące, reguła 1/5 i 1/e (opcjonalnie samoadaptacja) |
| `algorithms/neh.py` | gotowe | NEH (z przyspieszeniem Taillarda) |
| `algorithms/random_search.py` | gotowe | baseline |
| `algorithms/ga_permutation.py` | gotowe | GA z OX / PMX, mutacja insertion – baseline |
| `algorithms/cmaes_rk.py` | gotowe | CMA-ES z pycma na random keys, z restartami – baseline |
| `algorithms/rk_ga.py` | szkielet | GA na random keys; działa z krzyżowaniem jednostajnym i szumem gaussowskim, Wasze operatory podpina się parametrami |
| `experiments/run.py` | gotowe | algorytmy × instancje × seedy → CSV, równolegle (joblib) |

Testy Waszych funkcji już są w `tests/test_random_keys.py` (przykłady liczbowe z PDF-a),
tylko pominięte – usuńcie `@pytest.mark.skip`, gdy zaimplementujecie funkcję.

## Zasady, których pilnuje kod

* **Algorytm ocenia rozwiązania tylko przez `Evaluator`** – inaczej FFE się nie zgodzą
  i porównanie z literaturą jest nieuczciwe.
* **Wstawienie zadania na k+1 pozycji = k+1 FFE**, nawet jeśli liczymy je szybko
  (Taillard). Jeśli zmienicie tę konwencję – dla wszystkich algorytmów i opiszcie w raporcie.
* **Po wyczerpaniu budżetu** Evaluator rzuca `BudgetExhausted`, runner to łapie –
  algorytmy mogą mieć pętlę `while True`.
* **Seedy są deterministyczne** (seed × algorytm × instancja), więc każde uruchomienie
  da się powtórzyć.
* Gotowe biblioteki – tylko w baseline'ach (ustalenie z prowadzącym 18.11).
  Spójne kopiowanie i sterowanie α piszemy sami.

## Uruchamianie eksperymentów

```bash
# szybki test na mini-przykładzie z PDF-a
python experiments/run.py --data data --pattern "example*" \
    --algorithms neh random_search ga_ox --budget 500 --seeds 3 --out results/smoke.csv

# makespan, warunki jak Guijt i in. 2022: instancje nr 1 i 2 z 20x5, 20 seedów, wszystkie rdzenie
python experiments/run.py --data data/taillard --pattern "tai20_5_[01]" \
    --algorithms ga_ox cmaes_rk rk_ga_gauss --budget literature --seeds 20 --jobs -1 \
    --out results/guijt_20x5.csv --history

# TFT, warunki jak Bosman i in. 2016
python experiments/run.py --data data/taillard --algorithms rk_ga_gauss \
    --objective tft --budget literature --seeds 20 --jobs -1 --out results/bosman_tft.csv
```

Kolumny CSV: instancja, rozmiar, algorytm, parametry (JSON), seed, cel, najlepszy wynik,
zużyte FFE, budżet, punkt odniesienia i jego źródło, RPD, czas, status, najlepsza permutacja.
`--history` zapisuje krzywe zbieżności do `results/history/`.

Parametry algorytmów nadpisuje się przez `--params '{"pop_size": 100}'`.

## Czas obliczeń – co zmierzyliśmy

Na maszynie testowej (2 rdzenie, nie Wasza) jedna ewaluacja przez Evaluator to ok.
2,4 µs dla 20×5 i ok. 17,6 µs dla 500×20, czyli przy budżecie z literatury ok.
7 min (20×5) do ok. 76 min (500×20) na **jedno** uruchomienie, bez narzutu algorytmu.
Odpalcie `benchmarks/bench_eval.py` u siebie – i9 będzie szybszy.

Przy małych instancjach większość czasu to narzut Pythona (sam makespan w Numbie
to ok. 0,4 µs dla 20×5). Jeśli będzie za wolno: oceniajcie całą populację jedną
funkcją w Numbie (`@njit` na pętli po osobnikach) – to największy możliwy zysk.

## Struktura

```
src/pfsp/            instancje, cel, evaluator, random keys, linkage, α, metryki, budżety
src/pfsp/algorithms/ NEH, random search, GA OX/PMX, CMA-ES, GA na random keys
experiments/run.py   runner eksperymentów
benchmarks/          mikrobenchmark ewaluacji
tests/               pytest
data/                instancje (nie w repo) i najlepsze znane wyniki
results/             wyniki (nie w repo)
```
