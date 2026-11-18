"""Miary jakości używane w literaturze PFSP.

RPD  = 100 · (wynik − najlepszy_znany) / najlepszy_znany
ARPD = średnia RPD po uruchomieniach (np. Bosman 2016: w nawiasach)
MRPD = mediana RPD (Bosman 2016: główna miara, bo wyniki nie są normalne)
Guijt 2022: mediana luki do optimum / ograniczenia w % – to to samo co MRPD.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def rpd(value: float, best_known: float) -> float:
    return 100.0 * (value - best_known) / best_known


def arpd(values: Sequence[float], best_known: float) -> float:
    return float(np.mean([rpd(v, best_known) for v in values]))


def mrpd(values: Sequence[float], best_known: float) -> float:
    return float(np.median([rpd(v, best_known) for v in values]))
