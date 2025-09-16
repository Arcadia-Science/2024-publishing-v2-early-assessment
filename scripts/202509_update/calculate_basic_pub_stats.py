import pandas as pd
from scipy import stats
import numpy as np

CURRENT_DATA_FILE = "data/202509_update/basic_pub_stats.csv"
ORIGINAL_DATA_FILE = "data/202412_original_pub/basic_pub_stats.csv"

# --- Helper functions ---


def calculate_descriptive_stats(data_series):
    """Calculates descriptive stats: n, mean/SD, 95% CI for mean, median/IQR."""
    series = pd.to_numeric(data_series, errors="coerce").dropna()

    n = len(series)
    if n < 2:
        return {
            "n": n,
            "mean": np.nan,
            "std": np.nan,
            "sem": np.nan,
            "ci_95": (np.nan, np.nan),
            "median": np.nan,
            "q1": np.nan,
            "q3": np.nan,
        }

    mean = series.mean()
    std = series.std(ddof=1)
    sem = stats.sem(series, ddof=1)

    ci_95 = stats.t.interval(0.95, df=n - 1, loc=mean, scale=sem)

    return {
        "n": n,
        "mean": mean,
        "std": std,
        "sem": sem,
        "ci_95": ci_95,
        "median": series.median(),
        "q1": series.quantile(0.25),
        "q3": series.quantile(0.75),
    }


def print_summary_stats(title, stats_dict, show_ci=True):
    """Pretty-print stats dictionary."""
    n = stats_dict["n"]
    print(f"\n# {title} (n={n}):")

    if n > 1:
        mean, std = stats_dict["mean"], stats_dict["std"]
        median, q1, q3 = stats_dict["median"], stats_dict["q1"], stats_dict["q3"]
        ci_low, ci_high = stats_dict["ci_95"]

        print(f"  - Mean: {mean:.1f}, SD: {std:.1f}")
        print(f"  - Median: {median:.1f}, IQR: [{q1:.1f}, {q3:.1f}]")
        if show_ci:
            print(f"  - 95% CI for mean: [{ci_low:.1f}, {ci_high:.1f}]")


def compare_groups(series1, series2):
    """
    Compares two groups with parametric and non-parametric tests:
    - Welch's t-test (compare means of the two group)
    - Mann-Whitney U as a robustness check (to see if the distributions are different)

    Returns formatted p-values.
    """
    s1 = pd.to_numeric(series1, errors="coerce").dropna()
    s2 = pd.to_numeric(series2, errors="coerce").dropna()

    # Welch's t-test (does not assume equal variances)
    ttest_res = stats.ttest_ind(s1, s2, equal_var=False)

    # Mann–Whitney U (two-sided)
    mwu_res = stats.mannwhitneyu(s1, s2, alternative="two-sided", method="asymptotic")

    return {"welch_t_p_value": ttest_res.pvalue, "mwu_p_value": mwu_res.pvalue}


def calculate_mean_difference_effects(series1, series2):
    """Calculates Hedges' g and the 95% CI for the difference in means (Welch)."""
    s1 = pd.to_numeric(series1, errors="coerce").dropna()
    s2 = pd.to_numeric(series2, errors="coerce").dropna()

    n1, n2 = len(s1), len(s2)
    m1, m2 = s1.mean(), s2.mean()
    v1, v2 = s1.var(ddof=1), s2.var(ddof=1)

    # Hedges' g (small-sample bias corrected)
    pooled_std = np.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    d = (m1 - m2) / pooled_std
    j = 1 - 3 / (4 * (n1 + n2) - 9)
    hedges_g = d * j

    # Calculate Glass's delta (non-equal variance)
    sd1 = np.sqrt(v1)  # sd1 is v1.0's SD
    glass_delta = (m1 - m2) / sd1

    # 95% CI for the difference in means (Welch–Satterthwaite)
    se_diff = np.sqrt(v1 / n1 + v2 / n2)
    df_welch = (v1 / n1 + v2 / n2) ** 2 / (
        (v1**2) / (n1**2 * (n1 - 1)) + (v2**2) / (n2**2 * (n2 - 1))
    )
    t_crit = stats.t.ppf(0.975, df=df_welch)
    mean_diff = m1 - m2
    ci_diff = (mean_diff - t_crit * se_diff, mean_diff + t_crit * se_diff)

    return {
        "hedges_g": hedges_g,
        "glass_delta": glass_delta,
        "mean_diff_ci_95": ci_diff,
    }


def main_v2_analysis(current_filepath, original_filepath):
    """
    Analyze pub data and print summaries, effect sizes, and non-parametric checks.
    In-progress (right censored) times are descriptive only.
    """

    df_current = pd.read_csv(current_filepath)
    df_original = pd.read_csv(original_filepath)

    # --- 1. Clean data
    work_col = "Workdays in progress"
    df_current[work_col] = pd.to_numeric(df_current[work_col], errors="coerce")
    df_current.dropna(subset=[work_col], inplace=True)
    df_current = df_current[
        df_current[work_col] > 0
    ].copy()  # keep only positive durations

    flesch_col = "Flesch reading ease version of record"
    if flesch_col in df_current.columns:
        # Clean and coerce to numeric (they're stored as percentages in basic_pub_stats.csv)
        df_current[flesch_col] = (
            df_current[flesch_col].astype(str).str.replace("%", "", regex=False)
        )
        df_current[flesch_col] = pd.to_numeric(df_current[flesch_col], errors="coerce")

    # --- 2. Stats for published pubs
    v1_published = df_current[
        (df_current["Publishing version"] == "v1.0")
        & (df_current["Status"] == "🔔 Published 🔔")
    ]
    v2_published = df_current[
        (df_current["Publishing version"] == "v2.0")
        & (df_current["Status"] == "🔔 Published 🔔")
    ]

    workdays_v1 = v1_published[work_col]
    workdays_v2 = v2_published[work_col]

    print("--- Published pub stats ---")
    stats_v1 = calculate_descriptive_stats(workdays_v1)
    stats_v2 = calculate_descriptive_stats(workdays_v2)
    print_summary_stats("Version 1.0 pubs", stats_v1)
    print_summary_stats("Version 2.0 pubs (all)", stats_v2)
    print("-" * 55)

    # --- 3. Comparison: v1.0 vs v2.0 ---
    print("\n--- Comparison (workdays): v1.0 vs v2.0 (published) ---")
    comparisons = compare_groups(workdays_v1, workdays_v2)
    effects = calculate_mean_difference_effects(workdays_v1, workdays_v2)
    print(f"  - Welch's t-test p-value: {comparisons['welch_t_p_value']:.4f}")
    print(f"  - Mann-Whitney U p-value: {comparisons['mwu_p_value']:.4f}")
    print(f"  - Effect size (Hedges' g): {effects['hedges_g']:.3f}")
    print(
        f"  - 95% CI for mean difference: [{effects['mean_diff_ci_95'][0]:.1f}, "
        f"{effects['mean_diff_ci_95'][1]:.1f}] workdays"
    )
    print("-" * 55)

    # --- 4. 'New' vs. initial v2.0 pubs ---
    original_v2_ids = set(
        df_original[df_original["Publishing version"] == "v2.0"]["ArbitraryID"]
    )
    initial_v2_pubs = v2_published[v2_published["ArbitraryID"].isin(original_v2_ids)]
    new_v2_pubs = v2_published[~v2_published["ArbitraryID"].isin(original_v2_ids)]

    workdays_initial_v2 = initial_v2_pubs[work_col]
    workdays_new_v2 = new_v2_pubs[work_col]

    print("\n--- v2.0 performance over time ---")
    stats_init_v2 = calculate_descriptive_stats(workdays_initial_v2)
    stats_new_v2 = calculate_descriptive_stats(workdays_new_v2)
    print_summary_stats("Initial v2.0 pubs", stats_init_v2)
    print_summary_stats("'New' v2.0 pubs", stats_new_v2)

    print("\n# Comparison: initial vs. new v2.0")
    comparisons_v2 = compare_groups(workdays_initial_v2, workdays_new_v2)
    effects_v2 = calculate_mean_difference_effects(workdays_initial_v2, workdays_new_v2)
    print(f"  - Welch's t-test p-value: {comparisons_v2['welch_t_p_value']:.4f}")
    print(f"  - Mann-Whitney U p-value: {comparisons_v2['mwu_p_value']:.4f}")
    print(f"  - Effect size (Hedges' g): {effects_v2['hedges_g']:.3f}")
    print(f"  - Effect size (Glass's delta): {effects_v2['glass_delta']:.3f}")
    print(
        f"  - 95% CI for mean difference: [{effects_v2['mean_diff_ci_95'][0]:.1f}, "
        f"{effects_v2['mean_diff_ci_95'][1]:.1f}] workdays"
    )
    print("-" * 55)

    # --- 5. In-progress pubs (descriptive only) ---
    in_progress_pubs = df_current[df_current["Status"] != "🔔 Published 🔔"]
    workdays_in_progress = in_progress_pubs[work_col]

    print("\n--- Current in-progress pubs (right-censored data) ---")
    stats_prog = calculate_descriptive_stats(workdays_in_progress)
    print_summary_stats("All in-progress pubs", stats_prog, show_ci=False)
    print("-" * 55)

    # --- 6. Flesch Reading Ease (published) ---
    if flesch_col in df_current.columns:
        fre_v1_raw = v1_published[flesch_col]
        fre_v2_raw = v2_published[flesch_col]

        fre_v1 = pd.to_numeric(fre_v1_raw, errors="coerce").dropna()
        fre_v2 = pd.to_numeric(fre_v2_raw, errors="coerce").dropna()

        fre_v1 = fre_v1[fre_v1.between(0, 100)]
        fre_v2 = fre_v2[fre_v2.between(0, 100)]

        print("\n--- Flesch Reading Ease (published) ---")
        stats_fre_v1 = calculate_descriptive_stats(fre_v1)
        stats_fre_v2 = calculate_descriptive_stats(fre_v2)
        print_summary_stats("Version 1.0 pubs FRE", stats_fre_v1)
        print_summary_stats("Version 2.0 pubs FRE", stats_fre_v2)

        print("\n# Comparison: FRE v1 vs v2")
        comparisons_fre = compare_groups(fre_v1, fre_v2)
        effects_fre = calculate_mean_difference_effects(fre_v1, fre_v2)
        print(f"  - Welch's t-test p-value: {comparisons_fre['welch_t_p_value']:.4f}")
        print(f"  - Mann-Whitney U p-value: {comparisons_fre['mwu_p_value']:.4f}")
        print(f"  - Effect size (Hedges' g): {effects_fre['hedges_g']:.3f}")
        print("-" * 55)


if __name__ == "__main__":
    main_v2_analysis(CURRENT_DATA_FILE, ORIGINAL_DATA_FILE)
