import os
import numpy as np
import faiss
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Reuse the same Gemini client setup, but for embeddings this time.
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

EMBED_MODEL = "gemini-embedding-001"


def embed_texts(texts: list[str]) -> np.ndarray:
    """Turn a list of texts into a NumPy array of embedding vectors."""
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    # Each item in response.data has an .embedding (a list of floats).
    vectors = [item.embedding for item in response.data]
    # FAISS needs a 2D float32 NumPy array.
    return np.array(vectors, dtype="float32")

def build_index(chunks: list[str]):
    """Embed all chunks and build a FAISS index for fast similarity search."""
    vectors = embed_texts(chunks)

    # dimension = length of one embedding vector.
    dimension = vectors.shape[1]

    # IndexFlatL2 = exact nearest-neighbor search using L2 (Euclidean) distance.
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)   # store all chunk vectors in the index

    return index


def retrieve(query: str, chunks: list[str], index, top_k: int = 3) -> list[str]:
    """Find the top_k chunks most relevant to the query."""
    query_vector = embed_texts([query])   # embed the question (as a 1-item list)

    # index.search returns distances and the indices of the closest vectors.
    distances, indices = index.search(query_vector, top_k)

    # Map those indices back to the original text chunks.
    return [chunks[i] for i in indices[0]]

# Cache: city name -> (chunks, faiss_index). Build once, reuse after.
_index_cache = {}


def lookup_travel_info(city: str, question: str, top_k: int = 3) -> str:
    """
    High-level RAG tool: return relevant travel-guide text for a question
    about a city. Builds and caches the index per city.
    """
    from services.wikivoyage import fetch_article, chunk_text
    
    # Build the index only the first time we see this city.
    if city not in _index_cache:
        text = fetch_article(city)
        if not text:
            return f"No travel guide found for {city}."
        chunks = chunk_text(text)
        index = build_index(chunks)
        _index_cache[city] = (chunks, index)

    chunks, index = _index_cache[city]
    results = retrieve(question, chunks, index, top_k=top_k)

    # Join the top chunks into one text block for the model to read.
    return "\n\n".join(results)


if __name__ == "__main__":
    from services.wikivoyage import fetch_article, chunk_text

    print("Fetching and chunking...")
    text = fetch_article("Kyoto")
    chunks = chunk_text(text)

    print(f"Embedding {len(chunks)} chunks (this may take a few seconds)...")
    index = build_index(chunks)

    question = "What are the best temples and gardens to see?"
    print(f"\nQuestion: {question}\n")

    results = retrieve(question, chunks, index)
    for i, chunk in enumerate(results):
        print(f"--- Relevant chunk {i + 1} ---")
        print(chunk[:300])   # first 300 chars of each
        print()