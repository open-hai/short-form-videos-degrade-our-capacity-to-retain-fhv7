"""Inner-loop entrypoint for Chiossi et al., CHI '23 (doi:10.1145/3544548.3580778).

Runs the paper's analysis pipeline over a trial-level dataset and prints an
observed-vs-reported comparison for every quantity the paper states.

    python src/analyze.py DATA/rt.csv --questionnaires DATA/q.csv --out results/

Nothing in here touches the human study: it consumes trials that already exist.
See REPRODUCIBILITY.md for what that boundary excludes.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import accuracy as acc_mod  # noqa: E402
import art_anova  # noqa: E402
import bayes_factor  # noqa: E402
import figures as fig_mod  # noqa: E402
from io_utils import describe_trials, load_trials  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def log(msg):
    print(msg, flush=True)


def compare(observed, reported, tol, label, citation, notes=""):
    if observed is None or reported is None:
        status = "n/a"
        delta = None
    else:
        delta = observed - reported
        status = "match" if abs(delta) <= tol else "MISMATCH"
    return {
        "quantity": label,
        "citation": citation,
        "reported": reported,
        "observed": observed,
        "delta": delta,
        "tolerance": tol,
        "status": status,
        "notes": notes,
    }


def term_key(term: str) -> str:
    """Human-readable key for a patsy term name."""
    out = term.replace("C(interrupt, Treatment(\"tiktok\"))", "interrupt")
    out = out.replace("C(interrupt, Treatment(\"rest\"))", "interrupt")
    out = out.replace("C(measure, Treatment(\"post\"))", "measure")
    out = out.replace("C(task, Treatment(\"LD\"))", "task")
    return out.replace("[T.", "[").replace("]", "]")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="trial-level CSV (the authors' rt.csv schema)")
    ap.add_argument("--questionnaires", help="questionnaire CSV (the authors' q.csv schema)")
    ap.add_argument(
        "--ddm",
        help="pre-fitted DDM parameter CSV; if omitted the fits are computed here",
    )
    ap.add_argument("--out", default="results", help="output directory")
    ap.add_argument(
        "--ddm-dt", type=float, default=0.001, help="DDM time step (paper's notebook uses 1e-4)"
    )
    ap.add_argument(
        "--skip-cell-ddm",
        action="store_true",
        help="skip the 240 per-participant DDM fits (Table 1 then needs --ddm)",
    )
    ap.add_argument("--no-figures", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    reported = json.load(open(os.path.join(HERE, "reported.json")))
    results = {"input": os.path.abspath(args.input), "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    comparisons = []

    # ---------------------------------------------------------------- data
    log("[1/8] loading trials")
    trials = load_trials(args.input)
    desc = describe_trials(trials)
    results["data_description"] = desc
    log(json.dumps(desc, indent=2, ensure_ascii=False))
    d = reported["design"]
    comparisons.append(
        compare(
            desc["n_participants"], d["n_participants"], 0, "participants", d["citation"]
        )
    )
    comparisons.append(
        compare(
            desc["pm_cue_trials_per_participant_per_block"]["mean"],
            d["pm_trials_per_block"],
            0.5,
            "PM cue trials per participant per block",
            d["citation"],
            "counted as trials whose stimulus is one of the three PM cue words",
        )
    )

    # ------------------------------------------------------------ accuracy
    log("[2/8] deriving accuracy and fitting the accuracy LMMs")
    acc = acc_mod.derive_accuracy(trials)
    acc.to_csv(os.path.join(args.out, "accuracy_derived.csv"), index=False)
    acc_mod.cell_means(acc).to_csv(os.path.join(args.out, "accuracy_cell_means.csv"), index=False)
    models = acc_mod.accuracy_models(acc)
    results["lmm"] = models
    keys = ["lmm_ld", "lmm_pm", "lmm_ld_vs_pm"]
    for model, key in zip(models, keys):
        rep = reported[key]
        comparisons.append(
            compare(
                round(model["r2_conditional"], 2),
                rep["r2"],
                0.01,
                f"{key}: conditional R2",
                rep["citation"],
                "paper quotes a single R2 without saying marginal or conditional",
            )
        )
        comparisons.append(
            compare(model["df"], rep["df"], 0, f"{key}: t degrees of freedom", rep["citation"])
        )
        for term in model["terms"]:
            name = term_key(term["term"])
            for wanted, obs in rep["terms"].items():
                if wanted.split(":")[0] in name and (
                    ":" not in wanted or wanted.split(":")[1] in name
                ):
                    if (":" in wanted) != (":" in name):
                        continue
                    comparisons.append(
                        compare(
                            round(term["beta"], 3),
                            obs["beta"],
                            0.006,
                            f"{key}: beta[{wanted}]",
                            rep["citation"],
                        )
                    )
                    comparisons.append(
                        compare(
                            round(term["t"], 2),
                            obs["t"],
                            0.05,
                            f"{key}: t[{wanted}]",
                            rep["citation"],
                        )
                    )
    # sensitivity: PM defined by stimulus rather than by the key pressed
    acc_stim = acc_mod.derive_accuracy(trials, label_by="stimulus")
    acc_stim.to_csv(os.path.join(args.out, "accuracy_derived_stimulus_labelled.csv"), index=False)
    results["lmm_sensitivity_stimulus_labelled"] = acc_mod.accuracy_models(acc_stim)

    # ------------------------------------------- trial-level RT / accuracy
    log("[3/8] trial-level RT and accuracy models")
    import rt_models

    results["rt_models"] = rt_models.rt_models(trials)
    results["trial_level_accuracy_models"] = rt_models.trial_level_accuracy_models(trials)
    for model in results["rt_models"]:
        sig = [t["term"] for t in model["terms"] if t["p"] < 0.05 and t["term"] != "Intercept"]
        comparisons.append(
            compare(
                1 if sig else 0,
                0,
                0,
                f"Section 4.1.2: significant fixed effects in {model['model'].split(' ')[0]} RT model",
                "Section 4.1.2",
                f"paper reports none; found: {sig if sig else 'none'}",
            )
        )

    # ----------------------------------------------------------------- DDM
    log("[4/8] DDM parameters")
    if args.ddm:
        ddm = pd.read_csv(args.ddm)
        results["ddm_source"] = f"supplied: {os.path.abspath(args.ddm)}"
    elif args.skip_cell_ddm:
        ddm = None
        results["ddm_source"] = "skipped"
    else:
        import ddm_fit

        ddm = ddm_fit.fit_all_cells(trials, dt=args.ddm_dt, progress=log)
        ddm.to_csv(os.path.join(args.out, "ddm_refit.csv"), index=False)
        results["ddm_source"] = f"refitted here (dt={args.ddm_dt})"

    if ddm is not None:
        log("[5/8] Table 1 ANOVAs on the DDM parameters")
        table1 = art_anova.anova_table(ddm)
        pd.DataFrame(table1).to_csv(os.path.join(args.out, "table1.csv"), index=False)
        results["table1"] = table1
        rep = reported["table1"]
        for row in table1:
            key = f"{row['task']}/{row['parameter']}/{row['effect']}"
            if key in rep["rows"]:
                r = rep["rows"][key]
                comparisons.append(
                    compare(round(row["F"], 3), r["F"], 0.01, f"Table 1 F[{key}]", rep["citation"], row["method"])
                )
                comparisons.append(
                    compare(round(row["effect_size"], 3), r["es"], 0.01, f"Table 1 effect size[{key}]", rep["citation"], row["effect_size_kind"])
                )
        posthoc = art_anova.posthoc_contrasts(ddm, task="PM")
        pd.DataFrame(posthoc).to_csv(os.path.join(args.out, "posthoc_pm.csv"), index=False)
        results["posthoc_pm"] = posthoc

    # ------------------------------------------------------- pooled TikTok
    log("[6/8] pooled TikTok PM fits (Figure 6)")
    import ddm_fit

    pooled = ddm_fit.fit_pooled_tiktok(trials, dt=args.ddm_dt)
    results["figure6"] = pooled
    rep = reported["figure6"]
    for measure in ("pre", "post"):
        comparisons.append(
            compare(round(pooled[measure]["accuracy"] * 100, 2), rep[measure]["accuracy_pct"], 0.01, f"Fig 6 {measure} accuracy %", rep["citation"])
        )
        comparisons.append(
            compare(round(pooled[measure]["drift"], 2), rep[measure]["drift"], 0.05, f"Fig 6 {measure} drift", rep["citation"], "differential evolution is unseeded")
        )
        comparisons.append(
            compare(round(pooled[measure]["noise"], 2), rep[measure]["noise"], 0.05, f"Fig 6 {measure} noise", rep["citation"], "differential evolution is unseeded")
        )
        comparisons.append(
            compare(round(pooled[measure]["bound"], 2), rep[measure]["bound"], 0.05, f"Fig 6 {measure} bound", rep["citation"], "differential evolution is unseeded")
        )
        comparisons.append(
            compare(round(pooled[measure]["nondectime"] * 1000), rep[measure]["nondectime_ms"], 2, f"Fig 6 {measure} non-decision time (ms)", rep["citation"])
        )
        comparisons.append(
            compare(round(pooled[measure]["loss"], 2), rep[measure]["loss"], 0.2, f"Fig 6 {measure} fit loss", rep["citation"])
        )

    # ------------------------------------------------------ questionnaires
    if args.questionnaires:
        log("[7/8] questionnaire ANOVAs and Bayes factors")
        q = pd.read_csv(args.questionnaires)
        rows = bayes_factor.questionnaire_tests(q)
        results["questionnaires"] = rows
        pd.DataFrame(rows).to_csv(os.path.join(args.out, "questionnaires.csv"), index=False)
        rep = reported["questionnaires"]
        for row in rows:
            r = rep.get(row["scale"])
            if r:
                comparisons.append(compare(round(row["F"], 3), r["F"], 0.01, f"{row['scale']} F", rep["citation"]))
                comparisons.append(compare(round(row["p"], 3), r["p"], 0.001, f"{row['scale']} p", rep["citation"]))
                comparisons.append(
                    compare(round(row["BF01"], 3), r["BF01"], 0.01, f"{row['scale']} BF01", rep["citation"], "BayesFactor's anovaBF is Monte Carlo; this is quadrature")
                )
        extra = [c for c in q.columns if c.startswith("META_")]
        if extra:
            results["undocumented_questionnaire_columns"] = extra

    # -------------------------------------------------------------- figures
    if not args.no_figures:
        log("[8/8] figures")
        paths = fig_mod.figure3(trials, args.out)
        paths.append(fig_mod.figure4(acc, args.out))
        if ddm is not None:
            paths.append(fig_mod.figure5(ddm, args.out))
        paths.append(fig_mod.figure6(trials, pooled, args.out))
        results["figures"] = paths

    # -------------------------------------------------------------- output
    results["comparisons"] = comparisons
    with open(os.path.join(args.out, "results.json"), "w") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False, default=float)
    table = pd.DataFrame(comparisons)
    table.to_csv(os.path.join(args.out, "comparison.csv"), index=False)

    n_match = int((table.status == "match").sum())
    n_mismatch = int((table.status == "MISMATCH").sum())
    log("")
    log(table[["quantity", "reported", "observed", "delta", "status"]].to_string(index=False))
    log("")
    log(f"{n_match} quantities within tolerance, {n_mismatch} outside, of {len(table)} compared")
    log(f"wrote {os.path.join(args.out, 'results.json')} and comparison.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
