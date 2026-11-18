"""NEH (Nawaz, Enscore, Ham 1983) – klasyczna heurystyka konstrukcyjna dla PFSP.

1. Sortuj zadania malejąco po sumie czasów na wszystkich maszynach.
2. Buduj ciąg: każde kolejne zadanie wstaw w miejsce dające najmniejszy cel.

Dla makespanu wstawianie liczone jest przyspieszeniem Taillarda (O(n²m) całość).
Remisy: wybieramy pierwszą najlepszą pozycję (tak w wersji oryginalnej);
literatura zna lepsze reguły remisów – możecie je dodać.
"""
from __future__ import annotations

import numpy as np

from ..evaluator import Evaluator


def neh_order(p: np.ndarray) -> np.ndarray:
    totals = p.sum(axis=0)
    return np.argsort(-totals, kind="stable").astype(np.int64)


def run(evaluator: Evaluator, rng: np.random.Generator | None = None) -> np.ndarray:
    order = neh_order(evaluator.p)
    seq = order[:1].copy()
    for job in order[1:]:
        vals = evaluator.insertion_values(seq, int(job))
        pos = int(np.argmin(vals))
        seq = np.insert(seq, pos, job)
    return seq
