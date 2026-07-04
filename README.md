# 🗺️ Trip Planner AI

An agentic AI trip-planning application that generates grounded, real-world
itineraries by autonomously orchestrating multiple tools and live data sources.

Built to explore production AI engineering: tool calling, RAG, external API
integration, state management, and feedback loops.

## What it does

Ask it to plan a trip ("Plan me an afternoon in Kyoto with sights and food"),
and the agent decides on its own which tools to call — geocoding the city,
searching for real points of interest, and retrieving travel-guide context —
then composes an itinerary and plots the locations on an interactive map.

## Key features

- **Autonomous agent loop** — the model decides which tools to call and in what
  order, using OpenAI-compatible function calling. No hardcoded workflow.
- **Real-world data integration** — geocoding via OpenStreetMap Nominatim, live
  points of interest via the Overpass API, with rate limiting and retry/backoff.
- **RAG over travel guides** — fetches Wikivoyage articles, chunks and embeds
  them, and retrieves relevant passages with FAISS for grounded background info.
- **Output grounding** — the agent is constrained to recommend only places that
  actually appear in tool results, preventing hallucinated locations.
- **Interactive UI & map** — a Streamlit chat interface with multi-turn memory
  and a PyDeck map of the itinerary.
- **Persistence & feedback loop** — save/load itineraries to disk; user feedback
  is collected and injected into future planning as preferences.

## Tech stack

Python · Streamlit · OpenAI-compatible API (Gemini) · FAISS · PyDeck ·
OpenStreetMap (Nominatim, Overpass) · Wikivoyage / MediaWiki API

## Architecture

- `services/` — external data tools (geocoding, POI search, RAG retrieval)
- `agent/` — the tool-calling loop, tool schemas, and system prompt
- `ui/` — map rendering and feedback components
- `app.py` — Streamlit entry point
- `persistence.py` — saving, loading, and feedback storage

## Running locally

1. Clone the repo and create a virtual environment.
2. `pip install -r requirements.txt`
3. Create a `.env` file with your API key: