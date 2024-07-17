import streamlit as st
from urllib.request import urlopen
from json import loads
import openai
from urllib.error import HTTPError

# Function to fetch data from various sources
@st.cache_data
def fetch_data(source, year=None):
    base_url = "https://educationdata.urban.org/api/v1/college-university/ipeds/"
    if source == "IPEDS Directory":
        url = f"{base_url}directory/{year}/"
    elif source == "IPEDS Institutional Characteristics":
        url = f"{base_url}institutional-characteristics/{year}/"
    elif source == "IPEDS Admissions":
        url = f"{base_url}admissions/{year}/"
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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response.choices[0].message["content"].strip()

# Function to summarize data
def summarize_data(data):
    summary = []
    if isinstance(data, list):
        for entry in data[:10]:  # Limit to first 10 entries for brevity
            summary.append(str(entry)[:1000])  # Limit each entry to 1000 characters
    elif isinstance(data, dict):
        for key, value in list(data.items())[:10]:  # Limit to first 10 key-value pairs for brevity
            summary.append(f"{key}: {str(value)[:1000]}")  # Limit each value to 1000 characters
    return "\n".join(summary)

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
        st.session_state.data = data
        st.write(data)

# Input field for user queries
user_query = st.text_input("Ask something about the data:")

if st.button("Submit Query"):
    if not user_query:
        st.error("Please enter a query.")
    else:
        if 'data' in st.session_state:
            data = st.session_state.data
            summarized_data = summarize_data(data)
            prompt = f"Using the following data: {summarized_data}, answer this question: {user_query}"
            response = query_openai(prompt)
            st.write(response)
        else:
            st.error("No data available. Please fetch data first.")
