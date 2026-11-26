# Dane

## Instancje Taillarda (`data/taillard/`)

Pliki ze strony Taillarda (https://mistic.iict-heig-vd.ch/taillard/problemes.dir/ordonnancement.dir/ordonnancement.html), sekcja
„Flow shop sequencing”: 12 plików `tai<n>_<m>.txt`, po 10 instancji w pliku.
`python scripts/generate_taillard.py --out <katalog>` odtwarza je z ziaren
(OR-Library `flowshop2.txt`) – macierze są identyczne z plikami ze strony;
UB w nagłówkach plików ze strony są nowsze niż w pracy z 1993 r., ale też nie
są aktualnymi najlepszymi wynikami. Parser
(`src/pfsp/instance.py`) obsługuje ten format i format jednoinstancyjny
(`n m seed UB LB`, potem m wierszy po n liczb).

Nazwy instancji po wczytaniu: `<nazwa_pliku>_<indeks>`, np. `tai20_5_0`
(indeksy od 0, tak jak w pracach Guijta i RK-EDA: „instancje nr 1 i 2”
to w ich numeracji te same co nasze `_0` i `_1` – sprawdźcie to!).

## Najlepsze znane wyniki (`best_known_makespan.csv`, `best_known_tft.csv`)

`best_lb_up.txt` – zestawienie najlepszych znanych LB/UB ze strony Taillarda
(link „Summary”, stan z 03.06.2026, tylko harmonogramy permutacyjne).
`best_known_makespan.csv` jest z niego wygenerowane: `best_known` = najlepsze
znane UB, `lower_bound` = LB, `status` = `optimal` (LB = UB) albo `open`.
Przy porównaniu z konkretną pracą sprawdźcie, względem jakich wartości ona
liczyła RPD – starsze prace używają starszych UB.
`best_known_tft.csv` – do uzupełnienia, jeśli będziemy liczyć TFT.
Jeśli instancji nie ma w CSV, runner bierze UB z pliku i zapisuje to
w kolumnie `ref_source`.

`example_3x2.txt` – mini-przykład z naszego PDF-a (optimum makespanu = 8).
