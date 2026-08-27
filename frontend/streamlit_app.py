import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000/summarize"

st.set_page_config(page_title="AI Meeting Notes Summarizer", page_icon="📝")
st.title("AI Meeting Notes Summarizer")
st.caption("Paste your notes, summarize them, and download the results.")

if "result" not in st.session_state:
    st.session_state.result = None

notes = st.text_area(
    "Meeting notes",
    height=220,
    placeholder="Paste your meeting notes here…",
)

if st.button("Summarize", type="primary"):
    if not notes.strip():
        st.error("Please paste some meeting notes before summarizing.")
        st.session_state.result = None
    else:
        try:
            response = requests.post(
                BACKEND_URL,
                json={"notes": notes},
                timeout=60,
            )
            response.raise_for_status()
            st.session_state.result = response.json()
        except requests.RequestException as exc:
            st.error(f"Could not reach the summarizer: {exc}")
            st.session_state.result = None

result = st.session_state.result
if result:
    st.subheader("Summary")
    for bullet in result.get("summary", []):
        st.markdown(f"- {bullet}")

    st.subheader("Action items")
    action_items = [
        {
            "task": item.get("task", ""),
            "owner": item.get("owner") or "—",
        }
        for item in result.get("action_items", [])
    ]
    st.table(action_items)

    lines = ["Summary"]
    for bullet in result.get("summary", []):
        lines.append(f"- {bullet}")
    lines.extend(["", "Action items"])
    for item in result.get("action_items", []):
        owner = item.get("owner") or "Unassigned"
        lines.append(f"- {item.get('task', '')} ({owner})")
    download_text = "\n".join(lines) + "\n"

    st.download_button(
        "Download as .txt",
        data=download_text,
        file_name="meeting_summary.txt",
        mime="text/plain",
    )
