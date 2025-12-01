import streamlit as st

# The text content from your image
text_content = """
This multi-page clinical intelligence platform is designed to accelerate research in regenerative medicine. It automates the entire analytical workflow by fetching live trial data from the ClinicalTrials.gov API, generating dynamic visualizations, and utilizing the Gemini LLM to produce tailored, strategic reports and answer complex data queries in a contextual chatbot environment.

You will be able to find and analyze all cutting-edge interventions and treatments currently in clinical trials. This data includes the full spectrum of regenerative modalities, from advanced Cell and Gene Therapies to next-generation Tissue-Engineered Scaffolds and combination Drug/Device products.
"""

# HTML/CSS to center the block and limit its width
st.markdown(
    f"""
    <div style='
        max-width: 600px; /* Adjust this value (e.g., 500px, 700px) to control block width */
        margin-left: auto; /* Centers the block itself */
        margin-right: auto; /* Centers the block itself */
        text-align: center; /* Centers the text inside the block */
        font-size: 1.1em; /* Optional: Slightly increase font size for better look */
    '>
    {text_content}
    </div>
    """,
    unsafe_allow_html=True
)


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

