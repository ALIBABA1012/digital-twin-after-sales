import json
import streamlit as st

st.set_page_config(
    page_title="Digital Twin After-Sales",
    page_icon="🚗",
    layout="wide"
)

with open("data/vehicle_data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

vehicle = data["vehicle"]
brakes = data["brakes"]

st.title("Digital Twin - Automotive After-Sales")

st.info("Demonstrator - synthetische Fahrzeugdaten")

st.subheader(f"Fahrzeug {vehicle['vehicle_id']}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Kilometerstand", f"{vehicle['mileage_km']:,} km")

with col2:
    st.metric(
        "Bremsbelagzustand",
        f"{brakes['brake_pad_condition_percent']} %"
    )

with col3:
    st.metric("Status", brakes["status"])

st.divider()

st.write("### Fahrzeuginformationen")
st.write(f"**Modell:** {vehicle['model']}")
st.write(f"**Baujahr:** {vehicle['year']}")
st.write(f"**Antrieb:** {vehicle['drivetrain']}")
