import numpy as np
import pytest

from pfsp.random_keys import (coherent_block_copy, decode, encode, insert_with_alpha,
                              plain_block_copy, reencode)


def to_jobs(perm):
    """Permutacja 0-indeksowana -> numery zadań jak w PDF-ie (od 1)."""
    return [int(j) + 1 for j in perm]


def test_decode_pdf_example():
    assert to_jobs(decode(np.array([0.70, 0.20, 0.90]))) == [2, 1, 3]


def test_encode_decode_roundtrip_and_reencode():
    rng = np.random.default_rng(0)
    for n in [1, 5, 50]:
        perm = rng.permutation(n)
        assert decode(encode(perm)).tolist() == perm.tolist()
        keys = rng.random(n) * 3 - 1          # celowo poza [0, 1]
        r = reencode(keys)
        assert decode(r).tolist() == decode(keys).tolist()
        assert np.allclose(np.sort(r), (np.arange(n) + 0.5) / n)


# ------------------------------------------------------------------
# Testy WASZEGO wkładu – usuńcie @pytest.mark.skip po implementacji.
# Oczekiwane wyniki = przykłady z PDF-a (rozdziały 6 i 7).
# ------------------------------------------------------------------

KEYS_PDF = np.array([0.5, 0.1, 0.9, 0.3, 0.7])  # Z1..Z5 -> 2 4 1 5 3


@pytest.mark.skip(reason="TODO: insert_with_alpha")
@pytest.mark.parametrize("alpha,expected", [
    (0.5, [4, 2, 1, 5, 3]),
    (1.5, [4, 1, 2, 5, 3]),
    (2.5, [4, 1, 5, 2, 3]),
    (4.0, [4, 1, 5, 3, 2]),
])
def test_insert_with_alpha_pdf(alpha, expected):
    assert to_jobs(decode(KEYS_PDF)) == [2, 4, 1, 5, 3]
    new = insert_with_alpha(KEYS_PDF, job=1, anchor=3, alpha=alpha)  # Z2 za Z4
    assert to_jobs(decode(new)) == expected
    assert np.all((new >= 0) & (new <= 1))
    assert KEYS_PDF.tolist() == [0.5, 0.1, 0.9, 0.3, 0.7]  # wejście nietknięte


DONOR = np.array([0.30, 0.65, 0.20, 0.45, 0.90])     # -> 3 1 4 2 5
RECEIVER = np.array([0.70, 0.22, 0.85, 0.40, 0.10])  # -> 5 2 4 1 3
BLOCK = np.array([2, 0])                              # zadania Z3 i Z1


@pytest.mark.skip(reason="TODO: plain_block_copy")
def test_plain_block_copy_pdf():
    child = plain_block_copy(RECEIVER, DONOR, BLOCK)
    assert to_jobs(decode(child)) == [5, 3, 2, 1, 4]   # blok rozerwany przez Z2


@pytest.mark.skip(reason="TODO: coherent_block_copy")
def test_coherent_block_copy_pdf():
    child = coherent_block_copy(RECEIVER, DONOR, BLOCK)
    assert to_jobs(decode(child)) == [5, 2, 3, 1, 4]   # blok w całości
