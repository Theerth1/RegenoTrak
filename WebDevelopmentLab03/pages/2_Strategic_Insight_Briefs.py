#- we can ask the same intiial question with mapping and stuff  (copy paste here)
# based on user input on the field, can generate industry/clinican oriented briefs for those groups of trials
import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
import os
import tabulate

st.markdown("""
    <div style='text-align: center;'>
        <h1>Strategic Insight Briefs (LLM Analysis)</h1>
        <h3>This page provides Industry/Clinician-Oriented Strategic Insights and Functional Reports based on existing clinical trials in any area of interest. You can use this webpage to do things like assess research maturity, market gaps, and strategic implications for both clinical practice and industry sponsorship.</h3>
    </div>
    """, unsafe_allow_html=True)

st.divider()
#---------------------------------SESSION STATE INITIALIZATION-------------------------------------------------------
if "past_queries" not in st.session_state:
    st.session_state["past_queries"] = []

if "raw_df" not in st.session_state:
    st.session_state["raw_df"] = None

if "filtered_df" not in st.session_state:
    st.session_state["filtered_df"] = None

if "rDFkey" not in st.session_state:
   st.session_state['rDFkey'] = None

if "fDFkey" not in st.session_state:
   st.session_state['fDFkey'] = None

if "check" not in st.session_state:
    st.session_state['check'] = False

if "query" not in st.session_state:
    st.session_state['query'] = None
#------------------------------------------------------------------------------------------------------------------------------------


#use past queires and current query as the dfs no need to reinvent the wheel
#logical block below checks multiple cases; has the user made any queries; how many queries; would they like to use filtered or nonfiltered
if st.session_state['past_queries'] == []:
    if st.session_state['raw_df'] is None: #it is initialized to None back in page 1; if data is fetched, it will not be None
        st.warning("Please Go To the Clinical Trial Explorer/Visualizer Page and fetch desired trials")
    elif st.session_state['raw_df'].equals(st.session_state['filtered_df']):
        queryLLM = st.session_state['raw_df']
        st.session_state['query'] = queryLLM
    elif not st.session_state['raw_df'].equals(st.session_state['filtered_df']):
        with st.form("Query Selector"):
            queryLLM1 = st.selectbox("Please choose a past query to generate your Industry/Clinician-Oriented Reports. You have fetched one set of trials so far. Would you like to use the query where you applied constriants (filtered) or did not apply any constriants (unfiltered)?", 
                                    ["Without Constraints/Unfiltered", "With Constraints/Filtered"])
            Submitted1 = st.form_submit_button("Enter")
else:
    #make a for loop going through all past queries, put into a list, and put that list variable down there for st.selectbox
    #this assumes there are past queries and a current query
    options = []
    tempDict = {} #use to access any df from the identifying name
    options.append(st.session_state['rDFkey'])
    options.append(st.session_state['fDFkey'])
    tempDict[st.session_state['rDFkey']] = st.session_state['raw_df']
    tempDict[st.session_state['fDFkey']] = st.session_state['filtered_df']

    for rDict,fDict in st.session_state['past_queries']:
        rawDictname = str(list(rDict.keys())[0])
        filteredDictname = str(list(fDict.keys())[0])
        tempDict[rawDictname] = list(rDict.values())[0]
        tempDict[filteredDictname] = list(fDict.values())[0]
        if list(rDict.values())[0].equals(list(fDict.values())[0]):
            options.append(rawDictname)
        else:
            options.append(rawDictname)
            options.append(filteredDictname)



    with st.form("Query Selector"):
        queryLLM2 = st.selectbox("Please choose a past query to generate your Industry/Clinician-Oriented Reports", options)
        Submitted2 = st.form_submit_button("Enter")
#--------------------------------------------------------------------------------------------------------------------------
if st.session_state['query'] is not None and not st.session_state['query'].empty: #this accounts for if they made one inquiry with no filter
    st.session_state['check'] = True
try:
    if Submitted1: #submitted 1 was for choosing between unfiltered vs filtered (only made one inquiry and maybe added filter)
        if queryLLM1 == "Without Constraints/Unfiltered":
            queryLLM = st.session_state['raw_df']
            st.session_state['query'] = queryLLM
            st.session_state['check'] = True
    
        elif queryLLM1 == "With Constraints/Filtered":
            queryLLM = st.session_state['filtered_df']
            st.session_state['query'] = queryLLM
            st.session_state['check'] = True
        
except:
    pass

try:
    if Submitted2: #accounts for if they made multiple inquiries
        queryLLM = tempDict[queryLLM2]
        st.session_state['query'] = queryLLM
        st.session_state['check'] = True
except:
    pass

if st.session_state['check']:
    with st.form("Industry or Clinical"):
        choice = st.selectbox("Would you like to generate a Clinical and/or Industry oriented report on the desired set of fetched trials?",["Clinical", "Industry", "Both"])
        extraInput = st.text_input("If you would like, you may make a specific, additional request to the Gemini LLM, pertaining to this set of fetched trials. If you would not like to, please leave this field blank.")
        Submitted3 = st.form_submit_button("Generate")

KEY = 'AIzaSyAuPzZSeDc-D-d2t5lc_8Mvu97pKvoD1x8'
#at this point, queryLLM holds the wanted df adn choice holds the wanted type of report
#--------------------------------------------------------------------------------------------------------------------------------------------------
#need the tabulate module to flatten if incase df is None or tmpyy
#need to pass in queryLLM for df and KEY for key, extraInput for ei, choice for choice
#geminiCall finds gemini Model, creates datastring based on dataframe, selects proper prompt, and gives prompt to model, returnign the response
def geminiCall(df, key, ei, choice, limit = 10000):
    if key:
        try:
            genai.configure(api_key=key)
            # Find a model that supports generation, prefer Flash
            #list comprehension
            all_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            for m in all_models:
                if 'flash' in m.name.lower():
                    active_model = genai.GenerativeModel(m.name)
                    break
            if not active_model and all_models:
                active_model = genai.GenerativeModel(all_models[0].name)
        except:
            st.write("❌ AI Connection Failed")
    dataString = df.head(limit).to_markdown(index=False)

    #this below just develops the right prompt to use
    if ei:
        if choice == "Clinical":
            prompt = f"""
            ROLE: Medical Research Director & Academic Grant Reviewer.
            TASK: Analyze the provided clinical trial data to generate a specialized Clinical Feasibility Brief.
            
            *** CRITICAL USER INSTRUCTION ***
            The user has provided a specific constraint that should be accounted for in addition to your standard task:
            "{extraInput}"
            Ensure this instruction is accounted for.
            
            DATASET (Markdown Table):
            {dataString}
            
            OUTPUT REQUIREMENTS:
            1. **User Request Analysis:** Directly address the specific instruction provided above using the data.
            2. **Clinical Maturity:** Is this field experimental (Phase 1) or established (Phase 3)?
            3. **Gap Analysis:** Identify a specific missing area of research (e.g., lack of pediatric trials or long-term follow-up).
            4. **Grant Justification:** Write a 3-sentence paragraph justifying funding for a new study, specifically referencing the user's constraint.
            """
        elif choice == "Industry":
            prompt = f"""
            ROLE: Biotech Strategy Consultant & Venture Capital Analyst.
            TASK: Analyze the provided clinical trial data to generate a specialized Industry Competitive Landscape Report.
            
            *** CRITICAL USER INSTRUCTION ***
            The user has provided a specific constraint that should be accounted for in addition to your standard task:
            "{extraInput}"
            Ensure this instruction is accounted for.
            
            DATASET (Markdown Table):
            {dataString}
            
            OUTPUT REQUIREMENTS:
            1. **User Request Analysis:** Directly address the specific instruction provided above using the data.
            2. **Market Leaders:** Identify the top sponsors (Industry vs. Academic) and their dominance.
            3. **Competitive Crowding:** Which intervention types are oversaturated?
            4. **Strategic Recommendation:** Provide a specific recommendation for investment or divestment based on the user's constraint.
            """
        elif choice == "Both":
            prompt = f"""
            ROLE: Regenerative Medicine Ecosystem Analyst.
            TASK: Analyze the provided data for a comprehensive "State of the Field" report.
            
            *** CRITICAL USER INSTRUCTION ***
            The user has provided a specific constraint that should be accounted for in addition to your standard task:
            "{extraInput}"
            Ensure this instruction is accounted for.
            
            DATASET (Markdown Table):
            {dataString}
            
            OUTPUT REQUIREMENTS:
            1. **User Request Analysis:** Directly address the specific instruction provided above.
            2. **Executive Summary:** Combine clinical maturity and market trends into a snapshot.
            3. **SWOT Analysis:** Provide one Strength, Weakness, Opportunity, and Threat related to the user's specific area of interest.
            4. **Dual Recommendation:** Provide one actionable step for a clinician and one for an investor.
            """ 
    else:
        if choice == "Clinical":
            prompt = f"""
            ROLE: Medical Research Director & Academic Grant Reviewer.
            TASK: Analyze the provided clinical trial data to generate a Clinical Feasibility Brief.
            
            DATASET (Markdown Table):
            {dataString}
            
            OUTPUT REQUIREMENTS:
            1. **Clinical Maturity:** Summarize the phase distribution. Is this field experimental (Phase 1) or established (Phase 3)?
            2. **Intervention Feasibility:** Which intervention type appears most viable based on the status (Recruiting/Completed)?
            3. **Gap Analysis:** Identify a specific missing area of research (e.g., "Lack of pediatric trials" or "No long-term follow-up") that could justify a new grant.
            4. **Grant Justification:** Write a 3-sentence paragraph justifying funding for a new study in this area using data evidence.
            """
        elif choice == "Industry":
            prompt = f"""
            ROLE: Biotech Strategy Consultant & Venture Capital Analyst.
            TASK: Analyze the provided clinical trial data to generate an Industry Competitive Landscape Report.
            
            DATASET (Markdown Table):
            {dataString}
            
            OUTPUT REQUIREMENTS:
            1. **Market Leaders:** Identify the top sponsors (Industry vs. Academic) and their dominance.
            2. **Competitive Crowding:** Which intervention types are oversaturated? Where is the "Blue Ocean" opportunity?
            3. **Speed to Market:** Analyze the duration and status. Are trials bogging down or moving quickly?
            4. **Executive Summary:** Write a 3-sentence summary for a potential investor on whether to invest in this specific niche.
            """
        elif choice == "Both":
            prompt = f"""
            ROLE: Regenerative Medicine Ecosystem Analyst.
            TASK: Analyze the provided data for a comprehensive "State of the Field" report.
            
            DATASET (Markdown Table):
            {dataString}
            
            OUTPUT REQUIREMENTS:
            1. **Executive Summary:** Combine clinical maturity and market heat into a snapshot.
            2. **Key Players & Trends:** Briefly list top sponsors and dominant interventions.
            3. **SWOT Analysis:** Provide one Strength, Weakness, Opportunity, and Threat based on the data.
            4. **Strategic Recommendation:** Provide one recommendation for a clinician and one for an investor.
            """

    try:
        response = active_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to Gemini: {str(e)}"
#----------------------------------------------------------------------------------------------------------------------------------------------
try:
    if Submitted3: #accounts for if clinical/industry and extra user input
        st.divider()

        if st.session_state['query'] is None:
            st.error("No dataset selected. Please go up to the 'Query Selector' form above and click 'Enter' again to lock in your data.")
        
        else:
            with st.spinner("**Analyzing data...**"):
                response = geminiCall(st.session_state['query'], KEY, extraInput, choice)
                st.markdown(response)
            
except:
    pass