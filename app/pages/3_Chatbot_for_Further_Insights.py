import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
import os
import tabulate
import numpy as np

# --- PAGE SETUP -------------------------------------------------------------------------------
st.set_page_config(page_title="TrialBot")

st.markdown("""
    <div style='text-align: center;'>
        <h1>Clinical Trial Chatbot</h1>
        <h3>Ask questions about your selected dataset!</h3>
    </div>
    """, unsafe_allow_html=True)

st.divider()
#--------------------------------------------------------
if "query" not in st.session_state:
    st.session_state['query'] = None
if 'raw_df' not in st.session_state:
    st.session_state['raw_df'] = None
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
KEY = st.secrets["GEMINI_API_KEY"]
#---------------------------------------------------------
active_model = None
try: #this gets active model
    genai.configure(api_key=KEY)
    # Find a model that supports generation, prefer Flash
    #list comprehension
    all_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    for m in all_models:
        if 'flash' in m.name.lower():
            active_model = genai.GenerativeModel(m.name)
            break
    if not active_model and all_models:
        active_model = genai.GenerativeModel(all_models[0].name)
except Exception as e:
    st.write(f"error details: {e}")
# --- GUARDRAIL: Check if data exists ---
if st.session_state['query'] is None and st.session_state['raw_df'] is None:
    st.warning("No dataset selected. Please go to the **Strategic Insights** page (Page 2) or **Explorer** page (Page 1) and confirm a dataset first.")
    st.stop() # Stops the rest of the app from running so it doesn't crash
elif st.session_state['query'] is not None and not st.session_state['query'].empty:
    st.write("**Your chosen data set from the **Strategic Insights** page (Page 2) will be used for this conversation.**")
    st.divider()
    dataString = st.session_state['query'].head(10000).to_markdown(index=False)
elif st.session_state['raw_df'] is not None and not st.session_state['raw_df'].empty:
    st.write("**Your chosen data set from the **Explorer** page (Page 1) will be used for this conversation since you did not interact with the **Strategic Insights** page (Page 2).**")
    st.divider()
    dataString = st.session_state['raw_df'].head(10000).to_markdown(index=False)

for message in st.session_state['messages']: #message is a dict containing if the person is user/ai and the message under the keys "role" and "content"
    with st.chat_message(message["role"]): #with tells us that anythign below belong to this role; this line creates a container for user/ai 
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about this clinical trial data..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    full_prompt = f"""
                You are a helpful Clinical Trial Analyst.

                CONTEXT DATA (The user is asking questions about this dataset):
                {dataString}

                USER QUESTION:
                {prompt}

                INSTRUCTIONS:
                - Use the provided table to answer the question.
                - If the answer is not in the table, state that you do not have that information.
                - Keep answers concise and professional.
                """

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            if active_model is None:
                ai_reply = "AI Connection Failed. Please check the Gemini API key and try again."
                st.error(ai_reply)
            else:
                try:
                    response = active_model.generate_content(full_prompt)
                    ai_reply = response.text
                    st.markdown(ai_reply)
                except Exception as e:
                    ai_reply = f"Error connecting to Gemini: {str(e)}"
                    st.error(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

