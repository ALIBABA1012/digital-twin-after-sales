import json
import pandas as pd
import plotly.graph_objects as go
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
# Simulationszustand speichern
# --------------------------------------------------

if "simuliert" not in st.session_state:
    st.session_state.simuliert = False

if "simulierter_zustand" not in st.session_state:
    st.session_state.simulierter_zustand = brakes[
        "brake_pad_condition_percent"
    ]

if "simulierter_status" not in st.session_state:
    st.session_state.simulierter_status = brakes["status"]

if "simulierter_km_stand" not in st.session_state:
    st.session_state.simulierter_km_stand = vehicle["mileage_km"]

if "zusaetzliche_km" not in st.session_state:
    st.session_state.zusaetzliche_km = 0

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
            "Letzte Zustandsmessung",
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

    st.caption(
        "Darstellung des aktuellen Bremsbelagzustands, "
        "des bisherigen Verlaufs und der prognostizierten Entwicklung."
    )

    st.info("Demonstrator – ausschließlich synthetische Fahrzeugdaten")

    # --------------------------------------------------
    # Aktueller Zustand und Prognose
    # --------------------------------------------------

    col_current, col_prediction = st.columns(2)

    with col_current:
        st.subheader("🔧 Aktueller Zustand")

        st.metric(
            "Bremsbelagzustand",
            f"{brakes['brake_pad_condition_percent']} %"
        )

        st.write(f"**Status:** {brakes['status']}")
        st.write(
            f"**Messzeitpunkt:** "
            f"{format_date(brakes['measurement_date'])}"
        )

    with col_prediction:
        st.subheader("📈 Prognose")
    
        VERSCHLEISS_PRO_1000_KM = 5
        GRENZE_SERVICE = 20
    
        aktueller_zustand = brakes["brake_pad_condition_percent"]
    
        if aktueller_zustand > GRENZE_SERVICE:
            benoetigter_verschleiss = (
                aktueller_zustand - GRENZE_SERVICE
            )
    
            wartungsbedarf_km = (
                benoetigter_verschleiss
                / VERSCHLEISS_PRO_1000_KM
            ) * 1000
    
            wartungsbedarf_km = round(
                wartungsbedarf_km / 500
            ) * 500
    
            st.metric(
                "Erwarteter Wartungsbedarf",
                f"in ca. {format_km(wartungsbedarf_km)}"
            )
    
            st.write(
                "**Prognosestatus:** Servicebedarf absehbar"
            )
            
            st.write(
                f"**Hinweis:** Bei gleichbleibender Zustandsentwicklung "
                f"wird in ca. {format_km(wartungsbedarf_km)} "
                f"ein Servicebedarf erwartet."
            )
    
        else:
            st.metric(
                "Erwarteter Wartungsbedarf",
                "Servicebereich erreicht"
            )
    
            st.write(
                "**Prognosestatus:** Service empfohlen"
            )
    
            st.write(
                "**Hinweis:** Der Bremsbelagzustand befindet sich "
                "bereits im definierten Servicebereich."
            )

    st.divider()

    # --------------------------------------------------
    # Zustandsverlauf und Prognose
    # --------------------------------------------------

    st.subheader("📊 Verlauf und Prognose des Bremsbelagzustands")

    # Historische Werte
    historische_km = [
        punkt["mileage_km"]
        for punkt in data["condition_history"]
    ]

    historische_zustaende = [
        punkt["brake_pad_condition_percent"]
        for punkt in data["condition_history"]
    ]

    # Vereinfachte synthetische Prognose
    VERSCHLEISS_PRO_1000_KM = 5

    prognose_km = [
        vehicle["mileage_km"],
        vehicle["mileage_km"] + 1000,
        vehicle["mileage_km"] + 2000,
        vehicle["mileage_km"] + 3000,
        vehicle["mileage_km"] + 4000,
        vehicle["mileage_km"] + 5000
    ]

    prognose_zustaende = [
        max(
            0,
            brakes["brake_pad_condition_percent"]
            - ((km - vehicle["mileage_km"]) / 1000)
            * VERSCHLEISS_PRO_1000_KM
        )
        for km in prognose_km
    ]

    fig = go.Figure()

    # Historischer Verlauf
    fig.add_trace(
        go.Scatter(
            x=historische_km,
            y=historische_zustaende,
            mode="lines+markers",
            name="Historischer Verlauf",
            hovertemplate=(
                "Kilometerstand: %{x:,.0f} km<br>"
                "Bremsbelagzustand: %{y:.0f} %"
                "<extra></extra>"
            )
        )
    )

    # Prognose
    fig.add_trace(
        go.Scatter(
            x=prognose_km,
            y=prognose_zustaende,
            mode="lines+markers",
            name="Prognose",
            line=dict(
                dash="dash"
            ),
            hovertemplate=(
                "Kilometerstand: %{x:,.0f} km<br>"
                "Bremsbelagzustand: %{y:.0f} %"
                "<extra></extra>"
            )
        )
    )

    # Aktuellen Zustand hervorheben
    fig.add_trace(
        go.Scatter(
            x=[vehicle["mileage_km"]],
            y=[brakes["brake_pad_condition_percent"]],
            mode="markers",
            name="Aktueller Zustand",
            marker=dict(
                size=15,
                color="green",
                line=dict(
                    width=2,
                    color="white"
                )
            ),
            hovertemplate=(
                "Kilometerstand: %{x:,.0f} km<br>"
                "Bremsbelagzustand: %{y:.0f} %"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        xaxis=dict(
            title="Kilometerstand [km]",
            tickmode="array",
            tickvals=[
                30000,
                32000,
                34000,
                36000,
                38000,
                40000,
                42000,
                44000,
                46000,
                48000
            ],
            ticktext=[
                "30.000",
                "32.000",
                "34.000",
                "36.000",
                "38.000",
                "40.000",
                "42.000",
                "44.000",
                "46.000",
                "48.000"
            ]
        ),
        yaxis=dict(
            title="Bremsbelagzustand [%]",
            range=[0, 100]
        ),
        legend_title="Darstellung",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "Der historische Verlauf und die Prognose basieren auf "
        "synthetischen Daten und einer vereinfachten "
        "Simulationslogik des Demonstrators."
    )

    st.divider()

    # --------------------------------------------------
    # Servicebewertung
    # --------------------------------------------------

    st.subheader("🛠️ Servicebewertung")

    st.success(
        "Aktuell besteht kein unmittelbarer Servicebedarf. "
        "Der Bremsbelagzustand sollte weiter beobachtet werden."
    )


# --------------------------------------------------
# SCREEN 3 – SIMULATION
# --------------------------------------------------

elif seite == "📈 Simulation":

    st.title("Simulation der Zustandsentwicklung")

    st.caption(
        "Vereinfachte Simulation der zukünftigen Entwicklung "
        "des Bremsbelagzustands."
    )

    st.info(
        "Die Simulation basiert auf synthetischen Annahmen des Demonstrators "
        "und stellt kein reales physikalisches Verschleißmodell dar."
    )

    # --------------------------------------------------
    # Simulationsparameter
    # --------------------------------------------------

    VERSCHLEISS_PRO_1000_KM = 5

    GRENZE_NORMAL = 30
    GRENZE_BEOBACHTEN = 20
    GRENZE_SERVICE = 10

    aktuelle_km = vehicle["mileage_km"]
    aktueller_zustand = brakes["brake_pad_condition_percent"]

    st.subheader("Simulationsparameter")

    st.write(
        "Wählen Sie die zusätzliche Fahrleistung aus, für die "
        "der zukünftige Bremsbelagzustand simuliert werden soll."
    )
    
    zusaetzliche_km = st.slider(
        "Zusätzliche Fahrleistung einstellen",
        min_value=0,
        max_value=5000,
        value=3000,
        step=500,
        format="%d km"
    )
    
    st.markdown(
        f"**Ausgewählte Fahrleistung: +{format_km(zusaetzliche_km)}**"
    )
    
    simulation_starten = st.button(
        "Simulation starten",
        type="primary"
    )

    # --------------------------------------------------
    # Simulation
    # --------------------------------------------------

    if simulation_starten:

        verschleiss = (
            zusaetzliche_km / 1000
        ) * VERSCHLEISS_PRO_1000_KM

        simulierter_zustand = max(
            0,
            aktueller_zustand - verschleiss
        )

        simulierter_km_stand = (
            aktuelle_km + zusaetzliche_km
        )

        # Status bestimmen
        if simulierter_zustand > GRENZE_NORMAL:
            simulierter_status = "Normal"

        elif simulierter_zustand > GRENZE_BEOBACHTEN:
            simulierter_status = "Beobachten"

        elif simulierter_zustand > GRENZE_SERVICE:
            simulierter_status = "Service empfohlen"

        else:
            simulierter_status = "Kritisch"

        # Simulationsergebnis für andere Ansichten speichern
        st.session_state.simuliert = True
        st.session_state.simulierter_zustand = simulierter_zustand
        st.session_state.simulierter_status = simulierter_status
        st.session_state.simulierter_km_stand = simulierter_km_stand
        st.session_state.zusaetzliche_km = zusaetzliche_km

        st.divider()

        # --------------------------------------------------
        # Vorher-Nachher-Vergleich
        # --------------------------------------------------

        st.subheader("Ergebnis der Simulation")

        col_before, col_after = st.columns(2)

        with col_before:
            st.markdown("### Vor Simulation")

            st.metric(
                "Kilometerstand",
                format_km(aktuelle_km)
            )

            st.metric(
                "Bremsbelagzustand",
                f"{aktueller_zustand:.0f} %"
            )

            st.success(
                f"Status: {brakes['status']}"
            )

        with col_after:
            st.markdown("### Nach Simulation")

            st.metric(
                "Kilometerstand",
                format_km(simulierter_km_stand)
            )

            st.metric(
                "Bremsbelagzustand",
                f"{simulierter_zustand:.0f} %"
            )

            if simulierter_status == "Normal":
                st.success(
                    f"Status: {simulierter_status}"
                )

            elif simulierter_status == "Beobachten":
                st.warning(
                    f"Status: {simulierter_status}"
                )

            elif simulierter_status == "Service empfohlen":
                st.warning(
                    f"Status: {simulierter_status}"
                )

            else:
                st.error(
                    f"Status: {simulierter_status}"
                )

        st.divider()

        # --------------------------------------------------
        # Servicebewertung
        # --------------------------------------------------

        st.subheader("Servicebewertung")

        if simulierter_status == "Normal":

            st.success(
                "Der simulierte Bremsbelagzustand befindet sich "
                "weiterhin im normalen Bereich."
            )

        elif simulierter_status == "Beobachten":

            st.warning(
                "Der Bremsbelagzustand sollte weiter beobachtet werden. "
                "Aktuell besteht noch kein unmittelbarer Servicebedarf."
            )

        elif simulierter_status == "Service empfohlen":

            st.warning(
                "Die simulierte Zustandsentwicklung weist auf einen "
                "bevorstehenden Wartungsbedarf hin."
            )

            st.write(
                "**Empfohlene Maßnahme:** "
                "Bremsbeläge bei einem Werkstatttermin prüfen."
            )

        else:

            st.error(
                "Die simulierte Zustandsentwicklung erreicht einen "
                "kritischen Bereich."
            )

            st.write(
                "**Empfohlene Maßnahme:** "
                "Zeitnahe Prüfung der Bremsbeläge."
            )

        st.caption(
            "Die verwendete Verschleißrate und die Statusgrenzen sind "
            "synthetische Annahmen des Demonstrators."
        )
# --------------------------------------------------
# SCREEN 4 – SERVICEINFORMATION
# --------------------------------------------------

elif seite == "👤 Serviceinformation":

    st.title("Serviceinformation")

    st.caption(
        "Vereinfachte Darstellung des Fahrzeugzustands und "
        "des daraus abgeleiteten Servicebedarfs für die "
        "Kommunikation mit dem Kunden."
    )

    st.info("Demonstrator – ausschließlich synthetische Fahrzeugdaten")

    # --------------------------------------------------
    # Daten auswählen
    # --------------------------------------------------

    if st.session_state.simuliert:
        zustand = st.session_state.simulierter_zustand
        status = st.session_state.simulierter_status
        kilometerstand = st.session_state.simulierter_km_stand

        st.success(
            "Die zuletzt durchgeführte Simulation wird "
            "für diese Serviceinformation verwendet."
        )

    else:
        zustand = brakes["brake_pad_condition_percent"]
        status = brakes["status"]
        kilometerstand = vehicle["mileage_km"]

        st.warning(
            "Es wurde noch keine Simulation durchgeführt. "
            "Dargestellt wird der aktuelle Fahrzeugzustand."
        )

    # --------------------------------------------------
    # Serviceübersicht
    # --------------------------------------------------

    st.subheader("🔧 Bremsbelagzustand")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Kilometerstand",
            format_km(kilometerstand)
        )
    
    with col2:
        st.metric(
            "Bremsbelagzustand",
            f"{zustand:.0f} %"
        )
    
    with col3:
        st.write("**Servicebewertung**")
    
        if status == "Normal":
            st.success("🟢 Normal")
    
        elif status == "Beobachten":
            st.warning("🟡 Beobachten")
    
        elif status == "Service empfohlen":
            st.warning("🟠 Service empfohlen")
    
        else:
            st.error("🔴 Kritisch")
    
    st.divider()

    # --------------------------------------------------
    # Statusskala
    # --------------------------------------------------
    
    st.subheader("Statusübersicht")
    
    status_stufen = [
        ("Normal", "🟢"),
        ("Beobachten", "🟡"),
        ("Service empfohlen", "🟠"),
        ("Kritisch", "🔴")
    ]
    
    spalten = st.columns(4)
    
    for spalte, (status_name, symbol) in zip(spalten, status_stufen):
    
        with spalte:
    
           st.markdown(
                f"""
                <div style="font-size:22px; font-weight:600;">
                    {symbol} {status_name}
                </div>
                """,
                unsafe_allow_html=True
            )
    
            if status == status_name:
                st.caption("▲ Aktueller Status")
    
    st.caption(
        "Die dargestellten Statusstufen basieren auf den "
        "synthetischen Annahmen des Demonstrators."
    )
    
    st.divider()

    # --------------------------------------------------
    # Verständliche Kundeninformation
    # --------------------------------------------------

    st.subheader("Kundeninformation")

    if status == "Normal":

        st.success("Bremsbelagzustand: Normal")

        st.markdown("### Was wurde festgestellt?")
        st.write(
            "Der aktuelle Bremsbelagzustand befindet sich "
            "im normalen Bereich."
        )

        st.markdown("### Besteht Handlungsbedarf?")
        st.write(
            "Aktuell besteht kein unmittelbarer Servicebedarf."
        )

        st.markdown("### Was wird empfohlen?")
        st.write(
            "Der Bremsbelagzustand wird im weiteren Fahrzeugbetrieb "
            "weiter beobachtet."
        )

    elif status == "Beobachten":

        st.warning("Bremsbelagzustand: Beobachten")

        st.markdown("### Was wurde festgestellt?")
        st.write(
            "Der Bremsbelagzustand hat sich gegenüber dem "
            "Ausgangszustand verringert."
        )

        st.markdown("### Besteht Handlungsbedarf?")
        st.write(
            "Aktuell besteht noch kein unmittelbarer Servicebedarf. "
            "Die weitere Entwicklung sollte jedoch beobachtet werden."
        )

        st.markdown("### Was wird empfohlen?")
        st.write(
            "Der Bremsbelagzustand sollte beim nächsten "
            "Service erneut geprüft werden."
        )

    elif status == "Service empfohlen":

        st.warning("Bremsbelagzustand: Service empfohlen")

        st.markdown("### Was wurde festgestellt?")
        st.write(
            "Die simulierte Zustandsentwicklung weist auf einen "
            "bevorstehenden Wartungsbedarf der Bremsbeläge hin."
        )

        st.markdown("### Besteht Handlungsbedarf?")
        st.write(
            "Eine Überprüfung der Bremsbeläge wird empfohlen."
        )

        st.markdown("### Was wird empfohlen?")
        st.write(
            "Die Bremsbeläge sollten bei einem Werkstatttermin "
            "fachgerecht geprüft werden."
        )

    else:

        st.error("Bremsbelagzustand: Kritisch")

        st.markdown("### Was wurde festgestellt?")
        st.write(
            "Die simulierte Zustandsentwicklung hat einen "
            "kritischen Bereich erreicht."
        )

        st.markdown("### Besteht Handlungsbedarf?")
        st.write(
            "Eine zeitnahe technische Prüfung wird empfohlen."
        )

        st.markdown("### Was wird empfohlen?")
        st.write(
            "Die Bremsbeläge sollten zeitnah in einer Werkstatt "
            "fachgerecht überprüft werden."
        )

    st.divider()

    st.caption(
        "Die dargestellte Serviceinformation basiert auf "
        "synthetischen Daten und einer vereinfachten "
        "Simulationslogik des Demonstrators."
    )
