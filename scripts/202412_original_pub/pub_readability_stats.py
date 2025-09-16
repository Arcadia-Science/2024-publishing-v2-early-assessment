"""
This script takes a research.arcadiascience.com URL (without version number) and scrapes the page
for its main content. It then calculates various readability metrics using scireadability.
"""

import argparse
import codecs
import urllib.parse
import urllib.robotparser

import justext
import requests
import scireadability
from bs4 import BeautifulSoup


def is_allowed_by_robots(url):
    """Checks if the URL is allowed to be crawled based on robots.txt."""
    rp = urllib.robotparser.RobotFileParser()
    robots_url = urllib.parse.urljoin(url, "/robots.txt")
    try:
        print(f"Fetching robots.txt from: {robots_url}")
        response = requests.get(robots_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        print(f"Successfully fetched robots.txt (status code: {response.status_code})")
        rp.parse(response.content.decode("utf-8").splitlines())
        return rp.can_fetch("*", url)
    except Exception as e:
        print(f"Error parsing robots.txt: {e}")
        return False  # Will not scrape if there is an issue


def clean_text(html_content):
    """Extract main content from HTML using justext."""
    print("\n--- Starting text cleaning ---")

    try:
        # Check for and remove BOM
        if html_content.startswith(codecs.BOM_UTF8.decode("utf-8")):
            html_content = html_content[len(codecs.BOM_UTF8) :]

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove the entire section-content div
        comment_section = soup.find("div", class_="section-content")
        if comment_section:
            comment_section.decompose()

        # Remove tables
        for table_div in soup.find_all("div", class_="tableWrapper"):
            table_div.decompose()

        # Remove figures
        for figure in soup.find_all("figure"):
            figure.decompose()

        # Remove specific blockquotes
        for blockquote in soup.find_all("blockquote"):
            if blockquote.find(string="Share your thoughts!"):
                blockquote.decompose()

        # Remove all headers (h1 to h6)
        for header in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            header.decompose()

        # Now, get the modified HTML
        modified_html = str(soup)

        # Extract main content using justext
        paragraphs = justext.justext(modified_html, justext.get_stoplist("English"))

        # Keep only the main content
        content = []
        for paragraph in paragraphs:
            if not paragraph.is_boilerplate:
                content.append(paragraph.text)

        # Join with proper spacing
        text = "\n\n".join(content)

        print(f"Final cleaned text length: {len(text)}")
        print(f"First 100 characters: {text[:100]}...")

        return text

    except Exception as e:
        print(f"Error in text extraction: {str(e)}")
        return ""


def print_readability_metrics(text):
    """Print various readability metrics."""
    print("\n=== Readability Metrics ===")
    print(f"Text length: {len(text)} characters")

    metrics = [
        ("Flesch Reading Ease", scireadability.flesch_reading_ease(text)),
        ("Flesch-Kincaid Grade", scireadability.flesch_kincaid_grade(text)),
        ("SMOG Index", scireadability.smog_index(text)),
        ("Coleman-Liau Index", scireadability.coleman_liau_index(text)),
        (
            "Automated Readability Index",
            scireadability.automated_readability_index(text),
        ),
        (
            "Dale-Chall Readability Score",
            scireadability.dale_chall_readability_score(text),
        ),
        (
            "Readability Consensus",
            scireadability.text_standard(text, float_output=True),
        ),
        ("Word Count", scireadability.lexicon_count(text)),
        ("Sentence Count", scireadability.sentence_count(text)),
        ("Average Syllables per Word", scireadability.avg_syllables_per_word(text)),
    ]

    for metric_name, value in metrics:
        print(f"{metric_name}: {round(value, 2)}")


def process_url(url, delay_seconds=5):
    print(f"\n=== Processing URL: {url} ===")

    if not is_allowed_by_robots(url):
        print(f"Scraping disallowed for {url} by robots.txt. Skipping.")
        return

    try:
        # Fetch webpage
        print("Fetching webpage...")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        print(f"Successfully fetched page (status code: {response.status_code})")

        # Decode the response content to a string
        html_content = response.content.decode("utf-8")

        # Extract and clean text
        clean_content = clean_text(html_content)

        # Print readability metrics
        print_readability_metrics(clean_content)

    except Exception as e:
        print(f"Error processing URL: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate readability metrics for a webpage."
    )
    parser.add_argument("url", help="The URL of the webpage to analyze")

    args = parser.parse_args()
    process_url(args.url)


if __name__ == "__main__":
    main()
