"""
Analyzes and visualizes comment impact data with configurable grouping and display options. Running
script by default will reproduce the same style of visualization as seen in the pub.

NOTE: The results reported in the pub were run on earlier data than what is reported by running
this script. You may notice small discrepancies.

Features:
- Multiple visualization options (pie, donut, bar charts)
- Configurable impact grouping methods
- Version comparison analysis
- Detailed statistical reporting

Impact Handling:
- Multiple impacts per comment are counted separately
- Empty/null impacts are excluded from percentage calculations
- Impact grouping options:
  - Threshold: Groups less frequent impacts based on count
  - Manual: Groups specified impacts into "Other" category

Visualization Notes:
- Pie/donut charts include total counts (n) in center
- Bar charts show direct version comparisons

CSV Requirements:
- Must contain columns:
  - Impact (can contain multiple impacts separated by commas)
  - Publishing version (from Pub)

Statistics Reported:
- Total comments by version
- Impact distributions
- Response rates
- Version comparisons
"""
import argparse
import os

import arcadia_pycolor as apc
import matplotlib.pyplot as plt
import pandas as pd

# Set up Arcadia pycolor
apc.mpl.setup()


# Function to read and process CSV data
def process_csv_data(csv_path):
    # Read CSV file
    csv_data = pd.read_csv(csv_path)

    # Convert comma-separated impact strings into lists
    csv_data['Impact'] = csv_data['Impact'].apply(
        lambda x: str(x).split(',') if pd.notna(x) else [])

    # Keep only relevant columns
    csv_data = csv_data[['Impact', 'Publishing version (from Pub)']]

    return csv_data


# Function to group impacts into "Other"
def group_other_impacts(impact_counts, grouping_method, threshold=None, other_impacts=None):
    if grouping_method == 'threshold':
        if threshold is None:
            raise ValueError("Threshold must be provided for threshold grouping method.")
        common_impacts = (
            impact_counts.groupby('Impact')['Count']
            .sum()
            .reset_index()
            .query('Count >= @threshold')['Impact']
        )
        impact_counts['Impact'] = impact_counts['Impact'].where(
            impact_counts['Impact'].isin(common_impacts), 'Other'
        )
    elif grouping_method == 'manual':
        if other_impacts is None:
            raise ValueError("List of impacts must be provided for manual grouping method.")
        impact_counts['Impact'] = impact_counts['Impact'].apply(
            lambda x: 'Other' if x in other_impacts else x)
    else:
        raise ValueError("Invalid grouping method. Choose 'threshold' or 'manual'.")
    return impact_counts


# Function to set categorical order of impacts
def set_impact_order(impact_counts, sort_version, other_position):
    if sort_version == 'v1':
        sort_by_version = 'v1.0'
    elif sort_version == 'v2':
        sort_by_version = 'v2.0'
    else:
        raise ValueError("Invalid sorting version. Choose 'v1' or 'v2'.")

    ordered_percentages = (
        impact_counts[impact_counts['Publishing version (from Pub)'] == sort_by_version]
        .sort_values(by='Percentage', ascending=False)
    )
    impact_order = ordered_percentages['Impact'].tolist()

    if other_position == 'end':
        if 'Other' in impact_order:
            impact_order.remove('Other')
            impact_order.append('Other')
    elif other_position != 'natural':
        raise ValueError("Invalid 'other' position. Choose 'end' or 'natural'.")

    impact_counts['Impact'] = pd.Categorical(
        impact_counts['Impact'], categories=impact_order, ordered=True
    )

    return impact_counts


def print_statistics(impact_counts, original_data, expanded_data):
    """Print detailed statistics about comment impacts."""
    print("\n=== Comment Impact Statistics ===\n")

    # Print comment and impact counts by version
    print("Comment and Impact Counts by Version:")
    print(f"{'Metric':<30} {'v1.0':>10} {'v2.0':>10}")
    print("-" * 50)

    for version in ['v1.0', 'v2.0']:
        version_data = original_data[original_data['Publishing version (from Pub)'] == version]
        version_expanded = expanded_data[expanded_data['Publishing version (from Pub)'] == version]

        if 'stats' not in locals():
            stats = {}

        stats[version] = {
            'total_comments': len(version_data),
            'rated_comments': len(version_data[version_data['Impact'].apply(lambda x: len(x) > 0)]),
            'unrated_comments': len(
                version_data[version_data['Impact'].apply(lambda x: len(x) == 0)]),
            'total_impacts': len(version_expanded)
        }

    metrics = [
        ('Total Comments', 'total_comments'),
        ('Rated Comments', 'rated_comments'),
        ('Unrated Comments', 'unrated_comments'),
        ('Total Impacts', 'total_impacts')
    ]

    for metric_name, metric_key in metrics:
        v1_value = stats['v1.0'][metric_key]
        v2_value = stats['v2.0'][metric_key]
        print(f"{metric_name:<30} {v1_value:>10} {v2_value:>10}")

    print("\nDetailed Impact Breakdown by Version:")

    # Print detailed breakdown by version
    for version in impact_counts['Publishing version (from Pub)'].unique():
        print(f"\n{version}:")
        version_stats = impact_counts[
            impact_counts['Publishing version (from Pub)'] == version
            ].sort_values('Count', ascending=False)

        print(f"{'Impact Type':<45} {'Count':>8} {'Percentage':>12}")
        print("-" * 65)

        for _, row in version_stats.iterrows():
            impact = row['Impact']
            count = int(row['Count'])
            percentage = row['Percentage']
            print(f"{impact:<45} {count:>8} {percentage:>11.1f}%")

        total = version_stats['Count'].sum()
        print("-" * 65)
        print(f"{'Total':<45} {int(total):>8} {100:>11.1f}%")


def create_plot(impact_counts, impact_pivot, versions, chart_type, chart_style='pie'):
    if chart_type == 'bar':
        fig, ax = plt.subplots(figsize=(12, 6))
        bar_width = 0.35
        x = range(len(impact_pivot))

        for i, version in enumerate(versions):
            offset = i * bar_width
            ax.bar([p + offset for p in x], impact_pivot[version], bar_width, label=version)

        ax.set_xlabel('Impact', fontsize=14)
        ax.set_ylabel('Percentage of Impacts', fontsize=14)
        ax.set_title('Distribution of Impacts by Publishing Version', fontsize=16)
        ax.set_xticks([p + bar_width / 2 for p in x])
        ax.set_xticklabels(impact_pivot['Impact'], rotation=45, ha='right', fontsize=12)
        ax.legend(title='Publishing Version', fontsize=12)
        ax.tick_params(axis='y', labelsize=12)

    elif chart_type == 'pie':
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

        wedge_order = [
            'No real impact',
            'Other',
            'Typo/small error',
            'Commenter got an idea/changed their perspective',
            'Influenced our thinking'
        ]

        # Set wedge width based on chart style
        wedge_width = 0.5 if chart_style == 'donut' else 1.0

        # First pie/donut chart (v1.0)
        v1_data = []
        v1_labels = []
        for category in wedge_order:
            if category in impact_pivot['Impact'].values:
                value = impact_pivot.loc[impact_pivot['Impact'] == category, 'v1.0'].iloc[0]
                if pd.notna(value) and value > 0:
                    v1_data.append(value)
                    v1_labels.append(category)

        v1_total = int(round(
            impact_counts[impact_counts['Publishing version (from Pub)'] == 'v1.0']['Count'].sum()))

        wedges1, _, autotexts1 = ax1.pie(v1_data,
                                         autopct='%1.1f%%',
                                         pctdistance=0.85,
                                         startangle=90,
                                         counterclock=True,
                                         wedgeprops=dict(width=wedge_width))

        ax1.text(0, 0, f'n = {v1_total}', ha='center', va='center')

        # Second pie/donut chart (v2.0)
        v2_data = []
        v2_labels = []
        for category in wedge_order:
            if category in impact_pivot['Impact'].values:
                value = impact_pivot.loc[impact_pivot['Impact'] == category, 'v2.0'].iloc[0]
                if pd.notna(value) and value > 0:
                    v2_data.append(value)
                    v2_labels.append(category)

        v2_total = int(round(
            impact_counts[impact_counts['Publishing version (from Pub)'] == 'v2.0']['Count'].sum()))

        wedges2, _, autotexts2 = ax2.pie(v2_data,
                                         autopct='%1.1f%%',
                                         pctdistance=0.85,
                                         startangle=90,
                                         counterclock=True,
                                         wedgeprops=dict(width=wedge_width))

        ax2.text(0, 0, f'n = {v2_total}', ha='center', va='center')

        # Legend using wedge labels
        readable_order = [
            'No real impact',
            'Influenced our thinking',
            'Commenter got an idea/changed their perspective',
            'Typo/small error',
            'Other'
        ]

        legend_handles = [wedge for wedge in wedges1]
        legend_labels = [label for label in v1_labels]

        sorted_handles_labels = []
        for category in readable_order:
            if category in legend_labels:
                idx = legend_labels.index(category)
                sorted_handles_labels.append((legend_handles[idx], category))

        sorted_handles, sorted_labels = zip(*sorted_handles_labels)

        fig.legend(sorted_handles,
                   sorted_labels,
                   title="Impacts",
                   loc="lower center",
                   bbox_to_anchor=(0.5, 0.1),
                   ncol=len(sorted_labels))

        plt.setp(autotexts1 + autotexts2, size=10)
        plt.subplots_adjust(wspace=0.2, right=0.85, bottom=0.2)
        ax1.set_aspect('equal')
        ax2.set_aspect('equal')

    return fig


def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Plot comment impact data from CSV.')

    # Default values reflect the behavior used on the pub
    parser.add_argument('csv_path', type=str, nargs='?', default='data/comment_impacts.csv',
                        help='Path to the CSV file (default: data/comment_impacts.csv)')
    parser.add_argument('--grouping', choices=['threshold', 'manual'], default='threshold',
                        help="Method for grouping 'Other' impacts: 'threshold' or 'manual' "
                            "(default: threshold).")
    parser.add_argument('--threshold', type=int, default=10,
                        help="Threshold count for 'Other' grouping "
                            "(only used with --grouping threshold, default: 10).")
    parser.add_argument('--other_impacts', nargs='+',
                        help="List of impacts to group as 'Other' (only used with "
                            "--grouping manual, not used by default).")
    parser.add_argument('--sort_version', choices=['v1', 'v2'], default='v1',
                        help="Version to use for sorting: 'v1' or 'v2' (default: v1).")
    parser.add_argument('--other_position', choices=['end', 'natural'], default='end',
                        help="Position of 'Other' in the order: 'end' or 'natural' (default: end).")
    parser.add_argument('--chart_type', choices=['bar', 'pie'], default='pie',
                        help="Type of chart to create: 'bar' or 'pie' (default: pie).")
    parser.add_argument('--chart_style', choices=['pie', 'donut'], default='donut',
                        help="Style of circular chart (only used with --chart_type pie):"
                            " 'pie' or 'donut' (default: donut).")

    args = parser.parse_args()

    if not os.path.exists(args.csv_path):
        raise FileNotFoundError(f"File not found: {args.csv_path}")

    # Read and process CSV data
    data = process_csv_data(args.csv_path)

    # Handle Impact column - explode and clean up
    expanded_data = data.explode('Impact')
    expanded_data['Impact'] = expanded_data['Impact'].str.strip()
    expanded_data = expanded_data.dropna(subset=['Impact'])
    expanded_data = expanded_data[expanded_data['Impact'] != '']

    # Calculate counts and percentages
    impact_counts = (
        expanded_data.groupby(['Impact', 'Publishing version (from Pub)'])
        .size()
        .reset_index(name='Count')
    )

    total_impacts = impact_counts.groupby('Publishing version (from Pub)')['Count'].transform('sum')
    impact_counts['Percentage'] = impact_counts['Count'] / total_impacts * 100

    # Print statistics before grouping
    print("\n=== Statistics Before Grouping into 'Other' ===")
    print_statistics(impact_counts, data, expanded_data)

    # Grouping "Other" impacts
    impact_counts = group_other_impacts(impact_counts, args.grouping, args.threshold,
                                        args.other_impacts)

    # Recalculate percentages after grouping into "Other"
    impact_counts = (
        impact_counts.groupby(['Impact', 'Publishing version (from Pub)'])
        .agg({'Count': 'sum'})
        .reset_index()
    )
    total_impacts = impact_counts.groupby('Publishing version (from Pub)')['Count'].transform('sum')
    impact_counts['Percentage'] = impact_counts['Count'] / total_impacts * 100

    print("\n=== Statistics After Grouping into 'Other' ===")
    print_statistics(impact_counts, data, expanded_data)

    # Set impact order
    impact_counts = set_impact_order(impact_counts, args.sort_version, args.other_position)

    # Drop any rows where Impact is null
    impact_counts = impact_counts.dropna(subset=['Impact'])

    # Convert Impact column to regular type before pivoting
    impact_counts['Impact'] = impact_counts['Impact'].astype(str)

    # Pivot the DataFrame for plotting
    impact_pivot = impact_counts.pivot(
        index='Impact', columns='Publishing version (from Pub)', values='Percentage'
    ).reset_index()

    # Fill NaN values with 0
    impact_pivot = impact_pivot.fillna(0)

    # Set the categorical ordering
    impact_order = impact_pivot['Impact'].tolist()
    if args.other_position == 'end' and 'Other' in impact_order:
        impact_order.remove('Other')
        impact_order.append('Other')

    impact_pivot['Impact'] = pd.Categorical(
        impact_pivot['Impact'],
        categories=impact_order,
        ordered=True
    )

    # Get unique versions for plotting
    versions = impact_counts['Publishing version (from Pub)'].unique()

    # Create and save the plot
    fig = create_plot(impact_counts, impact_pivot, versions, args.chart_type, args.chart_style)
    # plt.savefig("impact_pie_legend.svg")
    plt.show()


if __name__ == '__main__':
    main()
