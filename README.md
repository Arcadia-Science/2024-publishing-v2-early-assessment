# Publishing v2.0 early assessment tools

This respository accompanies the Arcadia Science pub, "[Early update on Arcadia publishing 2.0: Scientists are in charge, speed is an issue](https://doi.org/10.57844/arcadia-2a89-51c1)."
It includes raw data and analysis scripts for both the original publication and the September 2025 update.

***

## Overview

This repository contains the data and scripts necessary to replicate the claims in the pub:

- Number of pub team service requests and services ordered by number of requests
- Workdays to publication between v1.0 pubs and v2.0 pubs
- Pub reading ease
- Comment impact analysis and visualization
- Pub feedback form analysis

***

## Repository structure
This repo contains two main directories: `data` and `scripts`. Within these directories, there are subdirectories for the
`202412_original_pub` and the `202509_update` update.

## Scripts

### `scripts/original_pub/calculate_basic_pub_stats.py`

> Note: table 1 in the pub displays 'First time pub onboarding' as a service that has been requested at least two times.
> This script will return '1' for this service, although it has been requested twice. This is because that service can be
> requested independent of a pub.

> Note: although we have eight v2.0 pubs in progress at the time of publication, we have omitted one here because we do not have an accurate kickoff date at this time. This means the script will display summary statistics for seven pubs.

Analyzes basic publication metrics including:
- Version comparison (v1.0 vs v2.0)
- Time to completion
- Flesch Reading Ease scores
- Pub team service requests

### `scripts/original_pub/comment_impacts.py`

> Note: the included `comment_impacts.csv` file is more up-to-date than the one used in the pub, so you may note slight differences in impact distribution.

Visualizes and analyzes comment impacts with:
- Impact categorization
- Version comparison
- Configurable visualization options (pie/donut/bar charts) and multiple grouping methods for impact categories
- Summary statistics

### `scripts/original_pub/feedback_form_basic_stats.py`

> Note: the included `pub_feedback_form.csv` file is more up-to-date than the one used to report in the pub. You may notice a small difference in feedback values.

Processes publication feedback survey responses:
- Response rates by version
- Question-by-question analysis and comparison
- Monthly submission patterns

### `scripts/original_pub/pub_readability_stats.py`

>Note: we used [scireadability](https://github.com/robert-roth/scireadability), a derivative of textstat with more accurate syllable counting for our pubs.

Web scraping tool, specifically for Arcadia Science pubs, for readability analysis:
- Multiple readability metrics (Flesch, SMOG, Coleman-Liau, etc.)
- Content extraction and cleaning

### `scripts/update_202509/calculate_basic_pub_stats.py`

Analyzes basic pub stats, compares them to v1.0 and to the initial v2.0 pubs that we reported on in the original pub, and prints them. Tests include:
- Calculates and prints descriptive stats (n, mean/SD, 95% CI for mean, median/IQR)
- Performs Welch's t-test and a rank-sum robustness check (Mann-Whitney U)
- Calculates and prints effect sizes (Hedges' g)

These tests are applied to:

- Time to publication
- Flesch Reading Ease

### `scripts/update_202509/feedback_form_basic_stats.py`
Analyzes responses from the feedback form to compare reader perceptions of v1.0 and v2.0 pubs. The script prints contingency tables (counts and percentages) and test results for each question. Tests include:

- Chi-squared (χ2) test of independence for each question
- Applies two methods of multiple testing correction to adjust p-values:
  - Bonferroni correction (family-wise error rate)
  - Benjamini-Hochberg (false discovery rate)

These tests are applied to reader responses for:
- Straightforwardness/clarity of the pub
- Potential usefulness in the reader's own work
- Ability to find information needed for reuse
- Whether evidence supports the claims made

***

## Data files

There are two subdirectories within `data`. The subdirectory `original_pub` contains the data
used in the original analysis for "Early update on Arcadia publishing 2.0: Scientists are in charge, speed is an issue." 
The subdirectory `update_202509` contains the data used to update the pub and report additional results from the subsequent eight
months of publishing v2.0. The CSVs for the original pub were exported in December 2024, and the CSVs for the update were exported in September 2025.

### `basic_pub_stats.csv`

> Note that we originally used scireadability 0.6.4, which was yanked. Some Flesch Reading Ease scores were recalculated with 
> 2.0.1, which shifted the values. This does not affect our takeaways.

Basic pub information, including:
- Pub status
- Workdays in progress
- Flesch Reading Ease scores
- Number of pub team requests (this is omitted in `202509_update`)
- List of pub team requests (this is omitted in `202509_update`)

### `comment_impacts.csv`
> This file is omitted in update_202509 as we no longer require employees to rate all comments by impact

Comment data containing:
- Impact categorization
- Publishing version (from the pub where the comment was left)
- If the comment was submitted by a job applicant ("checked" = True, null = False)

### `pub_feedback_form_responses.csv`

Survey response data including:
- Ratings for all form responses
- Submission time
- Publishing version (from the pub where the form was submitted)

***

## Requirements

Create a Python 3.12 virtual environment using your preferred method. For example, using `mamba`:

```sh
mamba create -n 2024-publishing-v2-assessment python=3.12
mamba activate 2024-publishing-v2-assessment
```

Then, install the required packages:

```sh
pip install -r requirements.txt
```

***

## Usage

Most of the scripts are designed to work with the provided CSV files as shown below. The scripts either hardcode the relevant data files they use, or those files are the default. Configurable options are described in docstrings in the specific scripts.

>Scripts related to the 2025-09 update run with hardcoded CSV files by default.

```sh
python scripts/202412_original_pub/calculate_basic_pub_stats.py data/202412_original_pub/basic_pub_stats.csv
python scripts/202412_original_pub/comment_impacts.py data/202412_original_pub/comment_impacts.csv
python scripts/202412_original_pub/feedback_form_basic_stats.py data/202412_original_pub/pub_feedback_form_responses.csv
```

The `pub_readability_stats.py` script requires a URL to an Arcadia Science pub. 
These URLs have the format `https://research.arcadiascience.com/pub/<pub-slug>`.

For example:

```sh
python scripts/pub_readability_stats.py https://research.arcadiascience.com/pub/method-circular-dna-id
```
