
import streamlit as st
import pandas as pd
import requests

# Enformion API settings
ENFORMION_API_KEY = "your-enformion-api-key-here"  # Replace this with your real API key
ENFORMION_URL = "https://api.enformion.com/v2/people/search"  # Confirm this with Enformion docs

# Lookup phone number using Enformion
def lookup_phone_enformion(address, zip_code):
    try:
        payload = {
            "address": address,
            "city": "Orlando",
            "state": "FL",
            "zip": zip_code
        }
        headers = {
            "Authorization": f"Bearer {ENFORMION_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(ENFORMION_URL, json=payload, headers=headers)
        if response.status_code != 200:
            return f"HTTP {response.status_code}: {response.text.strip()}"
        try:
            data = response.json()
            # Example structure – adjust based on actual API response
            phones = data.get("phones", [])
            return phones[0]["number"] if phones else "Not found"
        except Exception as e:
            return f"Invalid JSON: {response.text.strip()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("📞 Upload Leads and Append Phone Numbers (Enformion)")

uploaded_file = st.file_uploader("Upload your lead CSV (with 'Property Address' and 'ZIP')", type="csv")

if uploaded_file:
    leads_df = pd.read_csv(uploaded_file)

    if "Property Address" not in leads_df.columns or "ZIP" not in leads_df.columns:
        st.error("CSV must contain both 'Property Address' and 'ZIP' columns.")
    else:
        st.write("📄 Preview of uploaded leads:")
        st.dataframe(leads_df.head())

        if st.button("🔍 Append Phone Numbers"):
            with st.spinner("Looking up phone numbers via Enformion..."):
                leads_df["Phone"] = leads_df.apply(
                    lambda row: lookup_phone_enformion(row["Property Address"], str(row["ZIP"])), axis=1
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
