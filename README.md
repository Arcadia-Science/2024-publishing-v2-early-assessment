# Publishing v2.0 early assessment tools

This respository accompanies the Arcadia Science pub, "[Early update on Arcadia publishing 2.0: Scientists are in charge, speed is an issue](https://doi.org/10.57844/arcadia-2a89-51c1)."
It contains the raw data as well as the scripts that we used to analyze and visualize this data.

***

## Overview

This repository contains the data and scripts necessary to replicate the claims in the pub:

- Number of pub team service requests and services ordered by number of requests
- Workdays to publication between v1.0 pubs and v2.0 pubs
- Pub reading ease
- Comment impact analysis and visualization
- Pub feedback form analysis

***

## Scripts

### `calculate_basic_pub_stats.py`

> Note: table 1 in the pub displays 'First time pub onboarding' as a service that has been requested at least two times.
> This script will return '1' for this service, although it has been requested twice. This is because that service can be
> requested independent of a pub.

> Note: although we have eight v2.0 pubs in progress at the time of publication, we have omitted it here because we do not have an accurate kickoff date at this time. This means the script will display summary statistics for seven pubs.

Analyzes basic publication metrics including:
- Version comparison (v1.0 vs v2.0)
- Time to completion
- Flesch Reading Ease scores
- Pub team service requests

### `comment_impacts.py`

> Note: the included `comment_impacts.csv` file is more up-to-date than the one used in the pub, so you may note slight differences in impact distribution.

Visualizes and analyzes comment impacts with:
- Impact categorization
- Version comparison
- Configurable visualization options (pie/donut/bar charts) and multiple grouping methods for impact categories
- Summary statistics

### `feedback_form_basic_stats.py`

> Note: the included `pub_feedback_form.csv` file is more up-to-date than the one used to report in the pub. You may notice a small difference in feedback values.

Processes publication feedback survey responses:
- Response rates by version
- Question-by-question analysis and comparison
- Monthly submission patterns

### `pub_readability_stats.py`

>Note: we used [scireadability](https://github.com/robert-roth/scireadability), a derivative of textstat with more accurate syllable counting for our pubs.

Web scraping tool, specifically for Arcadia Science pubs, for readability analysis:
- Multiple readability metrics (Flesch, SMOG, Coleman-Liau, etc.)
- Content extraction and cleaning

***

## Data Files

### `basic_pub_stats.csv`

Basic pub information, including:
- Pub status
- Workdays in progress
- Flesch Reading Ease scores
- Number of pub team requests
- List of pub team requests

### `comment_impacts.csv`

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

Most of the scripts are designed to work with the provided CSV files as shown below. Configurable options are described in docstrings in the specific scripts.

```sh
python scripts/calculate_basic_pub_stats.py data/basic_pub_stats.csv
python scripts/comment_impacts.py data/comment_impacts.csv
python scripts/feedback_form_basic_stats.py data/pub_feedback_form_responses.csv
```

The `pub_readability_stats.py` script requires a URL to an Arcadia Science pub. 
These URLs have the format `https://research.arcadiascience.com/pub/<pub-slug>`. 

For example:

```sh
python scripts/pub_readability_stats.py https://research.arcadiascience.com/pub/method-circular-dna-id
```
