
import streamlit as st
import pandas as pd
import requests

# Endato API key
ENDATO_API_KEY = "7dd6a024318044ab9f88c0dc405d52de"
ENDATO_URL = "https://api.endato.com/v2/identity/address"

# Lookup phone number using Endato
def lookup_phone_endato(address):
    try:
        payload = {
            "address": address,
            "city": "Orlando",
            "state": "FL"
        }
        headers = {
            "x-api-key": ENDATO_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(ENDATO_URL, json=payload, headers=headers)
        if response.status_code != 200:
            return f"HTTP {response.status_code}: {response.text.strip()}"
        try:
            data = response.json()
            phones = data.get("phones", [])
            return phones[0].get("number") if phones else "Not found"
        except Exception as e:
            return f"Invalid JSON: {response.text.strip()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("📞 Upload Leads and Append Phone Numbers")

uploaded_file = st.file_uploader("Upload your lead CSV (with address columns)", type="csv")

if uploaded_file:
    leads_df = pd.read_csv(uploaded_file)

    if "Property Address" not in leads_df.columns:
        st.error("CSV must contain a 'Property Address' column.")
    else:
        st.write("📄 Preview of uploaded leads:")
        st.dataframe(leads_df.head())

        if st.button("🔍 Append Phone Numbers"):
            with st.spinner("Looking up phone numbers via Endato..."):
                leads_df["Phone"] = leads_df["Property Address"].apply(lookup_phone_endato)

            st.success("✅ Phone numbers appended!")
            st.write(leads_df)

            csv = leads_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download CSV with Phones",
                data=csv,
                file_name="leads_with_phones.csv",
                mime="text/csv"
            )
