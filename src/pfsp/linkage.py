"""Linkage learning dla random keys – DO NAPISANIA.

Model zależności z Bosman, Luong, Thierens (GECCO 2016), dla pary zadań (i, j):

    waga(i, j) = (1 − H(p_ij)) · (1 − średnia_po_populacji((k_i − k_j)^2))

gdzie p_ij = odsetek osobników, w których klucz i < klucz j, a H to entropia
binarna. Sprawdźcie szczegóły (np. czy liczą na kluczach po przenumerowaniu)
w samej pracy.
"""
from __future__ import annotations

import numpy as np


def dsm_bosman(population_keys: np.ndarray) -> np.ndarray:
    """population_keys: (rozmiar_populacji, n). Zwraca symetryczną macierz n × n."""
    raise NotImplementedError("TODO: DSM wg Bosmana i in. (2016)")


def linkage_tree(dsm: np.ndarray) -> list[np.ndarray]:
    """Klastrowanie hierarchiczne DSM (jak LTGA/UPGMA).

    Zwraca listę bloków (tablice numerów zadań), od par po duże grupy –
    bez korzenia (całej permutacji), tak jak w LTGA.
    """
    raise NotImplementedError("TODO: linkage tree z DSM")


def random_blocks_like(blocks: list[np.ndarray], n: int, rng: np.random.Generator) -> list[np.ndarray]:
    """Kontrola: losowe bloki o TYCH SAMYCH rozmiarach co ``blocks``."""
    raise NotImplementedError("TODO: losowe bloki do eksperymentu kontrolnego")
