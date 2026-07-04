from services.geocoding import geocode_city
from services.poi import search_pois
from services.rag import lookup_travel_info

# JSON schema describing our tools to the model.
# The model reads these to decide WHICH tool to call and WHAT arguments to pass.
# It never sees our Python code — only these descriptions.

GEOCODE_TOOL = {
    "type": "function",
    "function": {
        "name": "geocode_city",
        "description": (
            "Convert a city or place name into geographic coordinates "
            "(latitude and longitude). Call this first whenever you need "
            "to know where a place is located."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city or place name, e.g. 'Kyoto, Japan'.",
                },
            },
            "required": ["city"],
        },
    },
}

# JSON schema describing our tools to the model.
# The model reads these to decide WHICH tool to call and WHAT arguments to pass.
# It never sees our Python code — only these descriptions.

GEOCODE_TOOL = {
    "type": "function",
    "function": {
        "name": "geocode_city",
        "description": (
            "Convert a city or place name into geographic coordinates "
            "(latitude and longitude). Call this first whenever you need "
            "to know where a place is located."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city or place name, e.g. 'Kyoto, Japan'.",
                },
            },
            "required": ["city"],
        },
    },
}

POI_TOOL = {
    "type": "function",
    "function": {
        "name": "search_pois",
        "description": (
            "Find points of interest (sights and food) near a location. "
            "Requires latitude and longitude, so call geocode_city FIRST "
            "to get the coordinates, then pass them into this tool."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {
                    "type": "number",
                    "description": "Latitude of the location center.",
                },
                "lon": {
                    "type": "number",
                    "description": "Longitude of the location center.",
                },
                "radius": {
                    "type": "number",
                    "description": "Search radius in meters. Optional, defaults to 1500.",
                },
            },
            "required": ["lat", "lon"],
        },
    },
}

TRAVEL_INFO_TOOL = {
    "type": "function",
    "function": {
        "name": "lookup_travel_info",
        "description": (
            "Look up background travel-guide information about a place — "
            "history, culture, what a district is like, whether something is "
            "worth visiting. Use this when the user asks 'why', 'what's it "
            "like', or wants context beyond just a list of place names."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city the question is about, e.g. 'Kyoto'.",
                },
                "question": {
                    "type": "string",
                    "description": "What the user wants to know about the city.",
                },
            },
            "required": ["city", "question"],
        },
    },
}

# All tools we expose to the model, collected in one list.

TOOLS = [GEOCODE_TOOL, POI_TOOL, TRAVEL_INFO_TOOL]

TOOL_FUNCTIONS = {
    "geocode_city": geocode_city,
    "search_pois": search_pois,
    "lookup_travel_info": lookup_travel_info,
}