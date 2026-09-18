"""
Bananriti - Phase 1
Download Bangla news articles from Prothom Alo.
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
from datetime import datetime, timedelta, timezone
from tqdm import tqdm

# -------------------------------------------------
# Where our downloaded text will be saved
# -------------------------------------------------
RAW_FOLDER = Path("data/raw")
RAW_FOLDER.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RAW_FOLDER / "raw_corpus.txt"
ARTICLE_URL_FILE = RAW_FOLDER / "article_urls.txt"

# -------------------------------------------------
# Prothom Alo configuration
# -------------------------------------------------
BASE_URL = "https://www.prothomalo.com"
SITEMAP_INDEX_URL = f"{BASE_URL}/sitemap.xml"
SITEMAP_DAYS = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
    )
}

# Keep only article sections
VALID_SECTIONS = [
    "/bangladesh/",
    "/sports/",
    "/technology/",
    "/education/",
    "/world/",
    "/economy/",
    "/entertainment/",
    "/lifestyle/"
]

# Remove non-article pages
INVALID_SECTIONS = [
    "/video/",
    "/photo/",
    "/podcast/",
    "/gallery/",
    "/cartoon/",
    "/opinion/",
    "/search/",
    "/ampstories/"
]

TARGET_SENTENCE_COUNT = 10_000
MIN_SENTENCE_LENGTH = 20
MAX_SENTENCE_LENGTH = 250

BANGLA_CHARACTER_PATTERN = re.compile(r"[\u0980-\u09FF]")
BANGLA_DIGIT_PATTERN = re.compile(r"[0-9০-৯]")
URL_PATTERN = re.compile(r"(?:https?://|www\.)", re.IGNORECASE)

UNWANTED_CONTENT_SELECTORS = [
    "script",
    "style",
    "noscript",
    "figure",
    "figcaption",
    "aside",
    "footer",
    "[class*='advert']",
    "[class*='caption']",
    "[class*='related']",
    "[class*='author']",
    "[class*='share']",
    "[id*='advert']",
    "[id*='caption']",
    "[id*='related']",
    "[id*='author']",
    "[id*='share']"
]

NON_ARTICLE_TEXT_PREFIXES = (
    "আরও পড়ুন",
    "সম্পর্কিত খবর",
    "লেখক:",
    "শেয়ার",
    "share",
    "related"
)


def get_html(url):
    """
    Download one webpage and return BeautifulSoup object.
    """
    response = requests.get(url, headers=HEADERS, timeout=20)

    # Stop if webpage fails (404, 403, etc.)
    response.raise_for_status()

    return BeautifulSoup(response.text, "lxml")


def get_xml(url):
    """
    Download and parse one XML sitemap.
    """

    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    return BeautifulSoup(response.content, "xml")


def get_recent_sitemap_urls(days=SITEMAP_DAYS):
    """
    Return daily sitemap URLs whose date is within the requested time window.
    """

    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days - 1)).date()
    sitemap_index = get_xml(SITEMAP_INDEX_URL)
    sitemap_urls = []

    for sitemap in sitemap_index.find_all("sitemap"):
        loc = sitemap.find("loc")
        if loc is None:
            continue

        sitemap_url = loc.get_text(strip=True)
        match = re.search(r"sitemap-daily-(\d{4}-\d{2}-\d{2})\.xml$", sitemap_url)

        if match is None:
            continue

        sitemap_date = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        if sitemap_date >= cutoff_date:
            sitemap_urls.append(sitemap_url)

    return sorted(sitemap_urls, reverse=True)


def is_valid_article_url(url):
    """
    Return True only for URLs from the selected Prothom Alo article sections.
    """

    return (
        url.startswith(BASE_URL)
        and any(section in url for section in VALID_SECTIONS)
        and not any(section in url for section in INVALID_SECTIONS)
    )


def collect_article_urls(sitemap_urls):
    """
    Read sitemap files and return sorted, unique article URLs.
    """

    all_links = set()
    processed_sitemap_count = 0

    for sitemap_url in tqdm(sitemap_urls, desc="Reading sitemaps"):
        try:
            sitemap = get_xml(sitemap_url)
            processed_sitemap_count += 1

            for url_tag in sitemap.find_all("url"):
                loc = url_tag.find("loc")

                if loc is None:
                    continue

                article_url = loc.get_text(strip=True)
                if is_valid_article_url(article_url):
                    all_links.add(article_url)
        except requests.RequestException as error:
            tqdm.write(f"Skipping sitemap: {sitemap_url} ({error})")

    return sorted(all_links), processed_sitemap_count


def save_article_urls(article_urls):
    """
    Save one article URL per line using UTF-8 encoding.
    """

    content = "\n".join(article_urls)
    if content:
        content += "\n"

    ARTICLE_URL_FILE.write_text(content, encoding="utf-8")


def normalize_whitespace(text):
    """
    Replace repeated whitespace with one space without changing Bangla text.
    """

    return re.sub(r"\s+", " ", text).strip()


def extract_main_bangla_paragraphs(soup):
    """
    Return clean Bangla paragraphs from the main article content only.
    """

    for element in soup.select(", ".join(UNWANTED_CONTENT_SELECTORS)):
        element.decompose()

    article = soup.find("article")
    paragraph_tags = article.find_all("p") if article else []

    if not paragraph_tags:
        paragraph_tags = soup.select("[class*='story-element-text'] p")

    paragraphs = []
    for paragraph in paragraph_tags:
        text = normalize_whitespace(paragraph.get_text(" ", strip=True))
        text_prefix = text.casefold()

        if len(text) <= 40:
            continue

        if not BANGLA_CHARACTER_PATTERN.search(text):
            continue

        if text_prefix.startswith(NON_ARTICLE_TEXT_PREFIXES):
            continue

        paragraphs.append(text)

    return paragraphs


def extract_article_text(url):
    """
    Download one article and return its cleaned Bangla paragraphs as text.
    """

    try:
        soup = get_html(url)
        paragraphs = extract_main_bangla_paragraphs(soup)
        return "\n".join(paragraphs) or None
    except requests.RequestException:
        return None


def split_bangla_sentences(paragraphs):
    """
    Split Bangla paragraphs into sentences at ।, ?, or ! punctuation.
    """

    sentences = []

    for paragraph in paragraphs:
        for sentence in re.split(r"(?<=[।?!])\s*", paragraph):
            sentence = normalize_whitespace(sentence)
            if sentence:
                sentences.append(sentence)

    return sentences


def is_clean_bangla_sentence(sentence):
    """
    Check sentence length, Bangla content, and numeric or URL-heavy noise.
    """

    if not MIN_SENTENCE_LENGTH <= len(sentence) <= MAX_SENTENCE_LENGTH:
        return False

    if URL_PATTERN.search(sentence):
        return False

    visible_characters = [character for character in sentence if not character.isspace()]
    if not visible_characters:
        return False

    bangla_count = sum(
        bool(BANGLA_CHARACTER_PATTERN.fullmatch(character))
        for character in visible_characters
    )
    digit_count = sum(
        bool(BANGLA_DIGIT_PATTERN.fullmatch(character))
        for character in visible_characters
    )

    if bangla_count / len(visible_characters) < 0.40:
        return False

    if digit_count / len(visible_characters) > 0.50:
        return False

    return True


def collect_clean_sentences(article_urls, target_count=TARGET_SENTENCE_COUNT):
    """
    Download articles until the target number of clean sentences is met.
    """

    collected_sentences = []
    articles_visited = 0
    articles_skipped = 0

    for article_url in tqdm(article_urls, desc="Downloading articles"):
        if len(collected_sentences) >= target_count:
            break

        articles_visited += 1

        try:
            soup = get_html(article_url)
            paragraphs = extract_main_bangla_paragraphs(soup)
            clean_sentences = [
                sentence
                for sentence in split_bangla_sentences(paragraphs)
                if is_clean_bangla_sentence(sentence)
            ]
        except requests.RequestException as error:
            articles_skipped += 1
            tqdm.write(f"Skipping article: {article_url} ({error})")
            continue

        if not clean_sentences:
            articles_skipped += 1
            continue

        remaining_count = target_count - len(collected_sentences)
        collected_sentences.extend(clean_sentences[:remaining_count])

    return collected_sentences, articles_visited, articles_skipped


def save_corpus_sentences(sentences):
    """
    Save one clean sentence per line using UTF-8 encoding.
    """

    content = "\n".join(sentences)
    if content:
        content += "\n"

    OUTPUT_FILE.write_text(content, encoding="utf-8")


if __name__ == "__main__":

    sitemap_urls = get_recent_sitemap_urls()
    article_links, processed_sitemap_count = collect_article_urls(sitemap_urls)
    save_article_urls(article_links)
    sentences, articles_visited, articles_skipped = collect_clean_sentences(article_links)
    save_corpus_sentences(sentences)

    print("\nCorpus collection complete")
    print(f"Articles visited: {articles_visited}")
    print(f"Articles skipped: {articles_skipped}")
    print(f"Total sentences collected: {len(sentences)}")
    print(f"Output file path: {OUTPUT_FILE}")
