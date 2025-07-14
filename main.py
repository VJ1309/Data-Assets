import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- Sample asset metadata --------------------
mock_data = pd.DataFrame([
    {
        "Asset Name": "customer_raw",
        "Layer": "L0",
        "Owner": "dataops@company.com",
        "Domain": "Deliver",
        "SLA": "Daily",
        "PII": True,
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
        "Transformation": "Cleansing and deduplication of raw data.",
        "DQ Rules": "Valid email pattern; unique customer_id",
        "Sensitivity": "Confidential",
        "Lineage": "L0.customer_raw -> L1.customer_cleaned",
        "Refresh": "Every 2 AM",
        "Last Updated": "2025-07-11"
    },
    {
        "Asset Name": "vendor_orders",
        "Layer": "L0",
        "Owner": "procurement@company.com",
        "Domain": "Procurement",
        "SLA": "Daily",
        "PII": False,
        "Transformation": "Flat file ingestion from SFTP.",
        "DQ Rules": "",
        "Sensitivity": "Internal",
        "Lineage": "SFTP -> L0.vendor_orders",
        "Refresh": "Every 4 hours",
        "Last Updated": "2025-07-10"
    }
])

# -------------------- Schema Definitions --------------------
schema_data = {
    "customer_raw": [
        {"Field Name": "customer_id", "Data Type": "INT", "Primary Key": True, "Foreign Key": False, "Nullable": False},
        {"Field Name": "name", "Data Type": "STRING", "Primary Key": False, "Foreign Key": False, "Nullable": True},
        {"Field Name": "phone", "Data Type": "STRING", "Primary Key": False, "Foreign Key": False, "Nullable": True}
    ],
    "customer_cleaned": [
        {"Field Name": "customer_id", "Data Type": "INT", "Primary Key": True, "Foreign Key": False, "Nullable": False},
        {"Field Name": "full_name", "Data Type": "STRING", "Primary Key": False, "Foreign Key": False, "Nullable": True},
        {"Field Name": "email", "Data Type": "STRING", "Primary Key": False, "Foreign Key": False, "Nullable": True}
    ],
    "vendor_orders": [
        {"Field Name": "order_id", "Data Type": "INT", "Primary Key": True, "Foreign Key": False, "Nullable": False},
        {"Field Name": "vendor_id", "Data Type": "STRING", "Primary Key": False, "Foreign Key": True, "Nullable": False},
        {"Field Name": "quantity", "Data Type": "INT", "Primary Key": False, "Foreign Key": False, "Nullable": True}
    ]
}

# -------------------- Streamlit App --------------------
st.set_page_config(layout="wide")
st.title("🧾 Data Lake Assets Functional Specification")

# Page Navigation
page = st.radio("Navigate", ["📊 Dashboard", "📂 Asset Explorer"])

# -------------------- Dashboard Page --------------------
if page == "📊 Dashboard":
    st.header("📊 Summary Dashboard")

    # Asset coverage by domain
    domain_counts = mock_data["Domain"].value_counts().reset_index()
    domain_counts.columns = ["Domain", "Count"]
    domain_counts["Coverage %"] = (domain_counts["Count"] / domain_counts["Count"].sum()) * 100

    fig1 = px.pie(domain_counts, names="Domain", values="Coverage %", title="Asset Coverage by Domain")
    st.plotly_chart(fig1, use_container_width=True)

    # DQ rule coverage
    dq_coverage = mock_data.copy()
    dq_coverage["Has DQ Rules"] = dq_coverage["DQ Rules"].apply(lambda x: "Yes" if x.strip() else "No")
    dq_summary = dq_coverage["Has DQ Rules"].value_counts().reset_index()
    dq_summary.columns = ["DQ Defined", "Count"]
    dq_summary["%"] = (dq_summary["Count"] / dq_summary["Count"].sum()) * 100

    fig2 = px.bar(dq_summary, x="DQ Defined", y="%", text="%", title="Data Quality Coverage", color="DQ Defined")
    fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig2.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig2, use_container_width=True)

# -------------------- Asset Explorer Page --------------------
elif page == "📂 Asset Explorer":
    # Sidebar Filters
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

    # Asset Table
    st.subheader("📂 Available Data Assets")
    st.dataframe(filtered_data[["Asset Name", "Layer", "Owner", "SLA", "Last Updated"]], use_container_width=True)

    # Detail Viewer
    st.subheader("🔎 Specification Details")
    if not filtered_data.empty:
        selected_asset = st.selectbox("Select an Asset to View Details", options=filtered_data["Asset Name"].tolist())
        asset_details = filtered_data[filtered_data["Asset Name"] == selected_asset].iloc[0]

        st.markdown(f"### 📌 **{asset_details['Asset Name']}** ({asset_details['Layer']})")
        st.markdown(f"**Owner**: {asset_details['Owner']}  \n**Domain**: {asset_details['Domain']}  \n**SLA**: {asset_details['SLA']}  \n**Contains PII**: {'Yes' if asset_details['PII'] else 'No'}")

        # Show schema table
        st.markdown("### 🧬 Schema Details")
        schema_df = pd.DataFrame(schema_data[asset_details["Asset Name"]])
        schema_df.insert(0, "Asset Name", asset_details["Asset Name"])
        st.dataframe(schema_df, use_container_width=True)

        # Other spec info
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
