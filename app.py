import json
import pandas as pd
import streamlit as st

# --------------------------------------------------
# Seiteneinstellungen
# --------------------------------------------------

st.set_page_config(
    page_title="Digital Twin After-Sales",
    page_icon="🚗",
    layout="wide"
)

# --------------------------------------------------
# Daten laden
# --------------------------------------------------

with open("data/vehicle_data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

vehicle = data["vehicle"]
brakes = data["brakes"]
service_history = data["service_history"]

# Deutsche Formatierung für Kilometerstände
def format_km(value):
    return f"{value:,.0f}".replace(",", ".") + " km"


# --------------------------------------------------
# Titel
# --------------------------------------------------

st.title("Digital Twin - Automotive After-Sales")

st.caption(
    "Prototypischer Demonstrator zur Unterstützung eines "
    "datenbasierten After-Sales-Serviceprozesses"
)

st.info("Demonstrator - ausschließlich synthetische Fahrzeugdaten")


# --------------------------------------------------
# Fahrzeug und Gesamtstatus
# --------------------------------------------------

col_vehicle, col_status = st.columns([3, 1])

with col_vehicle:
    st.subheader(f"Fahrzeug {vehicle['vehicle_id']}")

with col_status:
    st.write("**Aktueller Status**")
    st.success(f"● {brakes['status']}")


# --------------------------------------------------
# Kennzahlen
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Kilometerstand",
        format_km(vehicle["mileage_km"])
    )

with col2:
    st.metric(
        "Bremsbelagzustand",
        f"{brakes['brake_pad_condition_percent']} %"
    )

with col3:
    st.metric(
        "Letzte Aktualisierung",
        brakes["measurement_date"]
    )

st.divider()


# --------------------------------------------------
# Fahrzeug- und Zustandsinformationen
# --------------------------------------------------

col_info, col_condition = st.columns(2)

with col_info:
    st.subheader("🚗 Fahrzeuginformationen")

    st.write(f"**Fahrzeug-ID:** {vehicle['vehicle_id']}")
    st.write(f"**Modell:** {vehicle['model']}")
    st.write(f"**Baujahr:** {vehicle['year']}")
    st.write(f"**Antrieb:** {vehicle['drivetrain']}")
    st.write(f"**Kilometerstand:** {format_km(vehicle['mileage_km'])}")

with col_condition:
    st.subheader("🔧 Aktueller Bremszustand")

    st.metric(
        "Restzustand Bremsbelag",
        f"{brakes['brake_pad_condition_percent']} %"
    )

    st.write(f"**Status:** {brakes['status']}")
    st.write(f"**Messzeitpunkt:** {brakes['measurement_date']}")

st.divider()


# --------------------------------------------------
# Servicehistorie
# --------------------------------------------------

st.subheader("📋 Servicehistorie")

service_df = pd.DataFrame(service_history)

service_df = service_df.rename(
    columns={
        "date": "Datum",
        "mileage_km": "Kilometerstand",
        "service_type": "Service",
        "result": "Ergebnis"
    }
)

service_df["Kilometerstand"] = (
    service_df["Kilometerstand"]
    .apply(format_km)
)

st.dataframe(
    service_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Die dargestellten Fahrzeug-, Zustands- und Servicedaten "
    "sind synthetische Daten des Demonstrators."
)
