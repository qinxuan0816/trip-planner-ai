import time
import requests

HEADERS = {"User-Agent": "trip-planner/1.0 (serena - learning project)"}
SEARCH_URL = "https://nominatim.openstreetmap.org/search"

# Nominatim allows at most 1 request per second.
MIN_INTERVAL = 1.0  # seconds between requests
_last_request_time = 0.0  # tracks when we last called the API


def _rate_limit():
    """Sleep if needed so we never exceed 1 request per second."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - elapsed)
    _last_request_time = time.time()

def geocode_city(city: str, max_retries: int = 3):
    """
    Convert a city name into coordinates using Nominatim.
    Returns {"name": str, "lat": float, "lon": float} on success,
    or None if the city is not found.
    Retries on temporary network/server errors with exponential backoff.
    """
    params = {"q": city, "format": "json", "limit": 1}

    for attempt in range(max_retries):
        try:
            # Respect the 1 req/sec rule before every call.
            _rate_limit()

            response = requests.get(
                SEARCH_URL, params=params, headers=HEADERS, timeout=10
            )
            # Raise an error for HTTP failures like 500 (server overloaded).
            response.raise_for_status()

            data = response.json()
            if not data:
                return None  # No match found — this is NOT an error, don't retry.

            result = data[0]
            return {
                "name": result["display_name"],
                "lat": float(result["lat"]),
                "lon": float(result["lon"]),
            }

        except requests.exceptions.RequestException as e:
            # Network error, timeout, or HTTP error. Wait and retry.
            wait = 2 ** attempt  # 1s, then 2s, then 4s — exponential backoff.
            print(f"Attempt {attempt + 1} failed ({e}). Retrying in {wait}s...")
            time.sleep(wait)

    # All retries exhausted.
    print(f"Failed to geocode '{city}' after {max_retries} attempts.")
    return None

if __name__ == "__main__":
    # Case 1: a real city — should return a clean dict.
    print(geocode_city("Kyoto, Japan"))

    # Case 2: nonsense input — should return None, not crash.
    print(geocode_city("asdkfjhqwoeiu"))