"""Simple Streamlit chatbot with adjustable inference parameters."""
import streamlit as st
from openai import OpenAI
import config

# Page configuration
st.set_page_config(
    page_title="Simple Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize session state for chat and generation parameters."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "temperature" not in st.session_state:
        st.session_state.temperature = float(config.TEMPERATURE)
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = int(config.MAX_TOKENS)
    if "top_p" not in st.session_state:
        st.session_state.top_p = float(getattr(config, "TOP_P", 1.0))
    if "top_k" not in st.session_state:
        st.session_state.top_k = int(getattr(config, "TOP_K", 50))


def _get_openrouter_client():
    """Create an OpenAI-compatible client configured for OpenRouter."""
    return OpenAI(api_key=config.OPENROUTER_API_KEY, base_url=config.OPENROUTER_BASE_URL)


def _build_message_history():
    """Return chat history formatted for the OpenAI-compatible API."""
    formatted = []
    # Optional system prompt
    system_prompt = getattr(config, "SYSTEM_PROMPT", None)
    if system_prompt:
        formatted.append({"role": "system", "content": system_prompt})

    for msg in st.session_state.messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in {"user", "assistant"} and content:
            formatted.append({"role": role, "content": content})
    return formatted


def generate_response(prompt):
    """Call the model and return the assistant's reply text."""
    client = _get_openrouter_client()
    messages = _build_message_history() + [{"role": "user", "content": prompt}]

    payload = {
        "model": config.LLM_MODEL,
        "messages": messages,
        "temperature": float(st.session_state.temperature),
        "max_tokens": int(st.session_state.max_tokens),
        "top_p": float(st.session_state.top_p),
        "top_k": int(st.session_state.top_k),
    }

    try:
        completion = client.chat.completions.create(**payload)
    except Exception as first_error:
        # Fallback if provider doesn't support top_k (remove and retry once)
        if "top_k" in payload:
            payload.pop("top_k", None)
            try:
                completion = client.chat.completions.create(**payload)
            except Exception as second_error:
                return f"[Error from provider after retry: {second_error}]"
        else:
            return f"[Error from provider: {first_error}]"

    choice = completion.choices[0]
    content = getattr(choice.message, "content", None) or ""
    if not content.strip():
        finish_reason = getattr(choice, "finish_reason", None)
        if finish_reason == "content_filter":
            return "[Response blocked by model content filter.]"
        return "[Model returned an empty response. Try another model or adjust settings.]"
    return content


def display_sidebar():
    """Display sidebar controls for inference parameters and chat management."""
    with st.sidebar:
        st.subheader("⚙️ Inference Parameters")

        if not config.OPENROUTER_API_KEY:
            st.error(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY in the project root `.env` "
                "(see `.env.example`)."
            )
            st.stop()

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=float(st.session_state.temperature),
                step=0.05,
                help="Higher = more creative, lower = more deterministic.",
            )
        with col2:
            st.session_state.top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=float(st.session_state.top_p),
                step=0.01,
                help="Nucleus sampling cutoff.",
            )

        col3, col4 = st.columns(2)
        with col3:
            st.session_state.max_tokens = st.number_input(
                "Max Tokens",
                min_value=16,
                max_value=8192,
                value=int(st.session_state.max_tokens),
                step=16,
                help="Max new tokens to generate.",
            )
        with col4:
            st.session_state.top_k = st.number_input(
                "Top K",
                min_value=1,
                max_value=200,
                value=int(st.session_state.top_k),
                step=1,
                help="Sample from the top K tokens (model-dependent).",
            )

        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def display_chat():
    """Render the chat conversation and input box."""
    st.title("🤖 Simple Chatbot")
    st.caption("Adjust inference parameters in the sidebar and start chatting.")

    # Existing messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant reply without rendering an in-flight assistant bubble
        with st.spinner("Thinking..."):
            reply = generate_response(prompt)

        # Persist assistant reply and rerun to render via history
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()


def main():
    initialize_session_state()
    display_sidebar()
    display_chat()


if __name__ == "__main__":
    main()

