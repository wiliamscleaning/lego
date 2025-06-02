
import streamlit as st
import pandas as pd
import requests

# Enformion Galaxy API credentials (REPLACE THESE)
GALAXY_PROFILE_NAME = "your-profile-name"
GALAXY_PROFILE_PASSWORD = "your-profile-password"
GALAXY_CLIENT_TYPE = "Python"
GALAXY_SEARCH_TYPE = "PropertyV2"
ENFORMION_URL = "https://devapi.enformion.com/PropertyV2Search"

# Lookup phone number via Enformion Galaxy API
def lookup_phone_enformion(address, city, state, zip_code):
    headers = {
        "galaxy-ap-name": GALAXY_PROFILE_NAME,
        "galaxy-ap-password": GALAXY_PROFILE_PASSWORD,
        "galaxy-client-type": GALAXY_CLIENT_TYPE,
        "galaxy-search-type": GALAXY_SEARCH_TYPE
    }
    payload = {
        "FirstName": None,
        "LastName": None,
        "AddressLine1": address,
        "AddressLine2": f"{city}, {state}, {zip_code}"
    }
    try:
        response = requests.post(ENFORMION_URL, json=payload, headers=headers)
        if response.status_code != 200:
            return f"HTTP {response.status_code}: {response.text.strip()}"
        try:
            data = response.json()
            # You may need to adjust parsing logic based on real response structure
            phones = data.get("Phones", [])
            return phones[0]["PhoneNumber"] if phones else "Not found"
        except Exception as e:
            return f"Invalid JSON: {response.text.strip()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("📞 Upload Leads and Append Phone Numbers (Enformion Galaxy)")

uploaded_file = st.file_uploader("Upload your lead CSV (with Property Address, City, State, ZIP)", type="csv")

if uploaded_file:
    leads_df = pd.read_csv(uploaded_file)

    required_cols = {"Property Address", "City", "State", "ZIP"}
    if not required_cols.issubset(leads_df.columns):
        st.error(f"CSV must contain columns: {', '.join(required_cols)}")
    else:
        st.write("📄 Preview of uploaded leads:")
        st.dataframe(leads_df.head())

        if st.button("🔍 Append Phone Numbers"):
            with st.spinner("Looking up phone numbers via Enformion..."):
                leads_df["Phone"] = leads_df.apply(
                    lambda row: lookup_phone_enformion(
                        row["Property Address"],
                        row["City"],
                        row["State"],
                        row["ZIP"]
                    ), axis=1
                )

            st.success("✅ Phone numbers appended!")
            st.write(leads_df)

            csv = leads_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download CSV with Phones",
                data=csv,
                file_name="leads_with_phones.csv",
                mime="text/csv"
            )
