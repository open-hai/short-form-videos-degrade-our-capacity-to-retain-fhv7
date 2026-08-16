# Sources

## The paper

| Field | Value |
|---|---|
| Title | Short-Form Videos Degrade Our Capacity to Retain Intentions: Effect of Context Switching On Prospective Memory |
| Authors | Francesco Chiossi, Luke Haliburton, Changkun Ou, Andreas Butz, Albrecht Schmidt (all LMU Munich) |
| Venue | CHI '23 — Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems, Hamburg, Germany, April 23–28 2023 |
| DOI | [10.1145/3544548.3580778](https://doi.org/10.1145/3544548.3580778) |
| ISBN | 978-1-4503-9421-5/23/04 |
| Preprint | arXiv:2302.03714 (submitted 7 Feb 2023), DOI 10.48550/arXiv.2302.03714 |
| Length | 14 pages in the author PDF (the ACM reference format line in the paper itself says "14 pages"; the GitHub README and the ACM DL landing page both say 15) |
| Funding | DFG Project-ID 251654672-TRR 161 (Chiossi); Bavarian Research Alliance ForDigitHealth (Haliburton) — Acknowledgments |
| Data collection credit | Martina Gluderer (Acknowledgments; GitHub README) |

### Full text used for this audit

The publisher landing page (`https://dl.acm.org/doi/10.1145/3544548.3580778`) is behind a
Cloudflare interstitial and returned HTTP 403 to every automated request made here, so the
full text was taken from two author-hosted copies that carry the same ACM reference format
block and DOI:

* `https://arxiv.org/pdf/2302.03714` — fetched, 14 pages, text extracted with pypdf.
* `https://github.com/mimuc/media-prospective-memory/blob/main/chiossi2023short.pdf` — fetched
  in the repository clone, 14 pages, byte-identical page count and content to the arXiv PDF for
  the sections used here.
* `https://www.mmi.ifi.lmu.de/pubdb/publications/pub/chiossi2023short/chiossi2023short.pdf` —
  HTTP 200, same author copy on the group's publication database.

Every section, table and figure citation in this repository refers to that text.

## Artifact search

Each row is a place actually queried on 2026-08-16, with the URL and the result.
`found` = the artifact is there and was fetched; `none` = nothing was ever published there;
`dead` = something was published there and no longer resolves.

| Where | What was looked for | Result | Evidence |
|---|---|---|---|
| Paper Section 7 "Open Science" + footnote 4 | authors' own pointer to artifacts | found | Footnote 4 gives `https://github.com/mimuc/media-prospective-memory`; Section 7 claims "our experimental setup, collected datasets, and analysis scripts are available on Github" |
| GitHub `mimuc/media-prospective-memory` | code, data | found | HTTP 200; cloned; API reports created 2023-01-20, last push 2023-12-20, licence GPL-3.0, not archived, default branch `main`, single branch |
| GitHub repo contents | PsychoPy experiment / "experimental setup" | **none** | `git ls-files` lists 4 notebooks + 5 analysis notebooks, `stats.py`, `stats.R`, `requirements.txt`, `LICENSE`, the paper PDF, `data/{rt,acc,ddm,q}.csv` and `figures/*.pdf`. There is no PsychoPy program, no stimulus list file, no questionnaire, no video list |
| OSF project `osf.io/kzxy7` | data, supplements, preregistration | found | Linked from the GitHub README ("The [dataset](https://osf.io/kzxy7/)"). HTTP 200; OSF API v2 shows a public project created 2022-12-02, last modified 2023-12-22, licence "GNU General Public License (GPL) 3.0" |
| OSF file listing | files not on GitHub | found | 18 entries. Two exist only on OSF: `CHI23_Questionnaires.pdf` (fetched, 6 pages — Engagement item, SUQ-A, BSMAS) and `YT_interruption_Videos_list.txt` (fetched — the YouTube interruption playlist) |
| OSF `data/` folder | released data | found | `rt.csv`, `acc.csv`, `ddm.csv`, `q.csv`, same names and sizes as GitHub |
| OSF registrations endpoint for the project | preregistration | **none** | `api.osf.io/v2/nodes/kzxy7/registrations/` returns 0 registrations |
| OSF registries, title search "prospective memory" | preregistration | **none** | 10 registrations returned, none by these authors and none matching this study |
| OSF node search, title "short-form videos" | any other project by the authors | found (same one) | one node returned: `kzxy7`, `registration: false` |
| arXiv `2302.03714` abstract page | ancillary files | **none** | HTTP 200; page has a "Code, Data and Media" section but it links third-party indexes; `https://arxiv.org/src/2302.03714/anc` returns 404 |
| ACM DL `dl.acm.org/doi/10.1145/3544548.3580778` | supplementary material tab, artifact badges | **not verifiable here** | HTTP 403 (Cloudflare) on every request. The paper (Section 3.5) says "The questionnaires are included in the supplementary material"; the questionnaire PDF was instead located on OSF |
| LMU MMI publication database | author copy, extra material | found (paper only) | `https://www.mmi.ifi.lmu.de/pubdb/publications/pub/chiossi2023short/chiossi2023short.pdf` HTTP 200 |
| `changkun.de` (author page) | project page / extra artifacts | found (pointer only) | HTTP 200; the research listing links the same `prospective-memory` project |
| Zenodo API, `q="prospective memory" AND tiktok` | archived artifact copy | **none** | 0 hits |
| Zenodo API, creator "Chiossi" | archived artifact copy | **none** | 0 hits |
| GitHub search `org:mimuc memory` | any second repo (e.g. the experiment program) | **none beyond the one** | only `mimuc/media-prospective-memory` |
| GitHub search `psychopy prospective memory tiktok` | the experiment program elsewhere | **none** | 0 repositories |
| GitLab | mirror of the artifact | **none** | no project found under the authors' or the group's names |

## What the authors released, precisely

Fetched and inspected:

* `data/rt.csv` — 21,480 trial-level rows: `folder_id, task, interrupt, measure, stimulus, success, correct, rt`. 60 participants, 15 per condition. This is the real raw material of the paper.
* `data/acc.csv` — 240 rows of derived per-participant accuracy (regenerated exactly by `1.1.response_accuracy.ipynb` and by `src/accuracy.py` here).
* `data/ddm.csv` — 240 rows of fitted DDM parameters (`drift, noise, bound, nondectime`).
* `data/q.csv` — 60 rows: `SUQ, BSMARS, META_CC, META_POS, META_CSC, META_NEG, META_NC, ENGAGE`. The five `META_*` columns are not mentioned anywhere in the paper or in the released questionnaire PDF.
* Nine Jupyter notebooks (a mix of Python and R kernels) plus `stats.py` and `stats.R`, all with stored outputs.
* `figures/*.pdf` — the six figure files of the paper.
* `CHI23_Questionnaires.pdf` and `YT_interruption_Videos_list.txt` — OSF only.

Not released anywhere that could be found: the PsychoPy program, the SUBTLEX-DE word/pseudo-word
stimulus lists as such (the strings themselves survive inside `rt.csv`), the beginning/ending
Google Forms surveys including the demographic and screen-time items, the raw questionnaire item
responses, and any preregistration.

## Downstream literature consulted (context only, not evidence about this paper)

* A 2025 *Memory* article ("Context-switching in short-form videos: What is the impact on
  prospective memory?", doi:10.1080/09658211.2025.2521076) builds directly on this design; it was
  read only to confirm how the paradigm is described by others, and none of its numbers are used
  here.
