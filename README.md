# Reproducing "Short-Form Videos Degrade Our Capacity to Retain Intentions"

A reproducibility audit and a working re-implementation of the analysis of:

> Francesco Chiossi, Luke Haliburton, Changkun Ou, Andreas Butz, Albrecht Schmidt.
> **Short-Form Videos Degrade Our Capacity to Retain Intentions: Effect of Context Switching
> On Prospective Memory.** CHI '23. [doi:10.1145/3544548.3580778](https://doi.org/10.1145/3544548.3580778)
> (preprint: [arXiv:2302.03714](https://arxiv.org/abs/2302.03714))

## What the paper is

A between-subjects lab experiment with 60 participants (15 per condition). Participants performed
a lexical decision (LD) task with an embedded prospective memory (PM) task — press a special key
when one of three German colour words ("blau", "lila", "grün") appears — in two blocks separated
by a 10-minute interruption. The interruption was one of four conditions: *Rest*, *Twitter*,
*YouTube* or *TikTok* (Section 3). Accuracy and reaction times were modelled with linear mixed
models, a drift-diffusion model (DDM) was fitted per participant, and its parameters were entered
into two-way ANOVAs (Sections 4.1.1–4.1.3). Questionnaire scales (engagement, SUQ-A, BSMAS) were
compared with one-way ANOVAs plus Bayes factors (Section 4.2). The headline finding: PM accuracy
after the interruption dropped only in the TikTok condition.

## What this repository is

An independent re-implementation of the paper's **inner loop** — everything downstream of the
trial data — written in Python from the paper's text, and run against the authors' released
CC-0 dataset. It does **not** attempt the human study, and it does not simulate participants.

| File | What it holds |
|---|---|
| `REPRODUCIBILITY.md` | The verdict: per-component reproduction table, inner/outer boundary, hidden decisions, open-science scorecard |
| `verdict.json` | The same findings as data |
| `instrument.json` | The declared study protocol, the analysis entrypoint contract, the servability assessment |
| `SOURCES.md` | Paper identity and every artifact search performed, with results |
| `UNVERIFIED.md` | What could not be confirmed, each with its blocker |
| `src/` | The re-implementation |
| `results/` | Output of the run recorded in `REPRODUCIBILITY.md` |

## Running it

```bash
pip install -r requirements.txt

# the authors' data are CC-0 but are not vendored here; fetch them outside this repo
python src/fetch_data.py --dest /tmp/mpm-data

# full pipeline, using the authors' released DDM parameters for Table 1
python src/analyze.py /tmp/mpm-data/rt.csv \
    --questionnaires /tmp/mpm-data/q.csv \
    --ddm /tmp/mpm-data/ddm.csv \
    --out results

# or refit all 240 DDMs yourself (slow: ~10 min at dt=1e-3, ~1 h at the authors' dt=1e-4)
python src/analyze.py /tmp/mpm-data/rt.csv --questionnaires /tmp/mpm-data/q.csv \
    --ddm-dt 0.0001 --out results-refit

# how much of the published DDM parameter values is optimiser noise
python src/ddm_stability.py /tmp/mpm-data/rt.csv --repeats 8 --dt 0.0001
```

`src/analyze.py` prints an observed-vs-reported table for every number the paper states that can
be recomputed, and writes `results.json`, `comparison.csv`, the derived accuracy tables, the
Table 1 ANOVA, the post-hoc contrasts, the questionnaire tests and re-drawn versions of
Figures 3–6.

## The pieces

* `src/io_utils.py` — input schema, validation, design descriptives.
* `src/accuracy.py` — accuracy derivation (Section 4.1.1) and the three accuracy LMMs, with
  Nakagawa R² and lme4-style Wald t.
* `src/rt_models.py` — trial-level RT models (Section 4.1.2) and the footnote-2 trial-level
  binomial model.
* `src/ddm_fit.py` — PyDDM fits, per participant and pooled (Sections 3.6, 4.1.3, Figure 6).
* `src/art_anova.py` — the Shapiro-gated ART / mixed ANOVA of Table 1, plus post-hoc contrasts.
* `src/bayes_factor.py` — one-way ANOVAs and JZS Bayes factors of Section 4.2.
* `src/figures.py` — Figures 3–6 re-drawn.
* `src/ddm_stability.py` — repeated unseeded DDM fits, to measure how identifiable the published
  parameters are.
* `src/reported.json` — every number quoted from the paper, each tagged with its section, table
  or figure. This is the ground truth the comparison table is checked against.

## Headline result

The inner loop is largely reproducible: the accuracy models, Table 1, the questionnaire ANOVAs
and Bayes factors and the Figure 6 fit statistics come back at or very near the published values
from the released data. Three things do not: the paper's stated PM trial count, the R² quoted for
the lexical-decision model, and the claim that the reaction-time analyses found nothing. The DDM
parameter values themselves turn out not to be identified — see `REPRODUCIBILITY.md` for the
per-component table and the evidence.
