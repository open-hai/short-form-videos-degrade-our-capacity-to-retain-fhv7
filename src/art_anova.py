"""Two-way mixed ANOVA on the fitted DDM parameters (Table 1, Section 4.1.3).

The paper states the decision rule in Section 4: "depending on normality,
evaluated by the Shapiro-Wilk test, we report two-way mixed ANOVA results for
parameter analysis on the fitted DDM parameters, or ART ANOVAs for the
non-parametric data".  The authors' `stats.R` shows the rule concretely: a
Shapiro-Wilk test on the whole column, ART (ARTool) if p < .05, `ez::ezANOVA`
otherwise; the effect-size column is partial omega-squared on the ART path and
the ezANOVA effect size on the parametric path.

This module re-implements that rule in Python.  The alignment step follows
Wobbrock et al.'s ART: for each effect, subtract the cell mean, add back the
effect's own estimate, then rank; the ANOVA is then run on the aligned ranks
with the same mixed design.
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
import pingouin as pg
from scipy import stats

BETWEEN = "interrupt"
WITHIN = "measure"
SUBJECT = "folder_id"


def align(d: pd.DataFrame, dv: str) -> dict[str, np.ndarray]:
    """Aligned responses for the two main effects and the interaction."""
    grand = d[dv].mean()
    eff_b = d.groupby(BETWEEN)[dv].transform("mean") - grand
    eff_w = d.groupby(WITHIN)[dv].transform("mean") - grand
    cell = d.groupby([BETWEEN, WITHIN])[dv].transform("mean")
    resid = d[dv] - cell
    interaction = cell - grand - eff_b - eff_w
    return {
        "interrupt": (resid + eff_b).to_numpy(),
        "measure": (resid + eff_w).to_numpy(),
        "interaction": (resid + interaction).to_numpy(),
    }


def _mixed(d: pd.DataFrame, dv: str) -> pd.DataFrame:
    return pg.mixed_anova(
        data=d, dv=dv, between=BETWEEN, within=WITHIN, subject=SUBJECT
    )


def partial_omega_squared(f: float, df1: int, n_subjects: int) -> float:
    """Partial omega^2 as ARTool/effectsize reports it for these designs."""
    return df1 * (f - 1) / (df1 * (f - 1) + n_subjects)


def anova_table(ddm: pd.DataFrame, alpha: float = 0.05) -> list[dict]:
    """Table 1: one row per (task, DDM parameter, effect)."""
    rows = []
    for task in ("PM", "LD"):
        d = ddm[ddm.task == task].copy()
        n_subjects = d[SUBJECT].nunique()
        for param in ("drift", "noise", "bound", "nondectime"):
            w, p_shapiro = stats.shapiro(d[param])
            nonnormal = p_shapiro < alpha
            if nonnormal:
                aligned = align(d, param)
                for effect, source in (
                    ("interrupt", "interrupt"),
                    ("measure", "measure"),
                    ("interaction", "Interaction"),
                ):
                    dd = d.copy()
                    dd["_aligned_rank"] = stats.rankdata(aligned[effect])
                    res = _mixed(dd, "_aligned_rank")
                    r = res[res.Source == source].iloc[0]
                    rows.append(
                        {
                            "task": task,
                            "parameter": param,
                            "effect": effect,
                            "method": "ART",
                            "shapiro_p": float(p_shapiro),
                            "df1": int(r.DF1),
                            "df2": int(r.DF2),
                            "F": float(r.F),
                            "p": float(r.p_unc),
                            "effect_size": partial_omega_squared(
                                float(r.F), int(r.DF1), n_subjects
                            ),
                            "effect_size_kind": "partial omega^2",
                        }
                    )
            else:
                res = _mixed(d, param)
                for effect, source in (
                    ("interrupt", "interrupt"),
                    ("measure", "measure"),
                    ("interaction", "Interaction"),
                ):
                    r = res[res.Source == source].iloc[0]
                    rows.append(
                        {
                            "task": task,
                            "parameter": param,
                            "effect": effect,
                            "method": "mixed ANOVA",
                            "shapiro_p": float(p_shapiro),
                            "df1": int(r.DF1),
                            "df2": int(r.DF2),
                            "F": float(r.F),
                            "p": float(r.p_unc),
                            "effect_size": float(r.np2),
                            "effect_size_kind": "partial eta^2",
                        }
                    )
    return rows


def _holm(pvals: list[float]) -> list[float]:
    order = np.argsort(pvals)
    m = len(pvals)
    adjusted = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        val = (m - rank) * pvals[idx]
        running = max(running, val)
        adjusted[idx] = min(running, 1.0)
    return adjusted.tolist()


def posthoc_contrasts(ddm: pd.DataFrame, task: str = "PM") -> list[dict]:
    """Post-hoc comparisons of Section 4.1.3, on interaction-aligned ranks.

    The paper runs `art.con(..., adjust="holm")`, i.e. ARTool's ART-C procedure
    with emmeans' Kenward-Roger degrees of freedom.  There is no Python
    equivalent; what is done here is the pairwise test on the same aligned ranks
    with the same Holm correction, which recovers the direction and the
    significance pattern but not the paper's exact t and df.
    """
    out = []
    d = ddm[ddm.task == task].copy()
    for param in ("drift", "noise", "bound", "nondectime"):
        aligned = align(d, param)["interaction"]
        d["_r"] = stats.rankdata(aligned)
        wide = d.pivot_table(
            index=[SUBJECT, BETWEEN], columns=WITHIN, values="_r"
        ).reset_index()
        tests = []
        # pre vs post inside each condition
        for cond in sorted(d[BETWEEN].unique()):
            sub = wide[wide[BETWEEN] == cond]
            t, p = stats.ttest_rel(sub["pre"], sub["post"])
            tests.append(
                {
                    "parameter": param,
                    "contrast": f"{cond}: pre vs post",
                    "kind": "within",
                    "t": float(t),
                    "df": int(len(sub) - 1),
                    "p_raw": float(p),
                }
            )
        # every pair of conditions, post-interruption
        for a, b in itertools.combinations(sorted(d[BETWEEN].unique()), 2):
            xa = wide[wide[BETWEEN] == a]["post"]
            xb = wide[wide[BETWEEN] == b]["post"]
            t, p = stats.ttest_ind(xa, xb)
            tests.append(
                {
                    "parameter": param,
                    "contrast": f"{a} vs {b} (post)",
                    "kind": "between",
                    "t": float(t),
                    "df": int(len(xa) + len(xb) - 2),
                    "p_raw": float(p),
                }
            )
        adj = _holm([t["p_raw"] for t in tests])
        for test, p in zip(tests, adj):
            test["p_holm"] = p
        out.extend(tests)
    return out
