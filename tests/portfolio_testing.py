from urllib.parse import urljoin, urlparse
import pytest
import requests
from bs4 import BeautifulSoup


BASE_URL = "http://localhost:8000/"

PAGES_TO_TEST = ["/","/index.html"]
SKIP_EXTERNAL = True
IGNORE_DOMAINS = ["linkedin.com", "gmail.com", "github.com"]
REQUEST_TIMEOUT = 8


def get_page(path):
    url = urljoin(BASE_URL, path)
    return requests.get(url, timeout=REQUEST_TIMEOUT)


def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute = urljoin(base_url, href)
        links.append((tag.get_text(strip=True) or href, absolute))
    return links


def is_external(url):
    return urlparse(url).netloc not in ("", urlparse(BASE_URL).netloc)


def is_ignored(url):
    domain = urlparse(url).netloc.lower()
    return any(ignored in domain for ignored in IGNORE_DOMAINS)



@pytest.fixture(scope="module")
def page_html():
    """Fetch and cache each page's HTML once, keyed by path."""
    cache = {}

    def _get(path):
        if path not in cache:
            cache[path] = get_page(path)
        return cache[path]

    return _get



@pytest.mark.parametrize("path", PAGES_TO_TEST)
def test_page_returns_200(page_html, path):
    response = page_html(path)
    assert response.status_code == 200, f"{path} returned {response.status_code}, expected 200"


@pytest.mark.parametrize("path", PAGES_TO_TEST)
def test_page_has_title(page_html, path):
    response = page_html(path)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title")
    assert title is not None, f"{path} is missing a <title> tag"
    assert title.get_text(strip=True), f"{path} has an empty <title> tag"


@pytest.mark.parametrize("path", PAGES_TO_TEST)
def test_page_has_body_content(page_html, path):
    response = page_html(path)
    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.find("body")
    assert body is not None, f"{path} is missing a <body> tag"
    assert body.get_text(strip=True), f"{path} has an empty <body> (no visible content)"


@pytest.mark.parametrize("path", PAGES_TO_TEST)
def test_internal_links_resolve(page_html, path):
    page_url = urljoin(BASE_URL, path)
    response = page_html(path)
    links = extract_links(response.text, page_url)

    broken = []
    for text, url in links:
        if is_external(url):
            continue
        try:
            link_response = requests.get(url, timeout=REQUEST_TIMEOUT)
            if link_response.status_code >= 400:
                broken.append(f"'{text}' -> {url} ({link_response.status_code})")
        except requests.RequestException as exc:
            broken.append(f"'{text}' -> {url} (error: {exc})")

    assert not broken, f"Broken internal links on {path}:\n" + "\n".join(broken)


@pytest.mark.skipif(SKIP_EXTERNAL, reason="SKIP_EXTERNAL is set to True")
@pytest.mark.parametrize("path", PAGES_TO_TEST)
def test_external_links_resolve(page_html, path):
    page_url = urljoin(BASE_URL, path)
    response = page_html(path)
    links = extract_links(response.text, page_url)

    broken = []
    for text, url in links:
        if not is_external(url) or is_ignored(url):
            continue
        try:
            link_response = requests.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            if link_response.status_code >= 400:
                link_response = requests.get(url, timeout=REQUEST_TIMEOUT)
            if link_response.status_code >= 400:
                broken.append(f"'{text}' -> {url} ({link_response.status_code})")
        except requests.RequestException as exc:
            broken.append(f"'{text}' -> {url} (error: {exc})")

    assert not broken, f"Broken or unreachable external links on {path}:\n" + "\n".join(broken)