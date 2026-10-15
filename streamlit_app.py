"""Rosal AI - Streamlit chatbot powered by the Gemini API.

Main file for Streamlit Community Cloud: streamlit_app.py
Secrets (Streamlit settings -> Secrets, or .streamlit/secrets.toml locally):
    GEMINI_API_KEY = "..."          # required
    GEMINI_MODEL   = "gemini-3.8-flash"   # optional
    APP_PASSWORD   = "..."          # optional, protects your free quota
"""

import os

import streamlit as st
from google import genai

DEFAULT_MODEL = "gemini-3.8-flash"
SYSTEM_PROMPT = (
    "You are Rosal AI, a friendly and concise AI assistant. "
    "Answer clearly, use short paragraphs, and say so when you are unsure. "
    "Reply in the same language the user writes in."
)
MAX_INPUT_CHARS = 4000
STARTERS = [
    "Explain quantum computing simply",
    "Write a short story about a robot",
    "Help me plan a weekly workout",
    "Give me 5 startup ideas",
]

st.set_page_config(page_title="Rosal AI", page_icon="🟡", layout="centered")
st.logo("logo.svg", size="large")


def secret(name, default=None):
    """Read from Streamlit secrets first, then environment variables."""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.environ.get(name, default)


@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)


def friendly_error(exc):
    text = str(exc)
    if "429" in text or "RESOURCE_EXHAUSTED" in text or "quota" in text.lower():
        return "Rosal AI has hit its free usage limit for now. Please try again later."
    if "API key" in text or "401" in text or "403" in text or "PERMISSION_DENIED" in text:
        return "The API key was rejected. Check GEMINI_API_KEY in the app's secrets."
    if "404" in text or "NOT_FOUND" in text:
        return "That model isn't available. Set GEMINI_MODEL in the app's secrets to a current model."
    return "Something went wrong talking to the model. Please try again."


# ---- Optional password gate (keeps strangers from burning your free quota) ----
app_password = secret("APP_PASSWORD")
if app_password and not st.session_state.get("authed"):
    st.title("Rosal AI")
    entered = st.text_input("Password", type="password")
    if entered:
        if entered == app_password:
            st.session_state["authed"] = True
            st.rerun()
        else:
            st.error("Wrong password.")
    st.stop()

api_key = secret("GEMINI_API_KEY")
if not api_key:
    st.title("Rosal AI")
    st.error("Missing GEMINI_API_KEY. Add it in the app's Secrets settings.")
    st.stop()

model = secret("GEMINI_MODEL", DEFAULT_MODEL)
client = get_client(api_key)

# ---- State ----
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"|"assistant", "content": str}]
if "interaction_id" not in st.session_state:
    st.session_state.interaction_id = None  # server-side chat memory pointer

with st.sidebar:
    if st.button("New chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.interaction_id = None
        st.rerun()
    st.caption("Rosal AI can make mistakes. Check important information.")

# ---- Header / starters ----
if not st.session_state.messages:
    st.title("Rosal AI")
    st.write("How can I help you today?")
    cols = st.columns(2)
    for i, text in enumerate(STARTERS):
        if cols[i % 2].button(text, key=f"starter{i}", use_container_width=True):
            st.session_state.pending = text
            st.rerun()

# ---- Render history ----
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---- Input ----
prompt = st.chat_input("Message Rosal AI...") or st.session_state.pop("pending", None)

if prompt:
    prompt = prompt.strip()[:MAX_INPUT_CHARS]
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                kwargs = dict(
                    model=model,
                    input=prompt,
                    system_instruction=SYSTEM_PROMPT,
                )
                if st.session_state.interaction_id:
                    kwargs["previous_interaction_id"] = st.session_state.interaction_id
                interaction = client.interactions.create(**kwargs)
            answer = interaction.output_text or "(No reply. Please try again.)"
            st.markdown(answer)
            st.session_state.interaction_id = interaction.id
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as exc:  # noqa: BLE001
            st.session_state.messages.pop()  # drop the unanswered user turn
            st.error(friendly_error(exc))
