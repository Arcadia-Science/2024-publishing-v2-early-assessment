"""
Analyzes publication feedback survey responses with temporal and categorical breakdowns. Note that
the included pub_feedback_form.csv is more up-to-date than what was reported in the pub. You may
note small differences.

Analysis Features:
- Response rates by version and question
- Temporal trends in submission patterns
- Monthly submission analysis
- Question-by-question breakdown

Response Handling:
- Empty responses are tracked but excluded from percentage calculations
- Partial responses (some questions answered) are included
- Questions analyzed:
  - Straightforwardness
  - Potential usefulness
  - Information completeness
  - Evidence support

CSV Requirements (the included pub_feedback_form.csv file meets these requirements):
- Must contain columns:
  - Date submitted
  - Publishing version (from Pub)
  - Question response columns:
    - How straightforward was this pub?
    - Could this pub be useful in your own work?
    - Were you able to find all the information you'd need to assess or reuse this work?
    - Does the evidence presented support the claims
"""

import sys
import pandas as pd


def format_count_and_percentage(count, total):
    """Helper function to format count and percentage"""
    percentage = (count / total * 100) if total > 0 else 0
    return f"{count} ({percentage:.1f}%)"


def analyze_feedback(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Convert date string to datetime, handling both AM/PM formats
    df["Date submitted"] = pd.to_datetime(
        df["Date submitted"], format="%m/%d/%Y %I:%M%p", errors="coerce"
    )

    # Basic counts by version
    total_responses = len(df)
    version_counts = df["Publishing version (from Pub)"].value_counts()

    print("Overall Statistics:")
    print(f"Total responses: {total_responses}")
    print("\nResponses by version:")
    for version, count in version_counts.items():
        print(f"{version}: {format_count_and_percentage(count, total_responses)}")

    # Analysis for each question
    questions = [
        "How straightforward was this pub?",
        "Could this pub be useful in your own work?",
        "Were you able to find all the information you'd need to assess or reuse this work?",
        "Does the evidence presented support the claims",
    ]

    print("\nDetailed Analysis by Version:")
    print("-" * 50)

    for question in questions:
        print(f"\n{question}")

        # Calculate total responses for each version
        total_by_version = df.groupby("Publishing version (from Pub)").size()

        # Calculate non-null responses for each version
        valid_responses = df.groupby("Publishing version (from Pub)")[question].count()

        # Calculate response rates
        response_rates = (valid_responses / total_by_version * 100).round(1)

        # Create a crosstab for raw counts and percentages
        raw_counts = pd.crosstab(df["Publishing version (from Pub)"], df[question])
        percentages = (
            pd.crosstab(
                df["Publishing version (from Pub)"], df[question], normalize="index"
            )
            * 100
        )

        print("\nBreakdown by response:")
        # Print combined table with counts and percentages
        for version in raw_counts.index:
            print(f"\n{version}:")
            version_total = raw_counts.loc[version].sum()
            for column in raw_counts.columns:
                count = raw_counts.loc[version, column]
                pct = percentages.loc[version, column]
                print(
                    f"  {column}: {format_count_and_percentage(count, version_total)}"
                )

        print("\nResponse rates:")
        for version in response_rates.index:
            responded = valid_responses[version]
            total = total_by_version[version]
            print(f"{version}: {format_count_and_percentage(responded, total)}")

    # Temporal analysis
    print("\nTemporal Analysis:")
    print("-" * 50)
    df["month_year"] = df["Date submitted"].dt.to_period("M")
    monthly_counts = pd.crosstab(df["month_year"], df["Publishing version (from Pub)"])

    print("\nMonthly submission counts (last 10 months):")
    last_10_months = monthly_counts.tail(10)
    for month in last_10_months.index:
        print(f"\n{month}:")
        month_total = last_10_months.loc[month].sum()
        for version in last_10_months.columns:
            count = last_10_months.loc[month, version]
            print(f"  {version}: {format_count_and_percentage(count, month_total)}")

    # Calculate average responses per month
    print("\nAverage monthly submissions:")
    months_with_data = monthly_counts.astype(bool).sum()
    avg_monthly = (monthly_counts.sum() / months_with_data).round(1)
    total_avg = avg_monthly.sum()
    for version, avg in avg_monthly.items():
        print(
            f"{version}: {avg:.1f} per month ({(avg / total_avg * 100):.1f}% of monthly average) "
            + f"across {months_with_data[version]} months with data"
        )


if __name__ == "__main__":
    filepath = (
        sys.argv[1]
        if len(sys.argv) > 1
        else ("../../data/202412_original_pub/pub_feedback_form_responses.csv")
    )
    analyze_feedback(filepath)
