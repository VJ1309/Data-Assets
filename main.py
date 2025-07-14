import streamlit as st
import pandas as pd

# Sample mock data for demonstration
mock_data = pd.DataFrame([
    {
        "Asset Name": "customer_raw",
        "Layer": "L0",
        "Owner": "dataops@company.com",
        "Domain": "Deliver",
        "SLA": "Daily",
        "PII": True,
        "Schema": "customer_id:INT, name:STRING, phone:STRING",
        "Transformation": "Raw ingestion from CRM API.",
        "DQ Rules": "Non-null customer_id; phone must match regex.",
        "Sensitivity": "Confidential",
        "Lineage": "CRM_API -> L0.customer_raw",
        "Refresh": "Ingested every midnight",
        "Last Updated": "2025-07-11"
    },
    {
        "Asset Name": "customer_cleaned",
        "Layer": "L1",
        "Owner": "dataengineering@company.com",
        "Domain": "Deliver",
        "SLA": "Daily",
        "PII": True,
        "Schema": "customer_id:INT, full_name:STRING, email:STRING",
        "Transformation": "Cleansing and deduplication of raw data.",
        "DQ Rules": "Valid email pattern; unique customer_id",
        "Sensitivity": "Confidential",
        "Lineage": "L0.customer_raw -> L1.customer_cleaned",
        "Refresh": "Every 2 AM",
        "Last Updated": "2025-07-11"
    }
])

st.set_page_config(layout="wide")
st.title("🧾 Data Lake Assets Functional Specification")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")
selected_layer = st.sidebar.multiselect("Select Layer", options=["L0", "L1", "L2"])
selected_domain = st.sidebar.multiselect("Select Domain", options=["Plan", "Deliver", "Procurement"])
pii_filter = st.sidebar.selectbox("Contains PII?", options=["All", "Yes", "No"])

# Apply filters
filtered_data = mock_data[
    mock_data["Layer"].isin(selected_layer) & 
    mock_data["Domain"].isin(selected_domain)
]

if pii_filter == "Yes":
    filtered_data = filtered_data[filtered_data["PII"] == True]
elif pii_filter == "No":
    filtered_data = filtered_data[filtered_data["PII"] == False]

# --- Main Table ---
st.subheader("📂 Available Data Assets")
selected_row = st.dataframe(filtered_data[["Asset Name", "Layer", "Owner", "SLA", "Last Updated"]], use_container_width=True)

# --- Detail Viewer ---
st.subheader("🔎 Specification Details")

if not filtered_data.empty:
    selected_asset = st.selectbox("Select an Asset to View Details", options=filtered_data["Asset Name"].tolist())
    asset_details = filtered_data[filtered_data["Asset Name"] == selected_asset].iloc[0]

    st.markdown(f"### 📌 **{asset_details['Asset Name']}** ({asset_details['Layer']})")
    st.markdown(f"**Owner**: {asset_details['Owner']}  \n**Domain**: {asset_details['Domain']}  \n**SLA**: {asset_details['SLA']}  \n**Contains PII**: {'Yes' if asset_details['PII'] else 'No'}")

    with st.expander("📐 Schema"):
        st.code(asset_details["Schema"])

    with st.expander("🔄 Transformation Logic"):
        st.markdown(asset_details["Transformation"])

    with st.expander("✅ Data Quality Rules"):
        st.markdown(asset_details["DQ Rules"])

    with st.expander("🔐 Access Control"):
        st.markdown(f"**Sensitivity**: {asset_details['Sensitivity']}")

    with st.expander("⚙️ Operational Metadata"):
        st.markdown(f"**Lineage**: {asset_details['Lineage']}  \n**Refresh Strategy**: {asset_details['Refresh']}  \n**Last Updated**: {asset_details['Last Updated']}")

else:
    st.warning("No data assets found for the selected filters.")

