import requests

WIKIVOYAGE_URL = "https://en.wikivoyage.org/w/api.php"
HEADERS = {"User-Agent": "trip-planner/1.0 (serena - learning project)"}


def fetch_article(title: str) -> str | None:
    """Fetch the plain-text Wikivoyage travel guide for a place."""
    params = {
        "action": "query",
        "prop": "extracts",     # ask the TextExtracts extension for content
        "explaintext": 1,       # give us PLAIN TEXT, not HTML or wiki markup
        "redirects": 1,         # follow redirects (e.g. "Kyoto" -> correct page)
        "titles": title,
        "format": "json",
    }

    response = requests.get(WIKIVOYAGE_URL, params=params, headers=HEADERS, timeout=15)
    response.raise_for_status()
    data = response.json()

    # The API nests results under query -> pages -> {page_id: {...}}.
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))   # grab the first (only) page

    # A missing page has no "extract" key.
    extract = page.get("extract")
    if not extract:
        return None
    return extract

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """
    Split a long text into overlapping chunks of ~chunk_size characters.
    Overlap keeps sentences that fall on a boundary intact in at least one chunk.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        # Move the window forward, but step back by `overlap` so chunks overlap.
        start = end - overlap

    return chunks


if __name__ == "__main__":
    text = fetch_article("Kyoto")
    if not text:
        print("No article found.")
    else:
        chunks = chunk_text(text)
        print(f"Article length: {len(text)} characters")
        print(f"Number of chunks: {len(chunks)}\n")

        # Show the first two chunks to see the content and the overlap.
        print("--- Chunk 0 ---")
        print(chunks[0])
        print("\n--- Chunk 1 ---")
        print(chunks[1])