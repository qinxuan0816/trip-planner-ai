import time
import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "trip-planner/1.0 (serena - learning project)"}

# tourism tags we DON'T want in an itinerary (they're lodging, not sights).
EXCLUDED_TOURISM = {"hotel", "hostel", "motel", "guest_house", "apartment"}


def search_pois(lat: float, lon: float, radius: int = 1500, max_retries: int = 3):
    """
    Find tourism POIs within `radius` meters of (lat, lon) using Overpass.
    Returns the raw JSON for now. Retries on temporary server errors (5xx).
    """
    query = f"""
    [out:json][timeout:25];
    (
      node["tourism"](around:{radius}, {lat}, {lon});
      node["amenity"~"restaurant|cafe"](around:{radius}, {lat}, {lon});
    );
    out body 30;
    """

    for attempt in range(max_retries):
        try:
            response = requests.post(
                OVERPASS_URL, data={"data": query}, headers=HEADERS, timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return _parse_pois(data)

        except requests.exceptions.RequestException as e:
            # 504 / timeouts / network errors are temporary — wait and retry.
            wait = 2 ** attempt  # 1s, 2s, 4s
            print(f"Attempt {attempt + 1} failed ({e}). Retrying in {wait}s...")
            time.sleep(wait)

    print(f"Overpass request failed after {max_retries} attempts.")
    return None


def _parse_pois(data: dict) -> list[dict]:
    """
    Turn raw Overpass JSON into a clean list of POIs.
    - Skips nameless nodes.
    - Skips lodging (hotels, hostels, etc.).
    - Labels each POI as "sight" or "food".
    """
    pois = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name")

        if not name:
            continue  # skip nameless nodes

        tourism = tags.get("tourism")
        amenity = tags.get("amenity")

        # Skip lodging — we want places to visit, not places to sleep.
        if tourism in EXCLUDED_TOURISM:
            continue

        # Decide a simple, user-friendly category.
        if amenity in ("restaurant", "cafe"):
            kind = "food"
        else:
            kind = "sight"

        pois.append({
            "name": name,
            "kind": kind,                 # "sight" or "food"
            "detail": tourism or amenity,  # e.g. "museum", "restaurant"
            "lat": element.get("lat"),
            "lon": element.get("lon"),
        })
    return pois

if __name__ == "__main__":
    results = search_pois(35.0115754, 135.7681441)
    if results:
        print(f"Found {len(results)} POIs:")
        for poi in results:
            print(f"  [{poi['kind']:5}] {poi['name']} ({poi['detail']})")