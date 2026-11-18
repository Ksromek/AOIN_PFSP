"""Runner eksperymentów: algorytmy × instancje × seedy -> CSV.

Przykłady (z katalogu repo):

  # szybki test na przykładzie z PDF-a
  python experiments/run.py --data data --pattern "example*" --algorithms neh random_search \
      --budget 1000 --seeds 3

  # makespan, warunki jak Guijt i in. 2022, instancje nr 1 i 2 z 20x5, 20 seedów, 24 rdzenie
  python experiments/run.py --data data/taillard --pattern "tai20_5_[01]" \
      --algorithms ga_ox cmaes_rk --budget literature --seeds 20 --jobs 24 \
      --out results/guijt_20x5.csv

Każde uruchomienie: osobny Evaluator (licznik FFE od zera), seed wyznaczony
deterministycznie z (seed, algorytm, instancja). Wynik: jeden wiersz CSV.
Opcjonalnie --history zapisuje krzywą zbieżności (ffe, najlepsza wartość).
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pfsp import BudgetExhausted, Evaluator, load_dir  # noqa: E402
from pfsp.algorithms import REGISTRY  # noqa: E402
from pfsp.budgets import budget_for  # noqa: E402
from pfsp.metrics import rpd  # noqa: E402


def stable_seed(seed: int, *parts: str) -> np.random.SeedSequence:
    return np.random.SeedSequence([seed] + [zlib.crc32(p.encode()) for p in parts])


def load_best_known(path: Path | None) -> dict[str, int]:
    if path is None or not path.exists():
        return {}
    with path.open() as f:
        return {row["instance"]: int(row["best_known"]) for row in csv.DictReader(f) if row.get("best_known")}


def run_one(instance, algo_name: str, params: dict, seed: int, budget_rule, objective: str,
            reference: int | None, ref_source: str, history_dir: Path | None) -> dict:
    run_fn, default_params = REGISTRY[algo_name]
    all_params = {**default_params, **params}
    max_ffe = budget_for(instance.size, instance.n_jobs, budget_rule)
    ev = Evaluator(instance, objective=objective, max_ffe=max_ffe)
    rng = np.random.default_rng(stable_seed(seed, algo_name, instance.name))
    t0 = time.perf_counter()
    status = "finished"
    try:
        run_fn(ev, rng, **all_params)
    except BudgetExhausted:
        status = "budget"
    except NotImplementedError as exc:
        status = f"not_implemented: {exc}"
    elapsed = time.perf_counter() - t0
    row = {
        "instance": instance.name, "size": instance.size, "algorithm": algo_name,
        "params": json.dumps(all_params, sort_keys=True), "seed": seed, "objective": objective,
        "best": ev.best_value, "ffe_used": ev.ffe, "max_ffe": max_ffe,
        "reference": reference, "ref_source": ref_source,
        "rpd": None if (ev.best_value is None or not reference) else round(rpd(ev.best_value, reference), 4),
        "time_s": round(elapsed, 3), "status": status,
        "best_perm": " ".join(map(str, ev.best_perm.tolist())) if ev.best_perm is not None else "",
    }
    if history_dir is not None:
        history_dir.mkdir(parents=True, exist_ok=True)
        with (history_dir / f"{algo_name}__{instance.name}__s{seed}.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ffe", "best"])
            w.writerows(ev.history)
    return row


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default="data/taillard", help="katalog z plikami instancji")
    ap.add_argument("--pattern", default="*", help="filtr nazw instancji (fnmatch), np. 'tai20_5_[01]'")
    ap.add_argument("--algorithms", nargs="+", required=True, choices=sorted(REGISTRY))
    ap.add_argument("--params", default="{}", help='JSON z parametrami dla wszystkich algorytmów, np. \'{"pop_size": 100}\'')
    ap.add_argument("--seeds", type=int, default=20, help="liczba uruchomień (seedy 0..N-1)")
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--budget", default="literature", help="literature | 1000n2 | none | liczba FFE")
    ap.add_argument("--objective", default="makespan", choices=["makespan", "tft"])
    ap.add_argument("--best-known", default=None, help="CSV instance,best_known (domyślnie data/best_known_<cel>.csv)")
    ap.add_argument("--jobs", type=int, default=1, help="liczba równoległych procesów (-1 = wszystkie rdzenie)")
    ap.add_argument("--out", default="results/results.csv")
    ap.add_argument("--history", action="store_true", help="zapisz krzywe zbieżności do results/history/")
    args = ap.parse_args(argv)

    instances = [i for i in load_dir(args.data) if fnmatch.fnmatch(i.name, args.pattern)]
    if not instances:
        sys.exit(f"Brak instancji pasujących do {args.pattern!r} w {args.data}")
    bk_path = Path(args.best_known) if args.best_known else ROOT / "data" / f"best_known_{args.objective}.csv"
    best_known = load_best_known(bk_path)
    params = json.loads(args.params)
    budget_rule = int(args.budget) if args.budget.isdigit() else args.budget
    history_dir = ROOT / "results" / "history" if args.history else None

    tasks = []
    for inst in instances:
        if inst.name in best_known:
            ref, src = best_known[inst.name], "best_known_csv"
        elif args.objective == "makespan" and inst.upper_bound:
            ref, src = inst.upper_bound, "file_ub_1993"
        else:
            ref, src = None, "none"
        for algo in args.algorithms:
            seeds = [0] if algo == "neh" else range(args.seed_start, args.seed_start + args.seeds)
            for s in seeds:
                tasks.append((inst, algo, params, s, budget_rule, args.objective, ref, src, history_dir))

    print(f"{len(instances)} instancji × {len(args.algorithms)} algorytmów -> {len(tasks)} uruchomień")
    rows = Parallel(n_jobs=args.jobs, verbose=10 if args.jobs != 1 else 0)(
        delayed(run_one)(*t) for t in tasks)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_header = not out.exists()
    with out.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if write_header:
            w.writeheader()
        w.writerows(rows)
    print(f"Zapisano {len(rows)} wierszy do {out}")
    for r in rows:
        if r["status"].startswith("not_implemented"):
            print(f"  UWAGA: {r['algorithm']} – {r['status']}")
            break


if __name__ == "__main__":
    main()
