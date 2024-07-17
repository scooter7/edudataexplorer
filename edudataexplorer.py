import streamlit as st
from urllib.request import urlopen
from json import loads
import openai
from urllib.error import HTTPError

# Function to fetch data from various sources
@st.cache_data
def fetch_data(source, year=None):
    base_url = "https://educationdata.urban.org/api/v1/"
    if source == "IPEDS Directory":
        url = f"{base_url}college-university/ipeds/directory/{year}/"
    elif source == "IPEDS Institutional Characteristics":
        url = f"{base_url}college-university/ipeds/institutional-characteristics/{year}/"
    elif source == "IPEDS Admissions":
        url = f"{base_url}college-university/ipeds/admissions/{year}/"
    # Add more endpoints as required
    else:
        return None
    
    try:
        response = urlopen(url)
        data = loads(response.read())
        return data
    except HTTPError as e:
        st.error(f"HTTP Error: {e.code} - {e.reason}")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Function to query OpenAI
def query_openai(prompt):
    openai.api_key = st.secrets["openai"]["api_key"]
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Streamlit app interface
st.title("Education Data Portal Conversational Interface")

# Dropdown menu for selecting the data source
source = st.selectbox(
    "Select the data source:",
    [
        "IPEDS Directory",
        "IPEDS Institutional Characteristics",
        "IPEDS Admissions",
        # Add more sources as required
    ]
)

# Input field for the year, only if relevant for the selected source
if source.startswith("IPEDS"):
    year = st.number_input("Enter the year to fetch data from:", min_value=1980, max_value=2023, step=1, value=2003)

if st.button("Fetch Data"):
    data = fetch_data(source, year)
    if data:
        st.write(data)

# Input field for user queries
user_query = st.text_input("Ask something about the data:")

if st.button("Submit Query"):
    if not user_query:
        st.error("Please enter a query.")
    else:
        prompt = f"Using the following data: {data}, answer this question: {user_query}"
        response = query_openai(prompt)
        st.write(response)
