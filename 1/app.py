import streamlit as st
import config
from utils.greet import greet


st.set_page_config(page_title="Minimal Streamlit Demo", page_icon="✨", layout="centered")


def sidebar():
    st.sidebar.header("Demo Controls")
    name = st.sidebar.text_input("Your name", value="Streamlit Learner")
    color = st.sidebar.color_picker("Pick a color", "#4CAF50")
    show_balloons = st.sidebar.checkbox("Show balloons", value=True)
    return name, color, show_balloons


def main():
    name, color, show_balloons = sidebar()

    st.title("Minimal Streamlit App")
    st.caption("Starter example: inputs, layout, and file upload")

    # Basic widgets
    st.subheader("Interactive widgets")
    col1, col2 = st.columns(2)
    with col1:
        mood = st.selectbox("How are you feeling?", ["Happy", "Curious", "Focused", "Chill"]) 
    with col2:
        level = st.slider("Learning intensity", 1, 10, 5)

    st.markdown(f"{greet(name)} Your color is `{color}` and intensity is `{level}`.")

    # File upload demo (no processing)
    st.subheader("File upload")
    uploaded_files = st.file_uploader("Upload one or more files", type=config.SUPPORTED_FILE_TYPES, accept_multiple_files=True)

    if uploaded_files:
        st.info(f"Selected {len(uploaded_files)} file(s): " + ", ".join(f.name for f in uploaded_files))

    if show_balloons:
        st.balloons()

    st.divider()
    st.markdown("Try creating new helpers in `utils` and importing them here.")


if __name__ == "__main__":
    main()

