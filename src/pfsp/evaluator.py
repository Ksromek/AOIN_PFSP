"""Evaluator: jedyne miejsce, gdzie liczymy funkcję celu i FFE.

Każdy algorytm dostaje Evaluator i ocenia rozwiązania WYŁĄCZNIE przez niego.
Dzięki temu budżet (liczba wywołań funkcji celu, FFE) jest liczony tak samo
dla wszystkich metod – to warunek uczciwego porównania z literaturą
(np. budżety FFE z Bosmana i in. 2016 / Guijta i in. 2022, patrz budgets.py).

Po wyczerpaniu budżetu kolejne wywołanie rzuca ``BudgetExhausted``.
Runner łapie ten wyjątek i bierze najlepsze rozwiązanie z Evaluatora,
więc algorytmy nie muszą same pilnować budżetu.
"""
from __future__ import annotations

import numpy as np

from .instance import Instance
from .objective import insertion_makespans, makespan, objective_function, total_flow_time
from .random_keys import decode


class BudgetExhausted(Exception):
    """Wyczerpano budżet FFE."""


class Evaluator:
    def __init__(self, instance: Instance, objective: str = "makespan", max_ffe: int | None = None):
        self.instance = instance
        self.p = np.ascontiguousarray(instance.p, dtype=np.int64)
        self.objective = objective
        self._f = objective_function(objective)
        self.max_ffe = max_ffe
        self.ffe = 0
        self.best_value: int | None = None
        self.best_perm: np.ndarray | None = None
        # historia poprawy najlepszego: lista (ffe, wartość) – do krzywych zbieżności
        self.history: list[tuple[int, int]] = []

    # ------------------------------------------------------------------ budżet
    @property
    def remaining(self) -> float:
        return float("inf") if self.max_ffe is None else self.max_ffe - self.ffe

    def _charge(self, k: int = 1) -> None:
        if self.max_ffe is not None and self.ffe + k > self.max_ffe:
            raise BudgetExhausted
        self.ffe += k

    def _update_best(self, value: int, perm: np.ndarray) -> None:
        if self.best_value is None or value < self.best_value:
            self.best_value = int(value)
            self.best_perm = perm.copy()
            self.history.append((self.ffe, int(value)))

    # ------------------------------------------------------------------ ocena
    def evaluate(self, perm: np.ndarray) -> int:
        """Ocena permutacji. Koszt: 1 FFE."""
        self._charge(1)
        perm = np.asarray(perm, dtype=np.int64)
        value = int(self._f(perm, self.p))
        self._update_best(value, perm)
        return value

    def evaluate_keys(self, keys: np.ndarray) -> int:
        """Ocena wektora random keys (dekodowanie + ocena). Koszt: 1 FFE."""
        return self.evaluate(decode(keys))

    def insertion_values(self, seq: np.ndarray, job: int) -> np.ndarray:
        """Wartości celu dla wstawienia ``job`` na każdą pozycję ``seq``.

        KONWENCJA LICZENIA: k+1 pozycji = k+1 FFE (tak, jakby każdą pozycję
        oceniać osobno), mimo że dla makespanu liczymy to szybko (Taillard).
        Jeśli zmienicie konwencję, zmieńcie ją dla WSZYSTKICH algorytmów
        i opiszcie w raporcie.
        """
        seq = np.asarray(seq, dtype=np.int64)
        k = seq.shape[0]
        self._charge(k + 1)
        if self.objective == "makespan":
            vals = insertion_makespans(seq, np.int64(job), self.p)
        else:
            vals = np.empty(k + 1, dtype=np.int64)
            for pos in range(k + 1):
                vals[pos] = total_flow_time(np.insert(seq, pos, job), self.p)
        # najlepsze z tych wstawień traktujemy jak ocenione rozwiązanie
        # (tylko gdy seq + job to pełna permutacja)
        if k + 1 == self.instance.n_jobs:
            pos = int(np.argmin(vals))
            self._update_best(int(vals[pos]), np.insert(seq, pos, job))
        return vals

    def summary(self) -> dict:
        return {
            "best_value": self.best_value,
            "ffe_used": self.ffe,
            "max_ffe": self.max_ffe,
        }


__all__ = ["Evaluator", "BudgetExhausted", "makespan", "total_flow_time"]
