# PA-DRI: Precision Apiculture Dataset Readiness Index

Reproducibility materials for **“Assessing AI Readiness of Precision Apiculture Datasets: A Reproducible Benchmark”** (CSNT 2026).

PA-DRI is a documentation-based screening index for comparing the artificial-intelligence readiness of precision-apiculture datasets. This repository contains the ordinal scoring matrix for 12 purposively selected datasets (eight legacy datasets coded from a previously published review and four additions coded from primary sources), a source-referenced scoring evidence register, and a Python script that reproduces the paper's quantitative tables, figures, and weight-sensitivity analysis.

The scores represent documentation-based screening judgements; they do not establish downstream predictive performance or inter-rater reliability.

## Contents

- `data/dataset_scores.csv` — 12 datasets, modality, cohort (`A` = added; `L` = legacy), and seven integer scores (`D1`–`D7`, each 0–2).
- `data/scoring_evidence.csv` — 84 dataset–dimension assessments, including assigned scores, supporting evidence descriptions, source references, scoring justifications, and verification statuses.
- `scripts/generate_csnt26_results.py` — reads the scoring CSV, calculates the index, and performs the reproducible sensitivity analysis.
- `requirements.txt` — pinned Python dependencies.
- `results/` — created when the script runs; contains publication tables, figures, and a methodological summary.

## Scoring dimensions

| Column | Dimension |
|---|---|
| D1 | Accessibility |
| D2 | Machine readability |
| D3 | Scale adequacy |
| D4 | Quality and completeness |
| D5 | Diversity and representativeness |
| D6 | Task alignment |
| D7 | Deployment and longitudinal utility |

Each dimension is scored **0** (absent, severely limited, or insufficiently documented), **1** (partial evidence), or **2** (strong documented evidence), according to the operational rubric in the accompanying paper.

The equal-weight index for dataset *i* is:

`PA-DRI_i = (50/7) * sum(D1, ..., D7)`

The resulting index ranges from 0 to 100. Equal weighting provides a transparent reference rather than an objectively neutral weighting scheme.

## Scoring evidence and verification

The `data/scoring_evidence.csv` file documents the evidence associated with all **84 scoring decisions** (12 datasets × 7 dimensions).

Each record includes the assigned score, a supporting evidence description, a source reference, the corresponding scoring justification, and a verification status. Source identifiers refer to the bibliography of the accompanying paper.

The eight legacy datasets were evaluated using the published CoDIT 2024 review, whereas the four added datasets were evaluated using primary publications.

The evidence register has undergone a preliminary source-consistency review. However, **some scoring decisions remain flagged for further assessment** because the available documentation does not fully establish the assigned score or appears inconsistent with the operational rubric.

These flags are deliberately retained to distinguish source-supported observations from unresolved scoring decisions. The legacy repositories have not been independently re-audited.

The numerical scoring matrix is preserved to reproduce the results reported in the manuscript. Its inclusion does not imply that all individual judgements have been independently validated. Resolving the outstanding evidence discrepancies may require score revisions and regeneration of the corresponding quantitative results.

## Reproduce the results

Run the following commands from the **repository root** using Python 3:

```bash
python -m pip install -r requirements.txt
python scripts/generate_csnt26_results.py
```

By default, the generated outputs are written to `results/`:

- `Table_2_PA_DRI.csv` — equal-weight dataset scores, simulated 5th–95th percentile intervals, and top-three probabilities.
- `Table_2_Audit.csv` — separate numerical columns for verifying Table 2.
- `Table_3_Dimension_Readiness.csv` — mean readiness and number of zero scores by dimension.
- `Figure_1_PA_DRI.png` and `.pdf` — equal-weight dataset scores.
- `Figure_2_Weight_Sensitivity.png` and `.pdf` — median simulated scores and 5th–95th percentile intervals.
- `Spearman_and_Methodology.txt` — analysis settings and summary statistics.

An alternative output directory may be specified using `--output`:

```bash
python scripts/generate_csnt26_results.py --output "D:\PhD_2021_\Editings\Conf 2026\CSNT26"
```

The script also accepts `--input` to specify an alternative scoring CSV with the same schema.

The analysis reads `dataset_scores.csv`. The evidence register is supplied for methodological transparency and does not alter the computations unless the underlying scores are revised.

## Simulation details

- **Draws:** 20,000 weight vectors sampled from the symmetric `Dirichlet(1, 1, 1, 1, 1, 1, 1)` distribution.
- **Random generator:** NumPy `default_rng(20260817)` (PCG64).
- **Weighted score:** `50 * sum(weight_j * score_ij)`.
- **Spearman correlation:** Pearson correlation of descending ranks, using average ranks for ties, calculated against the equal-weight ranking for each draw.
- **Top-three probability:** Proportion of draws in which a dataset has competition rank 1, 2, or 3. Ties are included using a tolerance of `1e-10` on the 0–100 score scale.

Using the pinned environment and supplied scoring matrix, the median Spearman rank correlation is **0.922**, with a **5th–95th percentile interval of 0.723–0.993**, rounded to three decimal places.

The two identical UrBAN and sunflower-pollination scoring profiles each have a top-three probability of **89.9%**. Sentinel-2 Level-2A has **25.5%**, and Hymenoptera recognition has **12.8%**, rounded to one decimal place.

These results quantify sensitivity to alternative dimension weights, not uncertainty in the underlying assigned scores.

## Scope and limitations

The benchmark comprises 12 purposively selected datasets and is not intended to represent the complete population of precision-apiculture datasets.

The eight legacy entries were scored from a previously published review rather than through renewed repository-level audits. Differences in documentation depth between legacy and newly added datasets may influence score comparability.

The ordinal rubric involves judgement, and some evidence-to-score assignments remain flagged for further verification. Weight-sensitivity analysis examines uncertainty in dimension importance but does not quantify uncertainty in the assigned scores themselves.

No independent second-rater assessment or empirical validation against downstream machine-learning performance has been conducted.

Consequently, PA-DRI should be interpreted as an auditable screening and decision-support framework rather than a validated predictor of model performance or a universal dataset ranking.

## Citation

If you use these materials, please cite the accompanying CSNT 2026 paper:

**Haddaoui, S., Guelib, I., Toumi, S.-S., and Chikhi, S.** “Assessing AI Readiness of Precision Apiculture Datasets: A Reproducible Benchmark.” CSNT 2026.

Full publication metadata and DOI will be added when available.
