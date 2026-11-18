"""Random keys: kodowanie permutacji liczbami rzeczywistymi.

Infrastruktura (gotowa): decode, encode, reencode.
Wasz wkład (do napisania): insert_with_alpha, coherent_block_copy – na dole pliku.
"""
from __future__ import annotations

import numpy as np


def decode(keys: np.ndarray) -> np.ndarray:
    """Klucze -> permutacja: zadania posortowane rosnąco po kluczach.

    Sortowanie stabilne, więc przy równych kluczach wygrywa mniejszy numer
    zadania (deterministycznie).
    """
    return np.argsort(keys, kind="stable").astype(np.int64)


def encode(perm: np.ndarray) -> np.ndarray:
    """Permutacja -> klucze rozłożone równo: zadanie na pozycji i dostaje (i + 0.5) / n."""
    perm = np.asarray(perm)
    n = perm.shape[0]
    keys = np.empty(n, dtype=np.float64)
    keys[perm] = (np.arange(n) + 0.5) / n
    return keys


def reencode(keys: np.ndarray) -> np.ndarray:
    """Przenumerowanie kluczy (re-encoding): ta sama permutacja, równe odstępy 1/n.

    Robimy to raz na pokolenie: klucze się nie zagęszczają, nie wychodzą
    poza [0, 1], a zasięg α/n zawsze znaczy „około α pozycji”.
    """
    return encode(decode(keys))


def random_keys(n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.random(n)


# =====================================================================
#  WASZ WKŁAD – do napisania. Testy w tests/test_random_keys.py
#  (obecnie pomijane: usuńcie @pytest.mark.skip, gdy zaimplementujecie).
# =====================================================================

def insert_with_alpha(keys: np.ndarray, job: int, anchor: int, alpha: float) -> np.ndarray:
    """Mutacja: przesuń ``job`` za ``anchor`` o około ``alpha`` pozycji.

    k_nowy = k_anchor + alpha / n, przycięte do [0, 1].
    Zwraca NOWĄ tablicę (nie modyfikuje ``keys``).

    Przykład z PDF-a (n = 5, klucze po przenumerowaniu):
        keys = [0.5, 0.1, 0.9, 0.3, 0.7]  (Z1..Z5) -> permutacja 2 4 1 5 3
        job = Z2, anchor = Z4:
          alpha = 0.5 -> 4 2 1 5 3
          alpha = 1.5 -> 4 1 2 5 3
          alpha = 2.5 -> 4 1 5 2 3
          alpha = 4.0 -> 4 1 5 3 2  (klucz przycięty do 1.0)
    """
    raise NotImplementedError("TODO: wstawianie z zasięgiem alpha")


def coherent_block_copy(receiver: np.ndarray, donor: np.ndarray, block: np.ndarray,
                        width: float = 1e-6) -> np.ndarray:
    """Spójne kopiowanie bloku: klucze ``block`` od dawcy, „ściśnięte” wokół ich średniej.

    1. c = średnia kluczy dawcy dla zadań z ``block``,
    2. zadania z bloku dostają klucze z przedziału [c - width/2, c + width/2],
       w KOLEJNOŚCI, w jakiej stoją u dawcy,
    3. reszta kluczy zostaje od biorcy.
    Zwraca NOWĄ tablicę.

    Przykład z PDF-a: dawca 3 1 4 2 5, biorca 5 2 4 1 3, blok {3, 1}
    -> dziecko 5 2 3 1 4 (blok w całości, obok siebie).
    Uwaga: jeśli jakiś klucz biorcy wpada do ściśniętego przedziału, blok się
    rozerwie – zastanówcie się, czy to obsłużyć (np. przesunąć c).
    """
    raise NotImplementedError("TODO: spójne kopiowanie bloku")


def plain_block_copy(receiver: np.ndarray, donor: np.ndarray, block: np.ndarray) -> np.ndarray:
    """Zwykłe kopiowanie (jak w Permutation GOMEA): klucze ``block`` 1:1 od dawcy."""
    raise NotImplementedError("TODO: zwykłe kopiowanie bloku (kilka linii)")
