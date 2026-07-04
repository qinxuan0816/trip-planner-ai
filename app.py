import streamlit as st

from agent.core import run_agent
from agent.prompts import SYSTEM_PROMPT
from ui.map_view import extract_pois, build_map
from persistence import save_trip, list_trips, load_trip, save_feedback, collect_feedback_notes

st.title("🗺️ Trip Planner AI")
st.write("Tell me where you're going, and I'll plan something using real map data.")

# --- Initialize memory ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "pois" not in st.session_state:
    st.session_state.pois = []
if "current_trip_path" not in st.session_state:
    st.session_state.current_trip_path = None

# --- Show the conversation so far ---
for msg in st.session_state.messages:
    role = msg["role"] if isinstance(msg, dict) else msg.role
    content = msg["content"] if isinstance(msg, dict) else msg.content
    if role == "user":
        st.chat_message("user").markdown(content)
    elif role == "assistant" and content:
        st.chat_message("assistant").markdown(content)

# --- Chat input ---
user_request = st.chat_input("e.g. Plan an afternoon in Kyoto, then: add a park")

if user_request:
    st.session_state.messages.append({"role": "user", "content": user_request})
    st.chat_message("user").markdown(user_request)

    with st.spinner("Planning..."):
        # Inject past negative feedback as preferences before planning.
        notes = collect_feedback_notes()
        if notes:
            preference_text = (
                "\n\nThe user has previously given this feedback — "
                "respect these preferences:\n- " + "\n- ".join(notes)
            )
            # Append the preferences to the system message (the first message).
            st.session_state.messages[0]["content"] = SYSTEM_PROMPT + preference_text

        st.session_state.messages = run_agent(st.session_state.messages)
        st.session_state.pois = extract_pois(st.session_state.messages)

    reply = st.session_state.messages[-1]
    content = reply["content"] if isinstance(reply, dict) else reply.content
    st.chat_message("assistant").markdown(content)

# --- Map ---
if st.session_state.pois:
    st.subheader("📍 Places on the map")
    deck = build_map(st.session_state.pois)
    st.pydeck_chart(deck)

# --- Sidebar: save & load ---
with st.sidebar:
    st.header("💾 Save this trip")
    trip_name = st.text_input("Trip name", placeholder="e.g. Kyoto afternoon")
    if st.button("Save trip", key="save_btn"):
        if len(st.session_state.messages) <= 1:
            st.warning("Plan a trip first, then save it.")
        elif not trip_name:
            st.warning("Please give the trip a name.")
        else:
            path = save_trip(trip_name, st.session_state.messages, st.session_state.pois)
            st.success(f"Saved to {path}")

    st.divider()

    st.header("📂 Load a saved trip")
    trips = list_trips()
    if not trips:
        st.caption("No saved trips yet.")
    else:
        options = {f"{t['name']}  ({t['saved_at']})": t["path"] for t in trips}
        choice = st.selectbox("Choose a trip", list(options.keys()))
        if st.button("Load trip", key="load_btn"):
            data = load_trip(options[choice])
            st.session_state.messages = (
                [{"role": "system", "content": SYSTEM_PROMPT}] + data["messages"]
            )
            st.session_state.pois = data["pois"]
            st.session_state.current_trip_path = options[choice]
            st.rerun()

# --- Feedback on the currently loaded trip ---
if st.session_state.current_trip_path:
    st.divider()
    st.subheader("💬 How was this itinerary?")

    comment = st.text_input("Optional comment", key="fb_comment")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Good", key="fb_up"):
            save_feedback(st.session_state.current_trip_path, "up", comment)
            st.success("Thanks! Feedback saved.")
    with col2:
        if st.button("👎 Needs work", key="fb_down"):
            save_feedback(st.session_state.current_trip_path, "down", comment)
            st.success("Thanks! Feedback saved.")