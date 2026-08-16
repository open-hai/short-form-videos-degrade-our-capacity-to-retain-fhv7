"""Compare two sets of DDM parameter estimates.

Used to ask how much of the published per-participant DDM parameters (Table 1,
Figure 5) survives a refit: the raw parameters, or only the ratios that the
model actually identifies.

    python src/compare_ddm.py released.csv refit.csv
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

KEYS = ["folder_id", "task", "measure"]
PARAMS = ["drift", "noise", "bound", "nondectime"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("a", help="reference parameter CSV (e.g. the authors' ddm.csv)")
    ap.add_argument("b", help="comparison parameter CSV (e.g. your refit)")
    ap.add_argument("--out", default="results/ddm_refit_comparison.json")
    args = ap.parse_args()

    a = pd.read_csv(args.a)
    b = pd.read_csv(args.b)
    merged = a.merge(b, on=KEYS, suffixes=("_a", "_b"))
    out = {"n_cells": int(len(merged)), "parameters": {}, "ratios": {}}

    for param in PARAMS:
        x, y = merged[f"{param}_a"], merged[f"{param}_b"]
        out["parameters"][param] = {
            "pearson_r": float(np.corrcoef(x, y)[0, 1]),
            "median_abs_diff": float((x - y).abs().median()),
            "median_abs_pct_diff": float(((x - y).abs() / x.replace(0, np.nan)).median() * 100),
        }
    for name, num, den in (("drift_over_noise", "drift", "noise"), ("bound_over_noise", "bound", "noise")):
        x = merged[f"{num}_a"] / merged[f"{den}_a"]
        y = merged[f"{num}_b"] / merged[f"{den}_b"]
        out["ratios"][name] = {
            "pearson_r": float(np.corrcoef(x, y)[0, 1]),
            "median_abs_diff": float((x - y).abs().median()),
        }
    print(json.dumps(out, indent=2))
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
