import streamlit as st

# The text content from your image
# HTML/CSS to center the block and limit its width
st.markdown("""
    <div style='text-align: center;'>
        <h1>Welcome to RegenoTrak!</h1>
        <h3>This multi-page clinical intelligence platform is designed to accelerate research in regenerative medicine. It automates the entire analytical workflow by fetching live trial data from the ClinicalTrials.gov API, generating dynamic visualizations, and utilizing the Gemini LLM to produce tailored, strategic reports and answer complex data queries in a contextual chatbot environment.</h3>
        <h3>You will be able to find and analyze all cutting-edge interventions and treatments currently in clinical trials. This data includes the full spectrum of regenerative modalities, from advanced Cell and Gene Therapies to next-generation Tissue-Engineered Scaffolds and combination Drug/Device products.</h3>
    </div>
    """, unsafe_allow_html=True)


st.divider()

# Introduction
# TODO: Write a quick description for all of your pages in this lab below, in the form:
#       1. **Page Name**: Description
#       2. **Page Name**: Description
#       3. **Page Name**: Description
#       4. **Page Name**: Description

st.markdown("""
<div style='font-size: 1.25rem;'>
You can navigate between the pages using the sidebar to the left. The following pages are:

1. <b>Clinical Trial Explorer and Visualizer</b>
2. <b>Trial Summaries for Clinical & Industry Use</b>
3. <b>Chatbot for Further Insights on Selected Trials</b>
</div>
""", unsafe_allow_html=True)

