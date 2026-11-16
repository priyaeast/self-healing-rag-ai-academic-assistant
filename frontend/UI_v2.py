
import streamlit as st
import requests
import os
import uuid

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Academic Assistant",
    page_icon="🎓",
    layout="wide"
)

# ============================================================
# BACKEND CONFIGURATION
# ============================================================

# Change 8010 if your FastAPI server is running on another port.
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8010"
).rstrip("/")

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🎓 AI Academic Assistant")

    st.markdown("---")

    st.subheader("Ask About")

    st.markdown("""
    - Admissions
    - Fee Structure
    - Faculty Information
    - Academic Calendar
    - Student Policies
    - Scholarships
    - JEE Preparation
    - NEET Preparation
    - Study Material
    - Batch Timings
    """)

    st.markdown("---")

    

    if st.button("🗑️ Clear Chat", use_container_width=True):

        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.conversation_id = str(uuid.uuid4())

        st.rerun()

# ============================================================
# MAIN HEADER
# ============================================================

st.title("🎓 AI Academic Assistant")

st.write(
    "Your intelligent academic assistant powered by "
    "RAG, GraphRAG, Gemini AI and Agentic AI."
)

st.markdown("---")

# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if message["role"] == "assistant" and message.get("sources"):

            with st.expander("📄 View Sources"):

                for source in message["sources"]:
                    st.write(f"• {source}")

            if message.get("approved") is not None:
                st.caption(
                    "Critic Approved: "
                    + str(message["approved"])
                )

            if message.get("trace"):
                st.caption(
                    "Workflow: "
                    + " → ".join(message["trace"])
                )

# ============================================================
# CHAT INPUT
# ============================================================

user_message = st.chat_input("Ask your academic question...")

# ============================================================
# PROCESS USER QUESTION
# ============================================================

if user_message:

    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.write(user_message)

    payload = {
        "message": user_message,
        "user_id": "student",
        "session_id": st.session_state.session_id,
        "conversation_id": st.session_state.conversation_id
    }

    url = f"{BACKEND_URL}/chat"

    # ========================================================
    # BACKEND REQUEST
    # ========================================================

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = requests.post(
                    url,
                    json=payload,
                    timeout=120
                )

                response.raise_for_status()

                data = response.json()

                ai_reply = data.get(
                    "reply",
                    "No reply received."
                )

                sources = data.get("sources", [])
                approved = data.get("approved")
                trace = data.get("trace", [])

                st.write(ai_reply)

                if sources:

                    with st.expander("📄 View Sources"):

                        for source in sources:
                            st.write(f"• {source}")

                if approved is not None:
                    st.caption(
                        f"Critic Approved: {approved}"
                    )

                if trace:
                    st.caption(
                        "Workflow: " + " → ".join(trace)
                    )

            except requests.exceptions.Timeout:

                ai_reply = (
                    "The request took too long. "
                    "Please try again."
                )

                sources = []
                approved = None
                trace = []

                st.error(ai_reply)

            except requests.exceptions.ConnectionError:

                ai_reply = (
                    "Unable to connect to the backend. "
                    "Please check whether FastAPI is running."
                )

                sources = []
                approved = None
                trace = []

                st.error(ai_reply)

            except requests.exceptions.HTTPError:

                ai_reply = (
                    f"Backend returned HTTP "
                    f"{response.status_code}: {response.text}"
                )

                sources = []
                approved = None
                trace = []

                st.error(ai_reply)

            except Exception as e:

                ai_reply = "Something went wrong."

                sources = []
                approved = None
                trace = []

                st.error(ai_reply)
                st.caption(str(e))

    # ========================================================
    # SAVE ASSISTANT RESPONSE
    # ========================================================

    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_reply,
        "sources": sources,
        "approved": approved,
        "trace": trace
    })
