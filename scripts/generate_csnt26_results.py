"""Reproduce PA-DRI Tables 2–3, Figures 1–2 and Spearman sensitivity statistics.
Created by SelOua HADDAOUI

Dependencies: pip install numpy scipy pandas matplotlib
Run from repository root: python scripts/generate_csnt26_results.py
Optional: python scripts/generate_csnt26_results.py --output "D:\\other\\folder"
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import rankdata

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPOSITORY_ROOT / 'data' / 'dataset_scores.csv'
DEFAULT_OUTPUT = REPOSITORY_ROOT / 'results'
SEED = 20260817
N_DRAWS = 20_000
DIMENSION_KEYS = [f'D{i}' for i in range(1, 8)]
DIMENSIONS = [
    'Accessibility', 'Machine readability', 'Scale adequacy',
    'Quality/completeness', 'Diversity/representativeness',
    'Task alignment', 'Deployment/longitudinal utility',
]


def load_dataset_scores(input_csv: Path):
    df = pd.read_csv(input_csv, encoding='utf-8-sig')
    required = ['Dataset', 'Modality', 'Group', *DIMENSION_KEYS]
    missing = [column for column in required if column not in df]
    if missing:
        raise ValueError(f'Missing columns: {missing}')
    if len(df) != 12 or df['Dataset'].duplicated().any():
        raise ValueError('Expected 12 distinct datasets.')
    if not df['Group'].isin(['A', 'L']).all():
        raise ValueError('Group values must be A or L.')
    if (df['Group'] == 'A').sum() != 4:
        raise ValueError('Expected four added datasets.')
    if df[DIMENSION_KEYS].isna().any().any():
        raise ValueError('Missing dimension scores.')
    scores = df[DIMENSION_KEYS].to_numpy(dtype=float)
    if not np.all(np.isin(scores, [0, 1, 2])):
        raise ValueError('Dimension scores must be 0, 1 or 2.')
    return df, scores


def compute(input_csv: Path):
    source, scores = load_dataset_scores(input_csv)
    names = source['Dataset'].tolist()
    groups = source['Group'].to_numpy()
    assert scores.shape == (12, 7)
    assert np.all(np.isin(scores, [0, 1, 2]))

    equal = 50 * scores.mean(axis=1)
    rng = np.random.default_rng(SEED)  # NumPy PCG64 generator
    weights = rng.dirichlet(np.ones(7, dtype=np.float64), size=N_DRAWS)
    weighted = 50 * (weights @ scores.T)  # shape (20,000, 12)
    low, med, high = np.percentile(weighted, [5, 50, 95], axis=0)

    # Competition/tie-inclusive top-three rule: ALL tied datasets whose
    # minimum/competition rank is <= 3 count as top three.
    # Example: if 2 datasets are tied at 3rd, both are included.
    # Count number of datasets strictly ahead, avoiding floating-point
    # near-ties by assigning the same dot-product to identical profiles.
    # Scores can be extremely close for distinct profiles, but these
    # count as different unless equal within 1e-10 on the 0-100 scale.
    ahead = np.sum(weighted[:, :, None] < weighted[:, None, :] - 1e-10,
                   axis=2)  # [draw, candidate]: number of others ahead
    # IMPORTANT: the comparison axes here use candidate (axis 1) and opponent (axis 2):
    # weighted[:, :, None] < weighted[:, None, :] means candidate < opponent.
    p_top3 = np.mean(ahead < 3, axis=0) * 100

    base_ranks = rankdata(-equal, method='average')
    ranks = np.array([rankdata(-row, method='average') for row in weighted])
    x = base_ranks - base_ranks.mean()
    y = ranks - ranks.mean(axis=1, keepdims=True)
    rho = (y @ x) / np.sqrt(np.sum(x ** 2) * np.sum(y ** 2, axis=1))

    df = pd.DataFrame({
        'Dataset': names,
        'Modality': source['Modality'].tolist(),
        'Group': groups,
        'Equal-weight PA-DRI': np.round(equal, 1),
        '5th percentile': np.round(low, 1),
        '95th percentile': np.round(high, 1),
        'P(Top 3) (%)': np.round(p_top3, 1),
    })
    # Stable descending score sort, equal-score ties alphabetised.
    df = df.sort_values(['Equal-weight PA-DRI', 'Dataset'],
                        ascending=[False, True]).reset_index(drop=True)
    name_to_ix = {name: i for i, name in enumerate(names)}
    idx = np.array([name_to_ix[name] for name in df['Dataset']])
    # Explicitly verify identical scoring profiles have identical distributions.
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if np.array_equal(scores[i], scores[j]):
                assert np.allclose(weighted[:, i], weighted[:, j])
                assert np.isclose(p_top3[i], p_top3[j])

    return df, idx, names, groups, scores, equal, low, med, high, weighted, rho, p_top3


def save_figure1(out, df):
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    rows = df.iloc[::-1]
    y = np.arange(len(rows))
    bars = ax.barh(y, rows['Equal-weight PA-DRI'], height=0.72,
                   color='#4C78A8', edgecolor='#1F4E79', linewidth=0.7)
    for bar, group in zip(bars, rows['Group']):
        if group == 'A':
            bar.set_hatch('///')
    ax.set_yticks(y, rows['Dataset'])
    ax.set_xlabel('Equal-weight PA-DRI (0 to 100)')
    ax.set_xlim(0, 108)
    for yi, score in zip(y, rows['Equal-weight PA-DRI']):
        ax.text(score + 1, yi, f'{score:.1f}', va='center', fontsize=8)
    ax.grid(axis='x', alpha=0.2)
    ax.set_axisbelow(True)
    fig.tight_layout()
    for ext in ('png', 'pdf'):
        fig.savefig(out / f'Figure_1_PA_DRI.{ext}', dpi=300, bbox_inches='tight')
    plt.close(fig)


def save_figure2(out, df, idx, low, med, high, equal):
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    labels = df['Dataset'].tolist()[::-1]
    indices = idx[::-1]
    y = np.arange(len(indices))
    median = med[indices]
    l = low[indices]
    h = high[indices]
    ax.errorbar(median, y, xerr=[median - l, h - median],
                fmt='o', markersize=4.5, capsize=3, color='#1F4E79',
                ecolor='#4C78A8', elinewidth=1.4, label='Median and 5th to 95th percentiles')
    ax.scatter(equal[indices], y, marker='|', color='#2A9DCE', s=90,
               label='Equal-weight score', zorder=3)
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 103)
    ax.set_xlabel('PA-DRI under Dirichlet(1, 1, 1, 1, 1, 1, 1) weights (0 to 100)')
    ax.grid(axis='x', alpha=0.2)
    ax.set_axisbelow(True)
    ax.legend(loc='lower right', fontsize=8, frameon=False)
    fig.tight_layout()
    for ext in ('png', 'pdf'):
        fig.savefig(out / f'Figure_2_Weight_Sensitivity.{ext}', dpi=300, bbox_inches='tight')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)

    df, idx, names, groups, scores, equal, low, med, high, weighted, rho, ptop = compute(args.input)
    # Full-precision statistics for auditing, plus formatted manuscript table.
    df['5th–95th percentile'] = (df['5th percentile'].map('{:.1f}'.format) + '–' +
                                df['95th percentile'].map('{:.1f}'.format))
    df['P(Top 3)'] = df['P(Top 3) (%)'].map('{:.1f}%'.format)
    manuscript_cols = ['Dataset', 'Modality', 'Group', 'Equal-weight PA-DRI',
                       '5th–95th percentile', 'P(Top 3)']
    df[manuscript_cols].to_csv(out / 'Table_2_PA_DRI.csv', index=False, encoding='utf-8-sig')
    df.to_csv(out / 'Table_2_Audit.csv', index=False, encoding='utf-8-sig')
    table3 = pd.DataFrame({
        'Dimension': DIMENSIONS,
        'Readiness (%)': np.round(scores.mean(axis=0) * 50, 1),
        'No. with score 0': np.sum(scores == 0, axis=0),
    })
    # Keep the same dimension ordering as Table 3 in the manuscript.
    table3 = table3.sort_values('Readiness (%)', kind='stable').reset_index(drop=True)
    table3.to_csv(out / 'Table_3_Dimension_Readiness.csv', index=False, encoding='utf-8-sig')
    save_figure1(out, df)
    save_figure2(out, df, idx, low, med, high, equal)

    summary = np.percentile(rho, [5, 50, 95])
    equal_ranks = rankdata(-equal, method='average')
    lines = [
        f'Random generator: numpy.random.default_rng({SEED}) (PCG64)',
        f'Dirichlet: alpha=[1,1,1,1,1,1,1]; number of draws: {N_DRAWS}',
        'Spearman: Pearson correlation of descending ranks; ties use average ranks.',
        'Top 3: count all tied datasets if competition rank <= 3.',
        f'Spearman median: {summary[1]:.6f}',
        f'Spearman 5th–95th: {summary[0]:.6f}–{summary[2]:.6f}',
        f'Manuscript rounded: {summary[1]:.3f} ({summary[0]:.3f}–{summary[2]:.3f})',
        f'Added-group equal-weight mean: {equal[groups == "A"].mean():.3f}',
        f'Legacy-group equal-weight mean: {equal[groups == "L"].mean():.3f}',
        '',
        'Equal-weight dataset ranks (average tie ranks):',
        *[f'  {name}: {rank:g}' for name, rank in zip(names, equal_ranks)],
    ]
    (out / 'Spearman_and_Methodology.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines[:9]))
    print('\n' + df[manuscript_cols].to_string(index=False))
    print(f'\nSaved to: {out.resolve()}')


if __name__ == '__main__':
    main()
