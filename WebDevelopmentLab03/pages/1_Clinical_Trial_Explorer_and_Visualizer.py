import streamlit as st
import pandas as pd
import requests
import plotly.express as px
#Title---------------------------------------------------------------------------------------------------------------------

st.markdown("""
    <div style='text-align: center;'>
        <h1>Clinical Trial Explorer and Visualizer</h1>
        <h3>Use this to find clinical trials for current regenerative medicine interventions/treatments and to visualize trends across trials</h3>
    </div>
    """, unsafe_allow_html=True)

st.divider()
#---------------------------------------------------------------------------------------------------------------------------
#SESSION STATE INITIALIZATION
if "raw_df" not in st.session_state: #will store a dataframe with all current trials the api collects (raw)
    st.session_state["raw_df"] = None

if "filtered_df" not in st.session_state: #will store a dataframe with all current trials the api collects (will be value of rawdf until user applies phase/status filters for dynamic charts)
    st.session_state["filtered_df"] = None

if "broad_category" not in st.session_state: #need to map user select to multiple words and store here
    st.session_state['broad_category'] = None

if "key_words" not in st.session_state: #when user makes a new query, old queries and their df will get stored in a dict here (so the chatbot can use it later on)
    st.session_state["key_words"] = None

if "unique_keyword_string" not in st.session_state: 
    st.session_state["unique_keyword_string"] = None

if "broad_category_label" not in st.session_state:
    st.session_state['broad_category_label'] = None

if "expr" not in st.session_state:
    st.session_state['expr'] = None

if "phase_filter" not in st.session_state:
    st.session_state["phase_filter"] = None

if "status_filter" not in st.session_state:
    st.session_state["status_filter"] = None

if "past_queries" not in st.session_state: #will be formatted as a dictionary where values are old data frames
    st.session_state["past_queries"] = []

if "rDFkey" not in st.session_state:
   st.session_state['rDFkey'] = None

if "fDFkey" not in st.session_state:
   st.session_state['fDFkey'] = None

#example trials_df will contain["NCTId","BriefTitle", "Condition", "InterventionType", "InterventionName", 
#"Phase", "OverallStatus", "LocationCountry", "SponsorName", "StartDate","PrimaryCompletionDate", "Link"]
#---------------------------------------------------------------------------------------------------------------------------

#USER INPUT
with st.form("Clinical Trial Searcher"):
  broad_category = st.selectbox("Please choose a broad category that encompasses different regenerative medicine interventions/treatments:", 
["Cartilage regeneration", "Bone regeneration", "Wound healing / skin", "Cardiac repair", "Nerve repair", "General scaffolds/hydrogels", "Bioprinting / 3D printing"])
  unique_keyword = st.text_input("Please type specific keyword(s) that fall under the broad category that you previously chose (eg. VEGF or decellularized matrix). If you would like to choose multiple, please place a comma between each item without any spaces between the commas and items")
  unique_keyword_list = [x.strip() for x in unique_keyword.split(",") if x.strip()]
  unique_keyword_string = ""
  if unique_keyword_list:
    for v in unique_keyword_list:
        unique_keyword_string += (v + " AND ")
  submitted1 = st.form_submit_button("Fetch")

#---------------------------------------------------------------------------------------------------------------------------
#takes broad category user input and maps to a exhaustive string of synonyms (cartilage -> "chondro OR cartilage OR..."")
BC_mapper = {

    "Cartilage regeneration": """
    (
      cartilage OR chondral OR chondral lesion OR chondral defect OR
      chondromalacia OR "articular cartilage" OR "knee cartilage" OR
      meniscus OR meniscal OR osteochondral OR "osteochondral defect" OR
      chondrocyte OR chondrocytes
    )
    AND
    (
      regeneration OR regenerative OR repair OR restoration OR resurfacing OR
      "tissue engineering" OR "regenerative medicine" OR "cartilage repair"
    )
    """,

    "Bone regeneration": """
    (
      bone OR bones OR osseous OR skeletal OR "bone defect" OR
      "segmental defect" OR "critical size defect" OR "fracture nonunion" OR
      "bone nonunion" OR "bone graft" OR "bone grafting" OR
      "spinal fusion" OR "spine fusion" OR
      "alveolar bone" OR "craniofacial" OR "maxillofacial" OR
      osteogenesis OR osteogenic OR "bone substitute" OR "bone substitute material"
    )
    AND
    (
      regeneration OR regenerative OR repair OR healing OR "bone healing" OR
      "bone regeneration" OR "bone repair" OR "tissue engineering" OR
      "regenerative medicine"
    )
    """,

    "Wound healing / skin": """
    (
      skin OR dermal OR dermis OR cutaneous OR epidermal OR
      wound OR wounds OR "chronic wound" OR "acute wound" OR
      ulcer OR ulcers OR "skin ulcer" OR "diabetic foot ulcer" OR
      "venous leg ulcer" OR "pressure ulcer" OR "pressure injury" OR
      "burn wound" OR "burn injury" OR "skin defect" OR "skin loss"
    )
    AND
    (
      healing OR "wound healing" OR regeneration OR regenerative OR repair OR
      "skin regeneration" OR "skin substitute" OR "tissue-engineered skin" OR
      "tissue engineered skin"
    )
    """,

    "Cardiac repair": """
    (
      cardiac OR heart OR myocardial OR myocardium OR
      "myocardial infarction" OR "MI" OR "ischemic cardiomyopathy" OR
      cardiomyopathy OR "heart failure" OR "ventricular remodeling" OR
      "ventricular remodelling"
    )
    AND
    (
      regeneration OR regenerative OR repair OR remuscularization OR
      "cardiac repair" OR "cardiac regeneration" OR
      "tissue engineering" OR "regenerative medicine" OR
      "cardiac patch" OR "myocardial patch"
    )
    """,

    "Nerve repair": """
    (
      nerve OR nerves OR "peripheral nerve" OR "peripheral nerves" OR
      neuropathy OR "nerve injury" OR "nerve defect" OR
      "brachial plexus" OR "median nerve" OR "ulnar nerve" OR
      "sciatic nerve" OR
      "spinal cord" OR "spinal cord injury" OR "SCI"
    )
    AND
    (
      regeneration OR regenerative OR repair OR "nerve repair" OR
      "nerve regeneration" OR "nerve graft" OR "nerve conduit" OR
      "nerve guidance conduit" OR "tissue engineering" OR
      "regenerative medicine"
    )
    """,

    "General scaffolds/hydrogels": """
    (
      scaffold OR scaffolds OR "tissue scaffold" OR "bone scaffold" OR
      "cartilage scaffold" OR "nerve scaffold" OR
      hydrogel OR hydrogels OR "injectable hydrogel" OR
      biomaterial OR biomaterials OR
      "extracellular matrix" OR "ECM" OR
      decellularized OR decellularised OR "acellular matrix" OR
      "matrix-based" OR "tissue matrix"
    )
    AND
    (
      regeneration OR regenerative OR repair OR
      "tissue regeneration" OR "tissue repair" OR
      "tissue engineering" OR "regenerative medicine"
    )
    """,

    "Bioprinting / 3D printing": """
    (
      bioprinting OR "bio-printing" OR "bio printing" OR
      bioink OR bioinks OR
      "3D printing" OR "3-D printing" OR "3 dimensional printing" OR
      "three dimensional printing" OR "three-dimensional printing" OR
      "additive manufacturing" OR biofabrication OR "bio-fabrication"
    )
    AND
    (
      scaffold OR scaffolds OR hydrogel OR hydrogels OR
      patch OR construct OR implant OR
      "tissue engineering" OR "tissue engineered" OR
      "regenerative medicine" OR regeneration OR regenerative OR repair
    )
    """
}
#---------------------------------------------------------------------------------------------------------------------------

#IMPORTANT: FORMAT OF JSON ; for each item in the "studies" list, there is one clinical trial
#{
#  "studies": [
#    {
#     "protocolSection": {
#       "identificationModule": { ... },
#        "conditionsModule": { ... },
#        "armsInterventionsModule": { ... },
#        "designModule": { ... },
#        "statusModule": { ... },
#        "sponsorCollaboratorsModule": { ... },
#        "contactsLocationsModule": { ... }
#      }
#    },
#    ...
#  ]
#}
#

def listJoiner(aList):
    if aList is None or len(aList) == 0:
        return ""
    result = ""
    for item in aList:
        if item is None or item == "":
            continue
        item_str = str(item)
        if not result:
            result = item_str
        else:
            result = result + '; ' + item_str
    return result     

#raw/filtered DF creator (each api fetch is in a list even if one value, so listJoiner makes it into a string)
#carefully finding nuggets of desired information in junglish json
def dfCreator(expr):
  #dataframe columns:
  header = [
        "NCTId",
        "Title",
        "Condition",
        "InterventionType",
        "InterventionName",
        "Phase",
        "OverallStatus",
        "LocationCountry",
        "SponsorName",
        "StartDate",
        "PrimaryCompletionDate",
        "Link"
    ]
  #parameters (unique keyword string) can be plugged into .get method to get only relavent trials to what the user wants
  parameters = {'query.term': expr, 'pageSize': 1000}
  baseURL = "https://clinicaltrials.gov/api/v2/studies"

  r = requests.get(baseURL, params=parameters) #parameters can be plugged into get function; here, we pass in quiery of 'ANDs and ORs' and page limit
  if r.status_code != 200:
     print(f"HTTP error: {r.status_code}")
     return pd.DataFrame()
  data = r.json()

  if "studies" in data and isinstance(data["studies"], list):
    studies = data["studies"]
  else:
    return pd.DataFrame(columns=header)



  #under studies, there are different modules we need to go through: identificationModule (has id,title), conditionsModule (has condition), armsInterventionsModule (intervention type and name)
  #design module (phase), statusModule (OverallStatus, StartDate, PrimaryCompletionDate), sponsorCollaboratorsModule (SponsorName), contactsLocationsModule (LocationCountry)
  #ALL ARE UNDER PROTOCOLSECTION  MODULE

  fList = []
  #this for loop goes through all clinical trials of interest and finds nuggets of desired information to fill in the dataframe with headers
  for s in studies:
     nct_id = ""
     title = ""
     conditions = ""
     interventionType = ""
     interventionName = ""
     phase = ""
     status = ""
     countries = ""
     leadSponsor = ""
     startDate = ""
     primaryCompletionDate = ""
     link = ""
     if "protocolSection" not in s or type(s["protocolSection"]) != dict:
        continue

     ps = s["protocolSection"] #each study in studies has a ps that corresponds to each trial
     nct_id = ps["identificationModule"]['nctId']
     if 'briefTitle' in ps["identificationModule"].keys():
        title = ps["identificationModule"]['briefTitle']
     elif "officialTitle" in ps["identificationModule"].keys():
        title = ps["identificationModule"]['officialTitle']
     else:
        title = ''

     conditions = listJoiner(ps['conditionsModule']['conditions'])
     try:
      interventions = ps["armsInterventionsModule"]['interventions']
      interventionTypeList = []
      interventionNameList = []
      for iv in interventions:
          if type(iv) == dict:
            interventionTypeList.append(iv['type'])
            interventionNameList.append(iv['name'])
      interventionType = listJoiner(interventionTypeList)
      interventionName = listJoiner(interventionNameList)
     except:
        interventionType = None
        interventionName = None

     try:
      phaseList = ps['designModule']['phases']
      phase = listJoiner(phaseList)
     except:
      phase = None

      #below breaks easily
     
     #try:
     # status = ps['statusModule']['overallStatus']
    # except:
     # status = None
    # try:
    #  startDate = ps['statusModule']['overallStatus']["startDateStruct"]["date"]
    # except:
    #  startDate = None
    # try:
     # primaryCompletionDate = ps['statusModule']['overallStatus']["primaryCompletionDateStruct"]["date"]
    # except:
     # primaryCompletionDate = None
      

     if "statusModule" in ps and type(ps['statusModule']) == dict:
        status_mod = ps['statusModule']
        if "overallStatus" in status_mod:
          status = status_mod["overallStatus"]
        if "startDateStruct" in status_mod and type(status_mod["startDateStruct"]) == dict:
          sds = status_mod["startDateStruct"]
          if "date" in sds:
              startDate = sds["date"]

        if "primaryCompletionDateStruct" in status_mod and type(status_mod["primaryCompletionDateStruct"]) == dict:
          pcds = status_mod["primaryCompletionDateStruct"]
          if "date" in pcds:
              primaryCompletionDate = pcds["date"]

     try:
      leadSponsor = ps["sponsorCollaboratorsModule"]["leadSponsor"]["name"]
     except:
      leadSponsor = None

    #below breaks easily
     
     #try:
      #countryLocation = ps["contactsLocationsModule"]["locations"]['country']
      #countryLocationList = []
     # for country in countryLocation:
      #    if country not in countryLocationList:
     #       countryLocationList.append(country)
      #    else:
     #       continue
     # countries = listJoiner(countryLocationList)
     #except:
    #    countries = None
    

     if "contactsLocationsModule" in ps and type(ps["contactsLocationsModule"]) == dict:
      loc_mod = ps["contactsLocationsModule"]
      if "locations" in loc_mod and type(loc_mod["locations"]) == list:
        countryLocationList = []
        for loc in loc_mod["locations"]:
            if type(loc) == dict and "country" in loc:
                c = loc["country"]
                if c and (c not in countryLocationList):
                    countryLocationList.append(c)
        countries = listJoiner(countryLocationList)

     if nct_id != None:
        link = f"https://clinicaltrials.gov/study/{nct_id}"

     fList.append({
      "NCTId": nct_id,
      "Title": title,
      "Condition": conditions,
      "InterventionType": interventionType,
      "InterventionName": interventionName,
      "Phase": phase,
      "OverallStatus": status,
      "LocationCountry": countries,
      "SponsorName": leadSponsor,
      "StartDate": startDate,
      "PrimaryCompletionDate": primaryCompletionDate,
      "Link": link})
  raw_df = pd.DataFrame(fList, columns=header)
  return raw_df

#ts EXPLODES the dfs
   
#---------------------------------------------------------------------------------------------------------------------------
#INPUT ORGANIZER

#this below accounts for if this is the first ever query
if submitted1 and st.session_state["expr"] == None:
  st.session_state['broad_category_label'] = broad_category
  st.session_state['broad_category'] = BC_mapper[broad_category]
  st.session_state['key_words'] = unique_keyword_list
  st.session_state["unique_keyword_string"] = unique_keyword_string #string version of unique_keyword_list
  if not st.session_state["unique_keyword_string"]:
    st.session_state['expr'] = st.session_state['broad_category']
  else:
    st.session_state['expr'] = st.session_state['broad_category'] + " AND " + st.session_state['unique_keyword_string'][:-5]
  st.session_state['raw_df'] = dfCreator(st.session_state['expr'])
  st.session_state['filtered_df'] = dfCreator(st.session_state['expr'])
  st.session_state['rDFkey'] = f"(RAW) {st.session_state['broad_category_label']} | {st.session_state['unique_keyword_string'][:-5]}"
  st.session_state['fDFkey'] = f"(FILTERED) {st.session_state['broad_category_label']} | {st.session_state['unique_keyword_string'][:-5]}"
  #st.write(f"{len(st.session_state['raw_df'])} Trials Found")



#this below takes old dfs and appends them to past queires so chatbot can use past user queires in future
elif submitted1:
  raw_key = f"(RAW) {st.session_state['broad_category_label']} | {st.session_state['unique_keyword_string'][:-5]}"
  filt_key = f"(FILTERED) {st.session_state['broad_category_label']} | {st.session_state['unique_keyword_string'][:-5]}"
  entry = [
    {raw_key: st.session_state["raw_df"]},
    {filt_key: st.session_state["filtered_df"]}]
  st.session_state["past_queries"].append(entry)
  #"past queires" session state contains sublists of old queieries
  st.session_state['broad_category_label'] = broad_category
  st.session_state['broad_category'] = BC_mapper[broad_category]
  st.session_state['key_words'] = unique_keyword_list
  st.session_state["unique_keyword_string"] = unique_keyword_string
  if not st.session_state["unique_keyword_string"]:
    st.session_state['expr'] = st.session_state['broad_category']
  else:
    st.session_state['expr'] = st.session_state['broad_category'] + " AND " + st.session_state['unique_keyword_string'][:-5]
  st.session_state['raw_df'] = dfCreator(st.session_state['expr'])
  st.session_state['filtered_df'] = dfCreator(st.session_state['expr'])
  st.session_state['rDFkey'] = f"(RAW) {st.session_state['broad_category_label']} | {st.session_state['unique_keyword_string'][:-5]}"
  st.session_state['fDFkey'] = f"(FILTERED) {st.session_state['broad_category_label']} | {st.session_state['unique_keyword_string'][:-5]}"
  #st.write(f"{len(st.session_state['raw_df'])} Trials Found")
  #st.write(st.session_state["past_queries"])
#---------------------------------------------------------------------------------------------------------------------------
#GRAPHER
#since some things are seperated by semicolons, we need to explode them (cant use .split because itll just create a list, each value in string needs a weight)

#make a pie chart with phase distribution (can use raw df for this always)
#make a bar graph with status distribution (can use raw df for this always)
#------------------------------------------------------------------------------------------------------
#CONSTRAINT SELECTION
with st.form("constrainer"):
  st.write("For the graphs below, feel free to add constraints to get better visualizations! Please enter the phases and/or statuses that you want to consider.")
  phaseFilter = st.multiselect("Please enter the phases that you only want to consider.", [
    "Phase1",
    "Phase2",
    "Phase3",
    "Phase4",
    "Early_Phase1",
    "Not_Applicable",
    "NA"

])
  statusFilter = st.multiselect("Please enter the statuses that you only want to consider.", [
    "Not_yet_recruiting",
    "Recruiting",
    "Enrolling_by_invitation",
    "Active_not_recruiting",
    "Completed",
    "Suspended",
    "Terminated",
    "Withdrawn",
    "Unknown_status"
])
  submitted2 = st.form_submit_button("Enter")



if submitted2:
    #st.write(f"{len(st.session_state['filtered_df'])} Trials Found")
    cleaned_phases = []
    for p in phaseFilter:
        cleaned_phases.append(p.lower().strip())
    st.session_state["phase_filter"] = cleaned_phases

    cleaned_statuses = []
    for s in statusFilter:
        cleaned_statuses.append(s.lower().strip())
    st.session_state["status_filter"] = cleaned_statuses
    df = st.session_state['raw_df'].copy()
    desired_rows = []
    #st.write(st.session_state['filtered_df']['Phase'])
    #st.write(st.session_state['filtered_df']['OverallStatus'])

    if not st.session_state["phase_filter"] and not st.session_state["status_filter"]:
       filtered_df = df.copy()
       st.session_state['filtered_df'] = filtered_df
       if filtered_df.empty: #filtered df is empty thats why this error is coming
          st.warning("No trials matched your filters.\nPlease adjust the constraints")
       else:
          st.write(f"{len(st.session_state['filtered_df'])} trials match your filters")


    elif st.session_state["phase_filter"] and not st.session_state["status_filter"]:
       for i in range(len(df)):
          row = df.iloc[i]
          phaseOfrow = row['Phase']
          phaseOfrowL = str(phaseOfrow).split('; ')
          for item in phaseOfrowL:
             if item.lower().strip() in st.session_state["phase_filter"]:
                desired_rows.append(row)
                break
       st.session_state['filtered_df'] = pd.DataFrame(desired_rows)
       if st.session_state['filtered_df'].empty: #filtered df is empty thats why this error is coming
          st.warning("No trials matched your filters.\nPlease adjust the constraints")
       else:
          st.write(f"{len(st.session_state['filtered_df'])} trials match your filters")


    elif not st.session_state["phase_filter"] and st.session_state["status_filter"]:
       for i in range(len(df)):
          row = df.iloc[i]
          statusOfrow = row['OverallStatus']
          statusOfrowL = str(statusOfrow).split('; ')
          for item in statusOfrowL:
             if item.lower().strip() in st.session_state["status_filter"]:
                desired_rows.append(row)
                break
       st.session_state['filtered_df'] = pd.DataFrame(desired_rows)
       if st.session_state['filtered_df'].empty: #filtered df is empty thats why this error is coming
          st.warning("No trials matched your filters.\nPlease adjust the constraints")
       else:
          st.write(f"{len(st.session_state['filtered_df'])} trials match your filters")



    elif st.session_state["phase_filter"] and st.session_state["status_filter"]:
       for i in range(len(df)):
          row = df.iloc[i]
          phaseOfrow = row['Phase']
          statusOfrow = row['OverallStatus']
          phaseOfrowL = str(phaseOfrow).split('; ')
          statusOfrowL = str(statusOfrow).split('; ')
          match_found_for_trial = False
          for item1 in phaseOfrowL:
             for item2 in statusOfrowL:
                if item1.lower().strip() in st.session_state["phase_filter"] and item2.lower().strip() in st.session_state["status_filter"]:
                   desired_rows.append(row)
                   match_found_for_trial = True
                   break
             if match_found_for_trial:
                break
       st.session_state['filtered_df'] = pd.DataFrame(desired_rows)
       if st.session_state['filtered_df'].empty: #filtered df is empty thats why this error is coming
          st.warning("No trials matched your filters.\nPlease adjust the constraints")
       else:
          st.write(f"{len(st.session_state['filtered_df'])} trials match your filters")
  

if st.session_state.get('raw_df') is not None and not st.session_state['raw_df'].empty:
    st.write(f"**Total Fetched Trials (Unfiltered): {len(st.session_state['raw_df'])}**")


#---------------------------------------------------------------------------------------------------------
#pie chart showing phase and status spread
st.divider()
if st.session_state['filtered_df'] is not None and not st.session_state['filtered_df'].empty:
   st.subheader('Distribution of Phase/Status Between all Trials')
   temp = st.session_state["raw_df"].copy()
   temp['Phase'] = temp['Phase'].apply(lambda x: str(x).lower().strip().split('; '))
   temp['OverallStatus'] = temp['OverallStatus'].apply(lambda x: str(x).lower().strip().split('; '))
   temp = temp.explode("Phase").explode('OverallStatus')
   temp['Phase'] = temp['Phase'].str.strip()
   temp['OverallStatus'] = temp['OverallStatus'].str.strip()
   
   phase_counts = temp["Phase"].value_counts().reset_index()
   status_counts = temp["OverallStatus"].value_counts().reset_index()
   phase_counts.columns = ['Phase', 'Count']
   status_counts.columns = ['Status', 'Count']

   fig_phase = px.pie(
        phase_counts,
        values='Count',
        names='Phase',
        title='Distribution of Trial Phases (By Trial Count)',
        hole=.1, # Creates a donut chart for better readability
        color_discrete_sequence=px.colors.sequential.RdBu
    )
   
   fig_status = px.pie(
        status_counts,
        values='Count',
        names='Status',
        title='Distribution of Trial Statuses (By Trial Count)',
        hole=.1, # Creates a donut chart for better readability
        color_discrete_sequence=px.colors.sequential.RdBu
    )
   st.plotly_chart(fig_phase, use_container_width=True)
   st.plotly_chart(fig_status, use_container_width=True)
else:
    st.warning("No data available to plot. Please run a query and apply filters.")

#bar chart with intervention types
st.divider()
if st.session_state['filtered_df'] is not None and not st.session_state['filtered_df'].empty:
   d = st.session_state['filtered_df'].copy()
   d["InterventionType"] = d["InterventionType"].apply(lambda x: str(x).lower().strip().split('; '))
   d = d.explode("InterventionType")
   d["InterventionType"] = d["InterventionType"].str.strip()

   interventionCounts = d["InterventionType"].value_counts().reset_index()
   interventionCountsColumns = ['InterventionType', 'count']
   st.subheader('Distribution of Intervention Modalities')
   fig_interv = px.bar(
        interventionCounts,
        x='InterventionType',
        y='count',
        labels={'InterventionType': 'Intervention Modality', 'Count': 'Number of Trials'},
        color_continuous_scale=px.colors.sequential.Teal
    )
   fig_interv.update_xaxes(categoryorder='total descending')
   st.plotly_chart(fig_interv, use_container_width=True)
else:
    st.warning("No data available to plot. Please run a query and apply filters.")

#plots by geography
st.divider()
if st.session_state['filtered_df'] is not None and not st.session_state['filtered_df'].empty:
    tempDf = st.session_state['filtered_df'].copy()
    tempDf["LocationCountry"] = tempDf["LocationCountry"].apply(lambda x: str(x).lower().strip().split('; '))
    tempDf = tempDf.explode("LocationCountry")
    tempDf["LocationCountry"] = tempDf['LocationCountry'].str.strip()
    
    #essentially finds value count for each country and creates a df mapping each country to count
    country_counts = tempDf["LocationCountry"].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count'] 
    
    st.subheader("Trials by Location Country")
    fig_map = px.choropleth(
        country_counts,
        locations='Country',
        locationmode='country names', 
        color='Count',
        
        hover_name='Country', 
        
        color_continuous_scale=px.colors.sequential.Plasma,
        title='Trial Count by Country')
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("No data available to plot. Please run a query and apply filters.")

#plots trials by each sponsor
st.divider()
if st.session_state['filtered_df'] is not None and not st.session_state['filtered_df'].empty: #proper conditional check to make sure its all there in the df
    sponsor_counts = st.session_state['filtered_df']["SponsorName"].value_counts() #value_counts goes in the sponsorname category and counts each sponsor and stores

    st.subheader("Number of Trials by Sponsor")
    st.bar_chart(sponsor_counts)
else:
    st.warning("No data available to plot. Please run a query and apply filters.")

#trial duration histogram (end-start)
st.divider()
if st.session_state['filtered_df'] is not None and not st.session_state['filtered_df'].empty:
   st.subheader("Trial Duration Visualizer")
   c = st.session_state["filtered_df"].copy()
   #to_datetime converts dates to a pandas usable object (can do subtraction and stuff)
   c["StartDate"] = pd.to_datetime(c['StartDate'], format='ISO8601')
   c["PrimaryCompletionDate"] = pd.to_datetime(c["PrimaryCompletionDate"], format='ISO8601')
   #dt.days converts to days
   c["DurationDays"] = (c["PrimaryCompletionDate"] - c["StartDate"]).dt.days
   #these bottom three are for cleaning (makes sure days is positive and less than 25)
   c = c.dropna(subset=['DurationDays'])
   c = c[c['DurationDays'] > 0]
   c = c[c['DurationDays'] < 365.25 * 25]
   c['Duration_Years'] = c['DurationDays'] / 365.25

   if not c.empty:
      fig_duration = px.histogram(
            c,
            x='Duration_Years',
            #nbins=20, # Determines the number of bars/bins in the histogram
            title='Distribution of Estimated Trial Durations (Years)',
            labels={'Duration_Years': 'Trial Duration (Years)', 'count': 'Number of Trials'},
            color_discrete_sequence=['#FF7F0E']
        )

      st.plotly_chart(fig_duration, use_container_width=True)
else:
   st.warning("No data available to plot. Please run a query and apply filters.")
   
#---------------------------------------------------------------------------------------------------------------------------
# since clinicaltrials.gov API does not categorize by these, we can search for trials by 'broad' AND {user-specific keyword input}
# this will ensure that the broad category is present in the search AND any really specific thing that the user wants is also there
# we will need to map each broad category to a bunch of smaller terms (cartilage can be cartilage, chondro, etc.)
#^^^^^^^^^^^^old planning thoughts





