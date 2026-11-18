"""Instancje PFSP: struktura danych i wczytywanie plików Taillarda.

Obsługiwane są dwa spotykane formaty:

1. Oryginalny plik Taillarda (np. ``tai20_5.txt``) – 10 instancji w jednym pliku,
   każda poprzedzona nagłówkiem tekstowym::

       number of jobs, number of machines, initial seed, upper bound and lower bound :
                 20           5   873654221        1278        1232
       processing times :
        54 83 15 ...        <- wiersz = maszyna, kolumna = zadanie

2. Pojedyncza instancja bez tekstu (np. pliki z przykładów solverów)::

       20 5 873654221 1278 1232
       54 83 15 ...         <- m wierszy po n liczb

W obu formatach czasy są zapisane maszynami: ``p[maszyna, zadanie]``.
Tak też trzymamy je w pamięci (macierz m × n, int64).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class Instance:
    name: str
    p: np.ndarray                 # czasy obróbki, kształt (m, n), int64
    seed: int | None = None       # seed generatora Taillarda (z pliku)
    upper_bound: int | None = None  # UB zapisane w pliku (stare, z 1993 r.!)
    lower_bound: int | None = None
    meta: dict = field(default_factory=dict)

    @property
    def n_jobs(self) -> int:
        return int(self.p.shape[1])

    @property
    def n_machines(self) -> int:
        return int(self.p.shape[0])

    @property
    def size(self) -> str:
        """Rozmiar w konwencji literatury, np. '20x5'."""
        return f"{self.n_jobs}x{self.n_machines}"

    def __repr__(self) -> str:  # krótko, bez całej macierzy
        return f"Instance({self.name!r}, {self.size}, UB={self.upper_bound})"


_INT = re.compile(r"-?\d+")


def _from_ints(name: str, ints: list[int], with_header: bool = True) -> Instance:
    n, m = ints[0], ints[1]
    if with_header:
        seed, ub, lb = ints[2], ints[3], ints[4]
        data = ints[5:]
    else:
        seed = ub = lb = None
        data = ints[2:]
    if len(data) < n * m:
        raise ValueError(f"{name}: oczekiwano {n * m} czasów, jest {len(data)}")
    p = np.asarray(data[: n * m], dtype=np.int64).reshape(m, n)
    return Instance(name=name, p=p, seed=seed, upper_bound=ub, lower_bound=lb)


def parse_taillard_text(text: str, base_name: str = "instance") -> list[Instance]:
    """Parsuje tekst w jednym z dwóch formatów (patrz docstring modułu)."""
    if "processing times" in text.lower():
        blocks = re.split(r"number of jobs[^\n]*\n", text, flags=re.IGNORECASE)
        instances = []
        for block in blocks:
            if not block.strip():
                continue
            header, _, times = re.split(r"(processing times\s*:?)", block, maxsplit=1, flags=re.IGNORECASE)
            ints = [int(x) for x in _INT.findall(header)] + [int(x) for x in _INT.findall(times)]
            instances.append(_from_ints(f"{base_name}_{len(instances)}", ints, with_header=True))
        return instances
    ints = [int(x) for x in _INT.findall(text)]
    return [_from_ints(base_name, ints, with_header=True)]


def load_file(path: str | Path) -> list[Instance]:
    path = Path(path)
    return parse_taillard_text(path.read_text(), base_name=path.stem)


def load_dir(directory: str | Path, pattern: str = "*.txt") -> list[Instance]:
    """Wczytuje wszystkie pliki z katalogu; nazwy instancji: <plik>_<indeks>."""
    out: list[Instance] = []
    for f in sorted(Path(directory).glob(pattern)):
        out.extend(load_file(f))
    return out


def random_instance(n_jobs: int, n_machines: int, seed: int = 0, low: int = 1, high: int = 99) -> Instance:
    """Losowa instancja U[low, high] jak u Taillarda (ale NIE te same liczby!).

    Do testów i benchmarków czasu, nie do porównań z literaturą.
    """
    rng = np.random.default_rng(seed)
    p = rng.integers(low, high + 1, size=(n_machines, n_jobs), dtype=np.int64)
    return Instance(name=f"rand{n_jobs}x{n_machines}_s{seed}", p=p)
