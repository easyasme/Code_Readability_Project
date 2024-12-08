import streamlit as st
import time
import requests

API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
headers = {"Authorization": f"Bearer {st.secrets['api_token']}"}

st.set_page_config(
    page_title="ChatBot - Demo",
    page_icon=":robot:"
)

st.header("ChatBot - Demo")


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def stream(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.05)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me anything"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    fetch = True
    with st.chat_message("assistant"):
        while fetch:
            try:
                with st.spinner('Typing...'):
                    output = query(prompt)
                    output_text = output[0]["generated_text"]
                    fetch = False
            # print(output)
            except KeyError:
                fetch = True
        st.write_stream(stream(output_text))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": output_text})

print(st.session_state.messages)