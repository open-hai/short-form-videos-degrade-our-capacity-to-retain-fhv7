"""Trial-level models: reaction times (Section 4.1.2) and the footnote-2 check.

Section 4.1.2 reports a Gamma-log GLMM on raw RTs with crossed random effects
for participant and stimulus, and states that nothing was significant.  Footnote
2 reports a trial-level binomial regression "accounting for per item and per
participants effects" and states it was "completely consistent" with the LMM.

Neither model can be fitted in Python exactly as lme4 fits it: statsmodels has
no Gamma GLMM and no Laplace/AGQ binomial GLMM with crossed random effects.  The
two closest available approximations are used instead, and both are labelled as
approximations wherever their output is reported:

* RT: a log-normal LMM (log RT, identity link) with crossed variance components
  for participant and stimulus.  On these data it lands within 0.01 of the
  authors' own released Gamma-log coefficients.
* Accuracy: `BinomialBayesMixedGLM` (variational Bayes) with the same crossed
  variance components.

One further choice is not in the paper but is in the authors' notebook: the RT
models are fitted on *correct* trials only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM

FORMULA = 'C(interrupt, Treatment("rest")) * C(measure, Treatment("pre"))'
VC = {"participant": "0 + C(folder_id)", "stimulus": "0 + C(stimulus)"}


def _tidy(name, res, n, extra=None):
    p_params = len(res.fe_params)
    df = n - p_params - 2
    terms = []
    for term in res.fe_params.index:
        beta = float(res.fe_params[term])
        se = float(res.bse[term])
        t = beta / se
        crit = stats.t.ppf(0.975, df)
        terms.append(
            {
                "term": term.replace('C(interrupt, Treatment("rest"))', "interrupt").replace(
                    'C(measure, Treatment("pre"))', "measure"
                ),
                "beta": beta,
                "ci_low": beta - crit * se,
                "ci_high": beta + crit * se,
                "t": t,
                "df": df,
                "p": float(2 * stats.t.sf(abs(t), df)),
            }
        )
    out = {"model": name, "n_trials": n, "terms": terms}
    if extra:
        out.update(extra)
    out["any_significant_fixed_effect"] = any(
        term["p"] < 0.05 for term in terms if term["term"] != "Intercept"
    )
    return out


def rt_models(trials: pd.DataFrame) -> list[dict]:
    """Log-normal approximation to the Section 4.1.2 RT GLMMs."""
    out = []
    for task in ("LD", "PM"):
        d = trials[
            (trials.task == task)
            & (trials.measure != "train")
            & (trials.success)
            & (trials.correct)
        ].dropna(subset=["rt"]).copy()
        d["log_rt"] = np.log(d["rt"])
        d["_all"] = 1
        res = smf.mixedlm(
            f"log_rt ~ {FORMULA}", d, groups=d["_all"], vc_formula=VC
        ).fit(reml=True)
        out.append(
            _tidy(
                f"{task} log RT ~ interrupt * measure + (1|folder_id) + (1|stimulus)",
                res,
                len(d),
                {"approximation": "log-normal LMM in place of lme4 Gamma(log) GLMM",
                 "trials_used": "correct responses only (authors' notebook, not stated in the paper)"},
            )
        )
    return out


def trial_level_accuracy_models(trials: pd.DataFrame) -> list[dict]:
    """Footnote 2: trial-level binomial model with participant and item effects."""
    out = []
    for task in ("LD", "PM"):
        d = trials[
            (trials.task == task) & (trials.measure != "train") & (trials.success)
        ].copy()
        d["y"] = d["correct"].astype(int)
        d["interrupt"] = pd.Categorical(
            d["interrupt"], categories=["tiktok", "rest", "twitter", "youtube"]
        )
        d["measure"] = pd.Categorical(d["measure"], categories=["post", "pre"])
        res = BinomialBayesMixedGLM.from_formula(
            "y ~ interrupt * measure", VC, d
        ).fit_vb(verbose=False)
        terms = []
        for name, mean, sd in zip(res.model.exog_names, res.fe_mean, res.fe_sd):
            z = mean / sd
            terms.append(
                {
                    "term": name,
                    "posterior_mean": float(mean),
                    "posterior_sd": float(sd),
                    "z": float(z),
                    "credible_interval_excludes_zero": bool(abs(z) > 1.96),
                }
            )
        out.append(
            {
                "model": f"{task} correct ~ interrupt * measure + (1|folder_id) + (1|stimulus)",
                "n_trials": int(len(d)),
                "approximation": "variational-Bayes binomial GLMM in place of lme4 glmer",
                "reference_cell": "tiktok / post",
                "terms": terms,
            }
        )
    return out
