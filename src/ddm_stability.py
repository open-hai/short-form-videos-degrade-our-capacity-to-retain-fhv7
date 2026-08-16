"""How stable is the DDM fit that Figure 6 reports?

`fit_adjust_model(..., fitting_method="differential_evolution")` is a stochastic
global optimiser and the authors' notebook sets no seed, so the published
parameter values are one draw.  This script repeats the pooled TikTok PM fit and
reports the spread of each parameter and of the loss.

    python src/ddm_stability.py DATA/rt.csv --repeats 8 --dt 0.001
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ddm_fit  # noqa: E402
from io_utils import load_trials  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--repeats", type=int, default=8)
    ap.add_argument("--dt", type=float, default=0.001)
    ap.add_argument("--out", default="results/ddm_stability.json")
    args = ap.parse_args()

    trials = load_trials(args.input)
    runs = []
    for i in range(args.repeats):
        fit = ddm_fit.fit_pooled_tiktok(trials, dt=args.dt)
        runs.append(fit)
        print(
            f"run {i + 1}: "
            + "  ".join(
                f"{m} mu={fit[m]['drift']:.3f} sigma={fit[m]['noise']:.3f} "
                f"B={fit[m]['bound']:.3f} t={fit[m]['nondectime'] * 1000:.0f}ms "
                f"loss={fit[m]['loss']:.2f}"
                for m in ("pre", "post")
            ),
            flush=True,
        )

    summary = {"dt": args.dt, "repeats": args.repeats, "spread": {}}
    for measure in ("pre", "post"):
        for param in ("drift", "noise", "bound", "nondectime", "loss"):
            vals = [r[measure][param] for r in runs]
            summary["spread"][f"{measure}/{param}"] = {
                "min": min(vals),
                "max": max(vals),
                "mean": statistics.fmean(vals),
                "sd": statistics.pstdev(vals),
            }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump({"runs": runs, "summary": summary}, fh, indent=2)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
