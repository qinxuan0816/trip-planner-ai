import os
import json
from datetime import datetime

TRIPS_DIR = "storage/itineraries"


def _clean_messages(messages: list) -> list:
    """
    Convert messages (a mix of dicts and OpenAI objects) into plain,
    saveable dicts. Keeps only the visible conversation, dropping the
    internal tool-calling machinery.
    """
    clean = []
    for m in messages:
        role = m["role"] if isinstance(m, dict) else m.role
        content = m["content"] if isinstance(m, dict) else m.content

        if role == "tool":
            continue                       # tool results are saved as POIs instead
        if role == "assistant" and not content:
            continue                       # skip pure tool-call messages (no text)

        clean.append({"role": role, "content": content})
    return clean


def save_trip(name: str, messages: list, pois: list) -> str:
    """Save a trip (conversation + POIs) to a JSON file. Returns the file path."""
    os.makedirs(TRIPS_DIR, exist_ok=True)   # create the folder if it doesn't exist

    data = {
        "name": name,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "messages": _clean_messages(messages),
        "pois": pois,
    }

    # Build a safe filename from the trip name + a timestamp.
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in name).strip("_")
    path = os.path.join(TRIPS_DIR, f"{safe_name}_{stamp}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return path

def list_trips() -> list[dict]:
    """List all saved trips, newest first. Returns [{name, saved_at, path}, ...]."""
    if not os.path.isdir(TRIPS_DIR):
        return []

    trips = []
    for filename in os.listdir(TRIPS_DIR):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(TRIPS_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            trips.append({
                "name": data.get("name", filename),
                "saved_at": data.get("saved_at", ""),
                "path": path,
            })
        except (json.JSONDecodeError, OSError):
            continue   # skip any corrupted or unreadable file

    # Newest first.
    trips.sort(key=lambda t: t["saved_at"], reverse=True)
    return trips


def load_trip(path: str) -> dict:
    """Load one saved trip from its JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_feedback(path: str, rating: str, comment: str = "") -> None:
    """Attach user feedback (rating + optional comment) to a saved trip file."""
    data = load_trip(path)          # read the existing trip
    data["feedback"] = {
        "rating": rating,           # "up" or "down"
        "comment": comment,
        "at": datetime.now().isoformat(timespec="seconds"),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def collect_feedback_notes() -> list[str]:
    """
    Gather comments from trips the user rated 'down'.
    These become preferences the agent should respect next time.
    """
    notes = []
    for trip in list_trips():
        data = load_trip(trip["path"])
        fb = data.get("feedback")
        if fb and fb.get("rating") == "down" and fb.get("comment"):
            notes.append(fb["comment"])
    return notes