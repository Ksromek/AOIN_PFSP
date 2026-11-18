"""Funkcje celu PFSP w Numbie.

Konwencje:
* ``p`` – czasy obróbki, macierz (m, n), int64, ``p[maszyna, zadanie]``,
* ``perm`` – permutacja zadań (int64), ``perm[i]`` = zadanie na pozycji i.

Uwaga: te funkcje NIE liczą FFE. Liczenie budżetu robi ``Evaluator``
(pfsp/evaluator.py) – algorytmy powinny wołać Evaluator, a nie te funkcje.
"""
from __future__ import annotations

import numpy as np
from numba import njit


@njit(cache=True)
def makespan(perm, p):
    """C_max: moment zakończenia ostatniego zadania na ostatniej maszynie. O(n·m)."""
    m = p.shape[0]
    c = np.zeros(m, dtype=np.int64)
    for idx in range(perm.shape[0]):
        j = perm[idx]
        c[0] += p[0, j]
        for k in range(1, m):
            if c[k - 1] > c[k]:
                c[k] = c[k - 1]
            c[k] += p[k, j]
    return c[m - 1]


@njit(cache=True)
def total_flow_time(perm, p):
    """TFT: suma momentów zakończenia wszystkich zadań na ostatniej maszynie. O(n·m)."""
    m = p.shape[0]
    c = np.zeros(m, dtype=np.int64)
    total = 0
    for idx in range(perm.shape[0]):
        j = perm[idx]
        c[0] += p[0, j]
        for k in range(1, m):
            if c[k - 1] > c[k]:
                c[k] = c[k - 1]
            c[k] += p[k, j]
        total += c[m - 1]
    return total


@njit(cache=True)
def insertion_makespans(seq, job, p):
    """Makespan po wstawieniu ``job`` na każdą pozycję 0..k ciągu ``seq`` (długość k).

    Przyspieszenie Taillarda (1990): zamiast k+1 osobnych obliczeń O(k·m)
    liczymy wszystkie pozycje naraz w O(k·m), przez macierze:
      e – „głowy” (najwcześniejsze zakończenia od początku),
      q – „ogony” (czas od startu zadania do końca, liczony od tyłu),
      f – zakończenia wstawianego zadania na każdej pozycji.
    Zwraca tablicę długości k+1: wynik[i] = C_max(seq z ``job`` na pozycji i).

    Tylko dla makespanu (dla TFT ta sztuczka nie działa wprost).
    """
    k = seq.shape[0]
    m = p.shape[0]
    e = np.zeros((k + 1, m), dtype=np.int64)  # e[i+1] = głowa po i-tym zadaniu, e[0] = 0
    for i in range(k):
        j = seq[i]
        for mm in range(m):
            prev_job = e[i, mm]
            prev_mach = e[i + 1, mm - 1] if mm > 0 else 0
            e[i + 1, mm] = (prev_job if prev_job > prev_mach else prev_mach) + p[mm, j]
    q = np.zeros((k + 1, m), dtype=np.int64)  # q[i] = ogon zadań od pozycji i do końca, q[k] = 0
    for i in range(k - 1, -1, -1):
        j = seq[i]
        for mm in range(m - 1, -1, -1):
            nxt_job = q[i + 1, mm]
            nxt_mach = q[i, mm + 1] if mm < m - 1 else 0
            q[i, mm] = (nxt_job if nxt_job > nxt_mach else nxt_mach) + p[mm, j]
    out = np.empty(k + 1, dtype=np.int64)
    f = np.zeros(m, dtype=np.int64)
    for pos in range(k + 1):
        best = 0
        for mm in range(m):
            a = f[mm - 1] if mm > 0 else 0
            b = e[pos, mm]
            f[mm] = (a if a > b else b) + p[mm, job]
            v = f[mm] + q[pos, mm]
            if v > best:
                best = v
        out[pos] = best
    return out


def objective_function(name: str):
    """Zwraca funkcję celu po nazwie: 'makespan' albo 'tft'."""
    if name == "makespan":
        return makespan
    if name in ("tft", "total_flow_time", "flowtime"):
        return total_flow_time
    raise ValueError(f"Nieznany cel: {name!r} (dostępne: 'makespan', 'tft')")
