import streamlit as st
import requests


<<<<<<< HEAD
# ============================================================
# PAGE CONFIGURATION
# ============================================================
=======
import os

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

# ----------------------------------
# Page Config
# ----------------------------------
>>>>>>> origin/main

st.set_page_config(
    page_title="AI Academic Assistant",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# BACKEND CONFIGURATION
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🎓 AI Academic Assistant")

    st.markdown("---")

    st.subheader("Ask About")

    st.markdown(
        """
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
        """
    )

    st.markdown("---")

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.title("🎓 AI Academic Assistant")

st.write(
    "Ask questions about admissions, fees, batches, "
    "faculty, scholarships, academic policies, "
    "JEE/NEET preparation, and other academic information."
)


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

user_message = st.chat_input(
    "Ask your question..."
)


# ============================================================
# PROCESS USER QUESTION
# ============================================================

if user_message:

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    with st.chat_message("user"):
        st.write(user_message)


    # --------------------------------------------------------
    # Prepare API request
    # --------------------------------------------------------

    payload = {
        "user_id": "student",
        "session_id": "academic_session",
        "message": user_message
    }

    url = f"{BACKEND_URL}/chat"


    # --------------------------------------------------------
    # Call backend
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = requests.post(
                    url,
                    json=payload,
                    timeout=120
                )


                # ------------------------------------------------
                # Successful response
                # ------------------------------------------------

                if response.status_code == 200:

                    data = response.json()

                    ai_reply = data.get(
                        "reply",
                        "No reply received."
                    )

                    st.write(ai_reply)


                    # ------------------------------------------------
                    # Display sources
                    # ------------------------------------------------

                    sources = data.get(
                        "sources",
                        []
                    )

                    if sources:

                        st.markdown("### 📄 Sources")

                        for source in sources:

                            st.write(
                                f"• {source}"
                            )


                # ------------------------------------------------
                # Backend error
                # ------------------------------------------------

                else:

                    ai_reply = (
                        f"Backend Error "
                        f"({response.status_code})\n\n"
                        f"{response.text}"
                    )

                    st.error(ai_reply)


            # ----------------------------------------------------
            # Connection / timeout / unexpected errors
            # ----------------------------------------------------

            except requests.exceptions.Timeout:

                ai_reply = (
                    "The request took too long to complete. "
                    "Please try again."
                )

                st.error(ai_reply)


            except requests.exceptions.ConnectionError:

                ai_reply = (
                    "Unable to connect to the backend. "
                    "Please try again later."
                )

                st.error(ai_reply)


            except Exception as e:

                ai_reply = (
                    "Something went wrong while processing "
                    "your question."
                )

                st.error(ai_reply)

                # Keep technical error out of the main UI
                st.caption(str(e))


    # ========================================================
    # SAVE ASSISTANT RESPONSE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_reply
        }
<<<<<<< HEAD
    )
=======
    )

    with st.chat_message(
        "assistant"
    ):
        st.write(ai_reply)
>>>>>>> origin/main
