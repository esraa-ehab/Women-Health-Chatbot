import streamlit as st
from chatbot import ask_question

st.set_page_config(page_title="Women's Health Chatbot", page_icon="💬")
st.title("Women's Health Chatbot!")
st.markdown(
    """
    This chatbot is designed to provide information and answer questions related to Women's Health.
    It can also engage in small talk. Feel free to ask me anything!
    """
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for sender, message in st.session_state.chat_history:
    with st.chat_message("user" if sender == "You" else "assistant"):
        st.markdown(message)

if prompt := st.chat_input("Ask a question..."):
    st.session_state.chat_history.append(("You", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = ask_question(prompt)
    except Exception as e:
        response = "⚠️ Sorry, something went wrong. Please try again."

    st.session_state.chat_history.append(("Bot", response))
    with st.chat_message("assistant"):
        st.markdown(response)

st.sidebar.button("🔁 Clear Chat", on_click=lambda: st.session_state.update(chat_history=[]))