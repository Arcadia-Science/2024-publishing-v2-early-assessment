import pandas as pd
from scipy.stats import chi2_contingency
from statsmodels.stats.multitest import multipletests

UPDATED_RESPONSES_FILE = "data/202509_update/pub_feedback_form_responses.csv"

FEEDBACK_FORM_QUESTIONS = [
    "How straightforward was this pub?",
    "Could this pub be useful in your own work?",
    "Were you able to find all the information you'd need to assess or reuse this work?",
    "Does the evidence presented support the claims?",
]

pd.set_option("display.max_columns", None)


def analyze_version_differences_v2(filepath):
    """
    Analyze feedback differences between v1.0 and v2.0.
    Applies Bonferroni and BH-FDR corrections; prints counts and row-wise percentages.
    """

    df = pd.read_csv(filepath)

    print("=" * 80)
    print("Feedback responses: v1.0 vs. v2.0 pubs")
    print("=" * 80)

    # --- 1. Run tests and collect raw p-values ---
    analysis_results = []
    for question in FEEDBACK_FORM_QUESTIONS:
        counts_table = pd.crosstab(df["Publishing version (from Pub)"], df[question])

        _, p_raw, _, _ = chi2_contingency(counts_table)

        analysis_results.append(
            {
                "question": question,
                "counts_table": counts_table,
                "p_raw": p_raw,
            }
        )

    # --- 2. Multiple testing corrections ---
    raw_p_values = [res["p_raw"] for res in analysis_results]

    # Bonferroni (FWER control)
    _, p_bonferroni, _, _ = multipletests(raw_p_values, alpha=0.05, method="bonferroni")

    # Benjamini–Hochberg (FDR control)
    _, q_fdr, _, _ = multipletests(raw_p_values, alpha=0.05, method="fdr_bh")

    # Attach adjusted values to results
    for i, res in enumerate(analysis_results):
        res["p_bonferroni"] = p_bonferroni[i]
        res["q_fdr"] = q_fdr[i]

    # --- 3. Print formatted results ---
    for res in analysis_results:
        print("-" * 80)
        print(f"Question: {res['question']}")
        print("-" * 80)

        counts_table = res["counts_table"]
        percentages_table = counts_table.div(counts_table.sum(axis=1), axis=0) * 100
        display_table = (
            counts_table.astype(str)
            + " ("
            + percentages_table.round(1).astype(str)
            + "%)"
        )

        print(display_table)
        print("-" * 50)

        total_n = counts_table.to_numpy().sum()
        print(f"Test results (N={total_n}):")
        print(f"   - Raw Chi-squared p-value:         {res['p_raw']:.4f}")
        print(f"   - Bonferroni-corrected p-value:    {res['p_bonferroni']:.4f}")
        print(f"   - Benjamini-Hochberg FDR q-value:  {res['q_fdr']:.4f}")

        if res["p_bonferroni"] < 0.05:
            print("   - Significant after Bonferroni correction.")
        elif res["q_fdr"] < 0.05:
            print("   - Significant after FDR correction.")
        else:
            print("   - Not significant after multiple testing correction.")

        print("\n")


if __name__ == "__main__":
    analyze_version_differences_v2(UPDATED_RESPONSES_FILE)
