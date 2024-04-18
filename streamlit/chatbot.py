import streamlit as st
from openai import OpenAI

def kanbot(contents):
    """
    A chatbot function that interacts with the user and provides responses using the OpenAI GPT-3 model.

    Parameters:
    - contents (list): The current task list.

    Returns:
    None
    """

    openai_api_key = st.secrets["api_key"]
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    # Create an expander widget in the sidebar for the chat window
    with st.sidebar.expander("KanBot", expanded=False):
        for msg in st.session_state.messages:
            if msg['role'] == 'user':  # Display only the user's message
                st.text_area(f"**You**", msg['content'], disabled=True)

        if og_msg := st.text_input("Your message"):
            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
                st.stop()
            list = contents
            prefix = f'This is the current task list:\n\n {list} \n\n. Categories are not indented.  When asked a question about any todo list, always assume that the list is the one above. \n\n Do not refer to any other list. \n '
            prompt = prefix + og_msg
            client = OpenAI(api_key=openai_api_key)

            # Add only the original message to the user's message
            st.session_state.messages.append({"role": "user", "content": og_msg})

            # Append the complete prompt to the assistant's message
            st.session_state.messages.append({"role": "assistant", "content": prompt})

            response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
            msg = response.choices[0].message.content

            # Clear the session state messages after receiving the response
            st.session_state.messages = []

            # Display the assistant's response in a text area
            st.text_area(f"**Assistant**", msg, disabled=False)

