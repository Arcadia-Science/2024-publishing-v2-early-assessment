"""
Analyzes publication statistics from included CSV data, basic_pub_stats.csv

Metrics analyzed:
- Publication completion rates and timelines
- Workdays in progress statistics (mean, median, std) by version
- Flesch Reading Ease
- Publication team service requests and types
- Version comparison (v1.0 vs v2.0)

Notes:
- Flesch scores are stored as percentage strings for internal display at Arcadia (e.g., "42.5%")
- NaN handling:
  - Uses numpy.nanmedian/nanmean for workday calculations
  - Filters NaN values from FRE before analysis
- Service request analysis only includes non-empty request fields
- Histograms are generated for workday distributions but not saved by default

CSV Requirements:
- Must contain columns:
  - Status
  - Flesch reading ease version of record
  - Publishing version
  - Workdays in progress
  - Total number of pub team requests
  - Pub team request types

Status values recognized:
- "🔔 Published 🔔"
- "Complete — internal"
- "Service(s) in progress"
- "No services requested"
"""

import pandas as pd
import sys
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import arcadia_pycolor as apc

# Set up Arcadia pycolor
apc.mpl.setup()


def analyze_service_types(df):
    # Get all service types across all publications
    service_counts = Counter()

    # Process each row's services
    for services in df['Pub team request types'].dropna():
        if isinstance(services, str) and services.strip():

            # Split by semicolon and remove any leading/trailing whitespace
            unique_services = set(service.strip() for service in services.split(';'))

            # Update counter with unique services from this pub
            service_counts.update(unique_services)

    # Sort by count (most to least frequent)
    sorted_services = sorted(service_counts.items(), key=lambda x: (-x[1], x[0]))

    print("\nService request frequencies:")
    print("-" * 50)
    for service, count in sorted_services:
        print(f"{service}: {count}")


def analyze_publications(csv_path):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)

        # Define completion status
        completed_statuses = ['🔔 Published 🔔', 'Complete — internal']

        # Create helper boolean columns
        df['is_completed'] = df['Status'].isin(completed_statuses)
        df['is_published'] = df['Status'] == '🔔 Published 🔔'

        # Convert Flesch reading ease from percentage string to float, keeping NaN values
        df['Flesch reading ease version of record'] = df[
            'Flesch reading ease version of record'].str.rstrip('%').astype('float')

        # Calculate v1.0 statistics
        v1_df = df[df['Publishing version'] == 'v1.0']
        v1_completed = len(v1_df[v1_df['is_completed']])
        v1_published = len(v1_df[v1_df['is_published']])
        v1_completed_workdays = v1_df[v1_df['is_completed']]['Workdays in progress']
        v1_workdays_median = float(
            np.nanmedian(v1_completed_workdays)) if not v1_completed_workdays.empty else np.nan
        v1_workdays_mean = float(
            np.nanmean(v1_completed_workdays)) if not v1_completed_workdays.empty else np.nan
        v1_workdays_std = float(
            np.nanstd(v1_completed_workdays)) if not v1_completed_workdays.empty else np.nan

        # Calculate v1.0 Flesch reading ease statistics (only for non-empty values)
        v1_flesch = v1_df[v1_df['is_published']]['Flesch reading ease version of record'].dropna()
        v1_flesch_median = float(np.median(v1_flesch)) if not v1_flesch.empty else np.nan
        v1_flesch_mean = float(np.mean(v1_flesch)) if not v1_flesch.empty else np.nan
        v1_flesch_std = float(np.std(v1_flesch)) if not v1_flesch.empty else np.nan
        v1_flesch_min = float(np.min(v1_flesch)) if not v1_flesch.empty else np.nan
        v1_flesch_max = float(np.max(v1_flesch)) if not v1_flesch.empty else np.nan

        # Calculate v2.0 statistics
        v2_df = df[df['Publishing version'] == 'v2.0']
        v2_completed = len(v2_df[v2_df['is_completed']])
        v2_published = len(v2_df[v2_df['is_published']])
        v2_in_progress = len(v2_df[~v2_df['is_completed']])

        # Calculate v2.0 workday statistics
        v2_completed_workdays = v2_df[v2_df['is_completed']]['Workdays in progress']
        v2_workdays_completed_median = float(
            np.nanmedian(v2_completed_workdays)) if not v2_completed_workdays.empty else np.nan
        v2_workdays_completed_mean = float(
            np.nanmean(v2_completed_workdays)) if not v2_completed_workdays.empty else np.nan
        v2_workdays_completed_std = float(
            np.nanstd(v2_completed_workdays)) if not v2_completed_workdays.empty else np.nan

        # Calculate v2.0 Flesch reading ease statistics (only for non-empty values)
        v2_flesch = v2_df[v2_df['is_published']]['Flesch reading ease version of record'].dropna()
        v2_flesch_median = float(np.median(v2_flesch)) if not v2_flesch.empty else np.nan
        v2_flesch_mean = float(np.mean(v2_flesch)) if not v2_flesch.empty else np.nan
        v2_flesch_std = float(np.std(v2_flesch)) if not v2_flesch.empty else np.nan
        v2_flesch_min = float(np.min(v2_flesch)) if not v2_flesch.empty else np.nan
        v2_flesch_max = float(np.max(v2_flesch)) if not v2_flesch.empty else np.nan

        v2_in_progress_workdays = v2_df[~v2_df['is_completed']]['Workdays in progress']
        v2_workdays_in_progress_median = float(
            np.nanmedian(v2_in_progress_workdays)) if not v2_in_progress_workdays.empty else np.nan
        v2_workdays_in_progress_mean = float(
            np.nanmean(v2_in_progress_workdays)) if not v2_in_progress_workdays.empty else np.nan
        v2_workdays_in_progress_std = float(
            np.nanstd(v2_in_progress_workdays)) if not v2_in_progress_workdays.empty else np.nan

        # Calculate v2.0 request statistics - Overall
        v2_requests = v2_df['Total number of pub team requests']
        v2_requests_median = float(np.nanmedian(v2_requests)) if not v2_requests.empty else np.nan
        v2_requests_mean = float(np.nanmean(v2_requests)) if not v2_requests.empty else np.nan
        v2_requests_min = int(np.nanmin(v2_requests)) if not v2_requests.empty else np.nan
        v2_requests_max = int(np.nanmax(v2_requests)) if not v2_requests.empty else np.nan
        v2_requests_std = float(np.nanstd(v2_requests)) if not v2_requests.empty else np.nan

        # Calculate v2.0 request statistics - Completed Pubs
        v2_requests_completed = v2_df[v2_df['is_completed']]['Total number of pub team requests']
        v2_requests_completed_median = float(
            np.nanmedian(v2_requests_completed)) if not v2_requests_completed.empty else np.nan
        v2_requests_completed_mean = float(
            np.nanmean(v2_requests_completed)) if not v2_requests_completed.empty else np.nan
        v2_requests_completed_min = int(
            np.nanmin(v2_requests_completed)) if not v2_requests_completed.empty else np.nan
        v2_requests_completed_max = int(
            np.nanmax(v2_requests_completed)) if not v2_requests_completed.empty else np.nan
        v2_requests_completed_std = float(
            np.nanstd(v2_requests_completed)) if not v2_requests_completed.empty else np.nan

        # Calculate v2.0 request statistics - Incomplete Pubs
        v2_requests_incomplete = v2_df[~v2_df['is_completed']]['Total number of pub team requests']
        v2_requests_incomplete_median = float(
            np.nanmedian(v2_requests_incomplete)) if not v2_requests_incomplete.empty else np.nan
        v2_requests_incomplete_mean = float(
            np.nanmean(v2_requests_incomplete)) if not v2_requests_incomplete.empty else np.nan
        v2_requests_incomplete_min = int(
            np.nanmin(v2_requests_incomplete)) if not v2_requests_incomplete.empty else np.nan
        v2_requests_incomplete_max = int(
            np.nanmax(v2_requests_incomplete)) if not v2_requests_incomplete.empty else np.nan
        v2_requests_incomplete_std = float(
            np.nanstd(v2_requests_incomplete)) if not v2_requests_incomplete.empty else np.nan

        # Print results
        print("Publication Statistics:")
        print("-" * 50)
        print(f"Total number of v1.0 pubs completed: {v1_completed}")
        print(f"Total number of v1.0 released publicly: {v1_published}")
        print(f"Total number of v2.0 pubs completed: {v2_completed}")
        print(f"Total number of v2.0 pubs released publicly: {v2_published}")
        print(f"Total number of v2.0 pubs in progress: {v2_in_progress}")
        print(f"Median workdays to completion, v1.0: {v1_workdays_median:.1f}")
        print(f"Mean workdays to completion, v1.0: {v1_workdays_mean:.1f}")
        print(f"Standard deviation of workdays to completion, v1.0: {v1_workdays_std:.1f}")
        print(
            f"Median workdays to completion, v2.0: {v2_workdays_completed_median:.1f} "
            f"({(v2_workdays_completed_median - v1_workdays_median):+.1f})")
        print(
            f"Mean workdays to completion, v2.0: {v2_workdays_completed_mean:.1f} "
            f"({(v2_workdays_completed_mean - v1_workdays_mean):+.1f})")
        print(
            f"Standard deviation of workdays to completion, v2.0: "
            f"{v2_workdays_completed_std:.1f} "
            f"({(v2_workdays_completed_std - v1_workdays_std):+.1f})")
        print(
            f"Median workdays in progress for incomplete pubs, v2.0: "
            f"{v2_workdays_in_progress_median:.1f}")
        print(
            f"Mean workdays in progress for incomplete pubs, v2.0: "
            f"{v2_workdays_in_progress_mean:.1f}")
        print(
            f"Standard deviation of workdays in progress for incomplete pubs, v2.0: "
            f"{v2_workdays_in_progress_std:.1f}")

        print("\nFlesch Reading Ease Statistics v1.0:")
        print("-" * 50)
        print(f"Median Flesch reading ease, v1.0: {v1_flesch_median:.1f}")
        print(f"Mean Flesch reading ease, v1.0: {v1_flesch_mean:.1f}")
        print(f"Min Flesch reading ease, v1.0: {v1_flesch_min:.1f}")
        print(f"Max Flesch reading ease, v1.0: {v1_flesch_max:.1f}")
        print(f"Standard deviation of Flesch reading ease, v1.0: {v1_flesch_std:.1f}")

        print("\nFlesch Reading Ease Statistics v2.0 (with change from v1.0):")
        print("-" * 50)
        print(
            f"Median Flesch reading ease, v2.0: {v2_flesch_median:.1f} "
            f"({(v2_flesch_median - v1_flesch_median):+.1f})")
        print(
            f"Mean Flesch reading ease, v2.0: {v2_flesch_mean:.1f} "
            f"({(v2_flesch_mean - v1_flesch_mean):+.1f})")
        print(
            f"Min Flesch reading ease, v2.0: {v2_flesch_min:.1f} "
            f"({(v2_flesch_min - v1_flesch_min):+.1f})")
        print(
            f"Max Flesch reading ease, v2.0: {v2_flesch_max:.1f} "
            f"({(v2_flesch_max - v1_flesch_max):+.1f})")
        print(
            f"Standard deviation of Flesch reading ease, v2.0: {v2_flesch_std:.1f} "
            f"({(v2_flesch_std - v1_flesch_std):+.1f})")

        print(f"\nRequests Statistics v2.0 - Overall:")
        print("-" * 50)
        print(f"Median number of pub team requests, v2.0: {v2_requests_median:.1f}")
        print(f"Mean number of pub team requests, v2.0: {v2_requests_mean:.1f}")
        print(f"Min number of pub team requests, v2.0: {v2_requests_min}")
        print(f"Max number of pub team requests, v2.0: {v2_requests_max}")
        print(f"Standard deviation of pub team requests, v2.0: {v2_requests_std:.1f}")

        print(f"\nRequests Statistics v2.0 - Completed Pubs:")
        print("-" * 50)
        print(
            f"Median number of pub team requests, v2.0 (completed): "
            f"{v2_requests_completed_median:.1f}")
        print(
            f"Mean number of pub team requests, v2.0 (completed): "
            f"{v2_requests_completed_mean:.1f}")
        print(f"Min number of pub team requests, v2.0 (completed): "
              f"{v2_requests_completed_min}")
        print(f"Max number of pub team requests, v2.0 (completed): "
              f"{v2_requests_completed_max}")
        print(
            f"Standard deviation of pub team requests, v2.0 (completed): "
            f"{v2_requests_completed_std:.1f}")

        print(f"\nRequests Statistics v2.0 - Incomplete Pubs:")
        print("-" * 50)
        print(
            f"Median number of pub team requests, v2.0 (incomplete): "
            f"{v2_requests_incomplete_median:.1f}")
        print(
            f"Mean number of pub team requests, v2.0 (incomplete): "
            f"{v2_requests_incomplete_mean:.1f}")
        print(f"Min number of pub team requests, v2.0 (incomplete): "
              f"{v2_requests_incomplete_min}")
        print(f"Max number of pub team requests, v2.0 (incomplete): "
              f"{v2_requests_incomplete_max}")
        print(
            f"Standard deviation of pub team requests, v2.0 (incomplete): "
            f"{v2_requests_incomplete_std:.1f}")

        # Analyze service types
        analyze_service_types(df)

        # --- Generate Histograms ---
        plt.figure(figsize=(10, 5))

        # Histogram for v1.0 workdays to completion
        plt.subplot(1, 2, 1)
        plt.hist(v1_completed_workdays.dropna(), bins=10, edgecolor='black')
        plt.title('Workdays to Completion (v1.0)')
        plt.xlabel('Workdays')
        plt.ylabel('Number of Publications')

        # Histogram for v2.0 workdays to completion
        plt.subplot(1, 2, 2)
        plt.hist(v2_completed_workdays.dropna(), bins=5, edgecolor='black')
        plt.title('Workdays to Completion (v2.0)')
        plt.xlabel('Workdays')
        plt.ylabel('Number of Publications')

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error processing: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else "data/basic_pub_stats.csv"
    analyze_publications(filepath)
