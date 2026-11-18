# Dane

## Instancje Taillarda (`data/taillard/`)

Pobierzcie pliki flow shopu ze strony Taillarda (pliki w stylu `tai20_5.txt`,
po 10 instancji w pliku) i wrzućcie je do `data/taillard/`. Parser
(`src/pfsp/instance.py`) obsługuje ten format i format jednoinstancyjny
(`n m seed UB LB`, potem m wierszy po n liczb).

Nazwy instancji po wczytaniu: `<nazwa_pliku>_<indeks>`, np. `tai20_5_0`
(indeksy od 0, tak jak w pracach Guijta i RK-EDA: „instancje nr 1 i 2”
to w ich numeracji te same co nasze `_0` i `_1` – sprawdźcie to!).

## Najlepsze znane wyniki (`best_known_makespan.csv`, `best_known_tft.csv`)

UB zapisane w plikach Taillarda są z 1993 r. i od tamtej pory wiele z nich
poprawiono. Do liczenia RPD wpiszcie AKTUALNE najlepsze znane wartości
(źródło podajcie w raporcie – np. strona Taillarda albo tabela z pracy,
z którą się porównujecie). Format: `instance,best_known`.
Jeśli instancji nie ma w CSV, runner bierze UB z pliku i zapisuje to
w kolumnie `ref_source`.

`example_3x2.txt` – mini-przykład z naszego PDF-a (optimum makespanu = 8).
