import streamlit as st
# Title of App
st.markdown("""
    <div style='text-align: center;'>
        <h1>Welcome to RegenoTrak!</h1>
        <h3>This web application serves as a clinical trial explorer for regenerative medicines.</h3>
        <h3>You will be able to find several different interventions/treatments that are currently being tested or used. These encompass medical devices, biologics, drugs, cell therapies, tissue-engineered constructs, behavioral interactions, procedures, and combination products.</h3>
    </div>
    """, unsafe_allow_html=True)


st.divider()

# Introduction
# TODO: Write a quick description for all of your pages in this lab below, in the form:
#       1. **Page Name**: Description
#       2. **Page Name**: Description
#       3. **Page Name**: Description
#       4. **Page Name**: Description

st.write("""
Welcome to our Streamlit Web Development Lab03 app! You can navigate between the pages using the sidebar to the left. The following pages are:

1. Clinical Trial Explorer and Visualizer
2. Trial Summaries for Clinical & Industry Use
3. Chatbot for Further Insights on Selected Trials

""")

