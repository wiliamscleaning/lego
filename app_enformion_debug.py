
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
def lookup_phone_enformion(address, city, state, zip_code, first_name=None, last_name=None):
    headers = {
        "galaxy-ap-name": GALAXY_PROFILE_NAME,
        "galaxy-ap-password": GALAXY_PROFILE_PASSWORD,
        "galaxy-client-type": GALAXY_CLIENT_TYPE,
        "galaxy-search-type": GALAXY_SEARCH_TYPE
    }
    payload = {
        "FirstName": first_name,
        "LastName": last_name,
        "AddressLine1": address,
        "AddressLine2": f"{city}, {state}, {zip_code}"
    }
    try:
        response = requests.post(ENFORMION_URL, json=payload, headers=headers)
        if response.status_code != 200:
            return f"HTTP {response.status_code}: {response.text.strip()}"
        try:
            data = response.json()
            st.subheader("📦 Raw API Response")
            st.json(data)

            # Try multiple paths to find a phone number
            if "Phones" in data:
                phones = data["Phones"]
            elif "Results" in data and isinstance(data["Results"], list):
                phones = data["Results"][0].get("Phones", [])
            else:
                phones = []

            return phones[0]["PhoneNumber"] if phones else "Not found"
        except Exception as e:
            return f"Invalid JSON: {response.text.strip()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("📞 Enformion Galaxy Lookup (Debug Mode)")

uploaded_file = st.file_uploader("Upload your CSV (must include Property Address, City, State, ZIP, optionally First/Last Name)", type="csv")

if uploaded_file:
    leads_df = pd.read_csv(uploaded_file)

    required = {"Property Address", "City", "State", "ZIP"}
    missing = required - set(leads_df.columns)
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}")
    else:
        st.write("📄 Preview of uploaded leads:")
        st.dataframe(leads_df.head())

        if st.button("🔍 Append Phone Numbers"):
            with st.spinner("Querying Enformion for each row..."):
                leads_df["Phone"] = leads_df.apply(
                    lambda row: lookup_phone_enformion(
                        address=row["Property Address"],
                        city=row["City"],
                        state=row["State"],
                        zip_code=row["ZIP"],
                        first_name=row["First Name"] if "First Name" in row else None,
                        last_name=row["Last Name"] if "Last Name" in row else None
                    ), axis=1
                )
            st.success("✅ Phone numbers appended!")
            st.write(leads_df)

            csv = leads_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download CSV with Phones",
                data=csv,
                file_name="leads_with_phones_debug.csv",
                mime="text/csv"
            )
