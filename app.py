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


# --------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------

def format_km(value):
    return f"{value:,.0f}".replace(",", ".") + " km"


def format_date(date_value):
    year, month, day = date_value.split("-")
    return f"{day}.{month}.{year}"


# --------------------------------------------------
# Navigation
# --------------------------------------------------

st.sidebar.title("Digital Twin")
st.sidebar.caption("Automotive After-Sales")

st.sidebar.divider()

st.sidebar.write(f"**Fahrzeug:** {vehicle['vehicle_id']}")

seite = st.sidebar.radio(
    "Navigation",
    [
        "🚗 Fahrzeugübersicht",
        "🔧 Bremszustand & Prognose",
        "📈 Simulation",
        "👤 Serviceinformation"
    ]
)

st.sidebar.divider()

st.sidebar.write("**Aktueller Status**")
st.sidebar.success(f"● {brakes['status']}")

st.sidebar.caption("Demonstrator mit synthetischen Fahrzeugdaten")


# --------------------------------------------------
# SCREEN 1 – FAHRZEUGÜBERSICHT
# --------------------------------------------------

if seite == "🚗 Fahrzeugübersicht":

    st.title("Digital Twin – Automotive After-Sales")

    st.caption(
        "Prototypischer Demonstrator zur Unterstützung eines "
        "datenbasierten After-Sales-Serviceprozesses"
    )

    st.info("Demonstrator – ausschließlich synthetische Fahrzeugdaten")

    # Fahrzeug und Gesamtstatus
    col_vehicle, col_status = st.columns([3, 1])

    with col_vehicle:
        st.subheader(f"Fahrzeug {vehicle['vehicle_id']}")

    with col_status:
        st.write("**Aktueller Status**")
        st.success(f"● {brakes['status']}")

    # Kennzahlen
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
            format_date(brakes["measurement_date"])
        )

    st.divider()

    # Fahrzeug- und Zustandsinformationen
    col_info, col_condition = st.columns(2)

    with col_info:
        st.subheader("🚗 Fahrzeuginformationen")

        st.write(f"**Fahrzeug-ID:** {vehicle['vehicle_id']}")
        st.write(f"**Modell:** {vehicle['model']}")
        st.write(f"**Baujahr:** {vehicle['year']}")
        st.write("**Antrieb:** Elektro")
        st.write(
            f"**Kilometerstand:** "
            f"{format_km(vehicle['mileage_km'])}"
        )

    with col_condition:
        st.subheader("🔧 Aktueller Bremszustand")

        st.metric(
            "Restzustand Bremsbelag",
            f"{brakes['brake_pad_condition_percent']} %"
        )

        st.write(f"**Status:** {brakes['status']}")
        st.write(
            f"**Messzeitpunkt:** "
            f"{format_date(brakes['measurement_date'])}"
        )

    st.divider()

    # Servicehistorie
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

    service_df["Datum"] = service_df["Datum"].apply(format_date)

    service_df["Kilometerstand"] = (
        service_df["Kilometerstand"].apply(format_km)
    )

    # Englische Inhalte der bisherigen JSON-Datei
    # für die sichtbare Oberfläche übersetzen
    service_df["Service"] = service_df["Service"].replace({
        "Inspection": "Inspektion",
        "Brake inspection": "Bremsenprüfung"
    })

    service_df["Ergebnis"] = service_df["Ergebnis"].replace({
        "No brake service required":
            "Kein Bremsenservice erforderlich",
        "Brake condition monitored":
            "Bremszustand weiter beobachten"
    })

    st.dataframe(
        service_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Die dargestellten Fahrzeug-, Zustands- und Servicedaten "
        "sind synthetische Daten des Demonstrators."
    )


# --------------------------------------------------
# SCREEN 2 – BREMSZUSTAND & PROGNOSE
# --------------------------------------------------

elif seite == "🔧 Bremszustand & Prognose":

    st.title("Bremszustand & Prognose")
    st.info("Diese Ansicht wird im nächsten Schritt aufgebaut.")


# --------------------------------------------------
# SCREEN 3 – SIMULATION
# --------------------------------------------------

elif seite == "📈 Simulation":

    st.title("Simulation der Zustandsentwicklung")
    st.info("Diese Ansicht wird anschließend aufgebaut.")


# --------------------------------------------------
# SCREEN 4 – SERVICEINFORMATION
# --------------------------------------------------

elif seite == "👤 Serviceinformation":

    st.title("Serviceinformation")
    st.info("Diese Ansicht wird anschließend aufgebaut.")
