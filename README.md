# PA-DRI: Precision Apiculture Dataset Readiness Index

Reproducibility materials for **“Assessing AI Readiness of Precision Apiculture Datasets: A Reproducible Benchmark”** (CSNT 2026).

PA-DRI is a documentation-based screening index for comparing the artificial-intelligence readiness of precision-apiculture datasets. This repository contains the ordinal scoring matrix for 12 purposively selected datasets (eight legacy datasets coded from a previously published review and four additions coded from primary sources) and a script that reproduces the paper's quantitative tables, figures, and weight-sensitivity analysis. The scores represent evidence-supported screening judgements; they do not establish downstream predictive performance or inter-rater reliability.

## Contents

- `data/dataset_scores.csv` — 12 datasets, modality, cohort (`A` = added; `L` = legacy), and seven integer scores (`D1`–`D7`, each 0–2).
- `scripts/generate_csnt26_results.py` — reads the scoring CSV, calculates the index, and runs the deterministic sensitivity analysis.
- `requirements.txt` — pinned Python dependencies.
- `results/` — created when the script runs; contains publication tables, figures and a methods summary.

The dataset-level evidence notes supporting the individual judgements are **not yet included** in this repository and should be added separately before claiming that the full evidence-coding process is independently auditable.

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

Each dimension is scored **0** (absent, severely limited or insufficiently documented), **1** (partial evidence), or **2** (strong documented evidence), according to the operational rubric in the accompanying paper. The equal-weight index for dataset *i* is `PA-DRI_i = (50/7) * sum(D1, ..., D7)`, on a 0–100 scale. Equal weighting is a reference choice, not an objectively neutral weighting scheme.

## Reproduce the results

Run the following commands from the **repository root** using Python 3:

```bash
python -m pip install -r requirements.txt
python scripts/generate_csnt26_results.py
```

By default, the generated outputs are written to `results/`:

- `Table_2_PA_DRI.csv` — equal-weight dataset scores, simulated 5th–95th percentile intervals and top-three probabilities.
- `Table_2_Audit.csv` — separate numerical columns for checking Table 2.
- `Table_3_Dimension_Readiness.csv` — mean readiness and number of zero scores by dimension.
- `Figure_1_PA_DRI.png` and `.pdf` — equal-weight dataset scores.
- `Figure_2_Weight_Sensitivity.png` and `.pdf` — median simulated scores and 5th–95th percentile intervals.
- `Spearman_and_Methodology.txt` — analysis settings and summary statistics.

An alternative output directory may be provided with `--output`, e.g.:

```bash
python scripts/generate_csnt26_results.py --output "D:\\PhD_2021_\\Editings\\Conf 2026\\CSNT26"
```

The script also accepts `--input` to specify an alternative scoring CSV with the same schema.

## Simulation details

- **Draws:** 20,000 independent weight vectors from the symmetric `Dirichlet(1, 1, 1, 1, 1, 1, 1)` distribution.
- **Random generator:** NumPy `default_rng(20260817)` (PCG64).
- **Weighted score:** `50 * sum(weight_j * score_ij)`.
- **Spearman correlation:** Pearson correlation of descending ranks, with average ranks for ties, computed against the equal-weight ranking for each draw.
- **Top-three probability:** proportion of draws in which a dataset has competition rank 1, 2 or 3. Ties are included, with tolerance `1e-10` on the 0–100 score scale.

Using the pinned environment and the supplied score matrix, the median Spearman correlation is **0.922**, with a **5th–95th percentile interval of 0.723–0.993** (rounded to three decimals). The two identical UrBAN and sunflower scoring profiles each have a top-three probability of **89.9%**; Sentinel-2 Level-2A has **25.5%**, and Hymenoptera recognition **12.8%** (rounded to one decimal).

## Scope and limitations

The 12-dataset corpus is purposive, not a representative sample of all available precision-apiculture datasets. Legacy entries were scored from the cited review rather than through renewed repository-level audits. Weight sensitivity varies the importance of dimensions but does not quantify uncertainty in the assigned ordinal scores. No independent second-rater study or empirical validation against downstream model performance is provided.

## Citation

If you use these materials, cite the accompanying CSNT 2026 paper, **“Assessing AI Readiness of Precision Apiculture Datasets: A Reproducible Benchmark”**. Publication metadata can be added here when available.
