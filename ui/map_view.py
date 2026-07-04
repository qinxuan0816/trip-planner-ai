import json


def extract_pois(messages: list) -> list[dict]:
    """
    Scan the conversation history and pull out all POIs (with coordinates)
    returned by the search_pois tool. Returns a flat list of POI dicts.
    """
    pois = []
    for msg in messages:
        # Tool results are stored as dicts with role == "tool".
        role = msg["role"] if isinstance(msg, dict) else getattr(msg, "role", None)
        if role != "tool":
            continue

        content = msg["content"] if isinstance(msg, dict) else msg.content
        try:
            data = json.loads(content)  # the tool result was stored as JSON text
        except (json.JSONDecodeError, TypeError):
            continue

        # search_pois returns a LIST of POIs; geocode_city returns a dict.
        # We only want the list results that contain lat/lon.
        if isinstance(data, list):
            for poi in data:
                if isinstance(poi, dict) and poi.get("lat") and poi.get("lon"):
                    pois.append(poi)
    return pois

import pydeck as pdk


def build_map(pois: list[dict]):
    """Build a PyDeck map with a pin for each POI. Returns None if no POIs."""
    if not pois:
        return None

    # Center the map on the average location of all POIs.
    avg_lat = sum(p["lat"] for p in pois) / len(pois)
    avg_lon = sum(p["lon"] for p in pois) / len(pois)

    # A ScatterplotLayer draws a colored dot at each coordinate.
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=pois,
        get_position=["lon", "lat"],   # note: PyDeck wants [lon, lat] order!
        get_radius=60,
        get_fill_color=[220, 50, 50],  # red dots
        pickable=True,                 # lets users hover to see the name
    )

    view = pdk.ViewState(latitude=avg_lat, longitude=avg_lon, zoom=13)

    # tooltip shows the POI name when hovering over a dot.
    return pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={"text": "{name}"},
    )