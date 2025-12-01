🧬 Regenotrak: AI-Driven Clinical Trial Intelligence Platform

A full-stack, multi-page Streamlit application developed for the CS 1301 Web Development Lab 3, designed to transform raw clinical trial data into actionable strategic intelligence for biotech and academic research.

Regenotrak integrates a live external API with a Google Gemini LLM to automate market analysis, feasibility assessment, and data querying in the regenerative medicine sector.

🚀 Key Features & Functionality (Phases 2-4)

1. Clinical Trial Explorer & Visualizer (Phase 2)

This is the core data pipeline responsible for fetching and processing data from the ClinicalTrials.gov API.

Live Data Fetching: Retrieves trials based on broad category and user-defined keywords.

Robust Filtering: Custom logic allows users to filter by multi-value fields (Phase, Status) using safe, vector-based Pandas operations (.equals, .shape[0]).

Dynamic Dashboard: Generates high-value visualizations that update based on applied constraints:

Trial Duration Histogram: Calculates and plots trial duration risk (PrimaryCompletionDate - StartDate).

Intervention Popularity: Bar chart showing the distribution of intervention modalities (Drug, Device, Cell Therapy).

Phase Distribution: Pie chart showing research maturity (Phase 1 vs. Phase 3).

Geographic Distribution: Bar chart showing global trial hubs.

2. Strategic Insight Briefs (Phase 3)

This section uses the power of Generative AI to synthesize quantitative data into qualitative, role-specific reports.

LLM Integration: Utilizes the Google Gemini LLM to analyze the filtered dataset.

Functional Content Generation: Produces automated reports for two distinct audiences:

Clinical: Grant Feasibility Briefs & Clinical Maturity Analysis.

Industry: Competitive Landscape Reports & Investor Executive Summaries.

Data Serialization: Data is efficiently passed to the LLM by flattening the DataFrame into a structured Markdown string (df.to_markdown()), limited to avoid token cost and latency issues.

3. AI Chatbot (Phase 4)

A context-aware Gemini Chatbot that allows users to query the specific dataset they selected.

RAG-like Context: The chosen DataFrame is injected as hidden context (dataString) into every single prompt, allowing the AI to answer complex questions ("Which sponsor runs the most Phase 3 trials in the Northeast?") without having external web access.

State Persistence: Conversation history is maintained using Streamlit's st.session_state.

⚙️ Setup & Installation

To run this application locally, ensure you have Python 3.9+ installed and follow these steps:

1. Clone the Repository

git clone [YOUR_REPO_URL]
cd Regenotrak/


2. Install Dependencies

This project requires several external libraries, including the tabulate library for Markdown conversion.

pip install -r requirements.txt


3. API Key Configuration

This application requires a Google Gemini API Key for Phases 3 and 4.

Get your key from Google AI Studio.

Set the key as an environment variable, or use the temporary key input provided in the application's sidebar.

4. Run the Application

Start the Streamlit server from the main directory:

streamlit run Home_Page.py


📁 File Structure

The project uses Streamlit's required multi-page structure:

Regenotrak/
├── .streamlit/             # Global configuration (e.g., color theme)
│   └── config.toml
├── pages/
│   ├── 1_Clinical_Trial_Explorer_and_Visualizer.py  # Phase 2 (Data Fetching & Filtering)
│   ├── 2_Strategic_Insight_Briefs.py              # Phase 3 (LLM Analysis)
│   └── 3_Chatbot_for_Further_Insights.py          # Phase 4 (Contextual Chatbot)
├── Home_Page.py            # Entry point and general introduction
└── requirements.txt        # Python dependency list
