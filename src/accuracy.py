"""Accuracy derivation and the linear mixed models of Section 4.1.1.

Two things are re-implemented here:

1. `derive_accuracy` — the preprocessing the authors do in
   `1.1.response_accuracy.ipynb`: response accuracy is the number of correct key
   presses divided by the number of key presses (Section 4.1.1), i.e. trials
   with no response are dropped from both numerator and denominator.

2. `fit_lmm` — the LMMs of Section 4.1.1.  The paper fits them with lme4 (REML,
   nloptwrap); statsmodels' `MixedLM` is the closest Python equivalent.  lme4's
   `report()` output quotes Wald t values on a residual degrees-of-freedom that
   the paper never states; `N - p - 2` reproduces the paper's df of 114 / 110 /
   230 exactly and is what is used here (see REPRODUCIBILITY.md, decision D4).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from io_utils import PM_CUES


def derive_accuracy(trials: pd.DataFrame, label_by: str = "released") -> pd.DataFrame:
    """Per participant x task x condition x block response accuracy.

    label_by == "released": use the `task` column as released, which labels a
        trial PM whenever the participant pressed a PM key (Q/W/E), whether or
        not the stimulus was a PM cue word.
    label_by == "stimulus": label a trial PM iff the stimulus was one of the
        three PM cue words ("blau", "lila", "grün").  This is the sensitivity
        analysis for decision D1.
    """
    df = trials[trials.measure != "train"].copy()
    if label_by == "stimulus":
        is_cue = df.stimulus.astype(str).str.upper().isin(PM_CUES)
        df["task"] = np.where(is_cue, "PM", "LD")
    elif label_by != "released":
        raise ValueError(label_by)
    df = df[df.success]
    acc = (
        df.groupby(["folder_id", "task", "interrupt", "measure"])
        .correct.agg(["sum", "count"])
        .reset_index()
    )
    acc["accuracy"] = acc["sum"] / acc["count"]
    return acc.drop(columns=["sum"]).rename(columns={"count": "n_trials"})


def _nakagawa_r2(res, data) -> tuple[float, float]:
    var_f = float(np.var(res.predict(data), ddof=0))
    var_r = float(np.asarray(res.cov_re)[0, 0])
    var_e = float(res.scale)
    total = var_f + var_r + var_e
    return var_f / total, (var_f + var_r) / total


def fit_lmm(data: pd.DataFrame, formula: str, name: str) -> dict:
    """Fit a random-intercept LMM and report lme4-style Wald t statistics."""
    res = smf.mixedlm(formula, data, groups=data["folder_id"]).fit(reml=True)
    n = len(data)
    p = len(res.fe_params)
    df_resid = n - p - 2  # reproduces the paper's t(114) / t(110) / t(230)
    marginal, conditional = _nakagawa_r2(res, data)
    terms = []
    for term in res.fe_params.index:
        beta = float(res.fe_params[term])
        se = float(res.bse[term])
        t = beta / se
        pval = 2 * stats.t.sf(abs(t), df_resid)
        crit = stats.t.ppf(0.975, df_resid)
        terms.append(
            {
                "term": term,
                "beta": beta,
                "se": se,
                "ci_low": beta - crit * se,
                "ci_high": beta + crit * se,
                "t": t,
                "df": df_resid,
                "p": pval,
            }
        )
    return {
        "model": name,
        "formula": formula,
        "n_observations": n,
        "df": df_resid,
        "r2_marginal": marginal,
        "r2_conditional": conditional,
        "terms": terms,
    }


def accuracy_models(acc: pd.DataFrame) -> list[dict]:
    """The three LMMs reported in Section 4.1.1, in the paper's own contrasts."""
    ld = acc[acc.task == "LD"]
    pm = acc[acc.task == "PM"]
    models = [
        fit_lmm(
            ld,
            'accuracy ~ C(interrupt, Treatment("tiktok"))',
            "LD accuracy ~ interrupt + (1|folder_id)",
        ),
        fit_lmm(
            pm,
            'accuracy ~ C(interrupt, Treatment("tiktok"))'
            ' * C(measure, Treatment("post"))',
            "PM accuracy ~ interrupt * measure + (1|folder_id)",
        ),
        fit_lmm(
            acc,
            'accuracy ~ C(interrupt, Treatment("rest"))'
            ' * C(task, Treatment("LD"))',
            "LD vs PM accuracy ~ interrupt * task + (1|folder_id)",
        ),
    ]
    return models


def cell_means(acc: pd.DataFrame) -> pd.DataFrame:
    return (
        acc.groupby(["task", "interrupt", "measure"])
        .accuracy.agg(["mean", "std", "count"])
        .reset_index()
    )
