import json
import time
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
# Zentrale Modellparameter des Demonstrators
# --------------------------------------------------

VERSCHLEISS_PRO_1000_KM = 5

GRENZE_NORMAL = 30
GRENZE_BEOBACHTEN = 20
GRENZE_SERVICE = 10

# --------------------------------------------------
# Digital-Twin-Zustand initialisieren
# --------------------------------------------------

if "twin_state" not in st.session_state:
    st.session_state.twin_state = {
        "mileage_km": float(vehicle["mileage_km"]),
        "speed_kmh": 0,
        "brake_condition_percent": float(
            brakes["brake_pad_condition_percent"]
        ),
        "status": brakes["status"],
        "operating_state": "Stillstand",
        "sync_status": "Synchronisiert",
        "last_update": time.time()
    }

if "fahrt_aktiv" not in st.session_state:
    st.session_state.fahrt_aktiv = False

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

def update_twin_state():
    """Aktualisiert den Digital-Twin-Zustand während der Demonstrationsfahrt."""

    if not st.session_state.fahrt_aktiv:
        return

    twin = st.session_state.twin_state

    # Beschleunigte synthetische Demonstrationsfahrt
    twin["speed_kmh"] = 72
    twin["operating_state"] = "Fahrt"

    # Pro Aktualisierung werden 100 km simuliert.
    simulated_distance = 100

    twin["mileage_km"] += simulated_distance

    # Synthetische Verschleißlogik:
    # 5 Prozentpunkte je 1.000 km
    brake_wear = (simulated_distance / 1000) * 5

    twin["brake_condition_percent"] = max(
        0,
        twin["brake_condition_percent"] - brake_wear
    )

    twin["last_update"] = time.time()

    twin["status"] = bestimme_status(
        twin["brake_condition_percent"]
    )
    
def bestimme_status(zustand):
    if zustand > GRENZE_NORMAL:
        return "Normal"

    elif zustand > GRENZE_BEOBACHTEN:
        return "Beobachten"

    elif zustand > GRENZE_SERVICE:
        return "Service empfohlen"

    else:
        return "Kritisch"
        
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

st.sidebar.write("**Aktueller Twin-Status**")

twin_status = st.session_state.twin_state["status"]

if twin_status == "Normal":
    st.sidebar.success(f"● {twin_status}")

elif twin_status == "Beobachten":
    st.sidebar.warning(f"● {twin_status}")

elif twin_status == "Service empfohlen":
    st.sidebar.warning(f"● {twin_status}")

else:
    st.sidebar.error(f"● {twin_status}")

st.sidebar.caption("Synthetische Fahrzeugdaten")


# --------------------------------------------------
# SCREEN 1 – FAHRZEUGÜBERSICHT
# --------------------------------------------------

if seite == "🚗 Fahrzeugübersicht":

    # Laufenden Digital Twin aktualisieren
    if st.session_state.fahrt_aktiv:
        update_twin_state()

    twin = st.session_state.twin_state
    
    st.title("Digital Twin – Automotive After-Sales")

    st.caption(
        "Prototypischer Demonstrator zur Unterstützung eines "
        "datenbasierten After-Sales-Serviceprozesses"
    )

    st.info("Demonstrator – ausschließlich synthetische Fahrzeugdaten")

    st.subheader("🔄 Digital-Twin-Synchronisation")

    col_live, col_operation, col_controls = st.columns([2, 2, 2])

    with col_live:
        if st.session_state.fahrt_aktiv:
            st.success("● LIVE – Digital Twin synchronisiert")
        else:
            st.info("● BEREIT – Fahrzeug im Stillstand")

    with col_operation:
        st.metric(
            "Betriebszustand",
            twin["operating_state"]
        )

    with col_controls:
        if not st.session_state.fahrt_aktiv:
            if st.button("▶ Fahrt starten", type="primary"):
                st.session_state.fahrt_aktiv = True
                st.rerun()
        else:
            if st.button("■ Fahrt stoppen"):
                st.session_state.fahrt_aktiv = False
                twin["speed_kmh"] = 0
                twin["operating_state"] = "Stillstand"
                st.rerun()

    st.caption(
        "Simulierter Live-Datenstrom – Die kontinuierliche "
        "Datenübertragung eines realen Fahrzeugs wird im Demonstrator "
        "durch synthetisch erzeugte Fahrzeugdaten simuliert."
    )

    # Fahrzeug und Gesamtstatus
    col_vehicle, col_status = st.columns([3, 1])

    with col_vehicle:
        st.subheader(f"Fahrzeug {vehicle['vehicle_id']}")

    with col_status:
        st.write("**Aktueller Status**")
    
        if twin["status"] == "Normal":
            st.success("● Normal")
    
        elif twin["status"] == "Beobachten":
            st.warning("● Beobachten")
    
        elif twin["status"] == "Service empfohlen":
            st.warning("● Service empfohlen")
    
        else:
            st.error("● Kritisch")

    # Kennzahlen
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Kilometerstand",
            format_km(twin["mileage_km"])
        )

    with col2:
        st.metric(
            "Geschwindigkeit",
            f"{twin['speed_kmh']} km/h"
        )

    with col3:
        st.metric(
            "Bremsbelagzustand",
            f"{twin['brake_condition_percent']:.1f} %"
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
            f"{format_km(twin['mileage_km'])}"
        )

    with col_condition:
        st.subheader("🔧 Aktueller Bremszustand")

        st.metric(
            "Bremsbelagzustand",
            f"{twin['brake_condition_percent']:.1f} %"
        )
        
        st.write(f"**Status:** {twin['status']}")
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
            "Bremszustand unauffällig"
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

    # Automatische Aktualisierung während der Fahrt
    if st.session_state.fahrt_aktiv:
        time.sleep(1)
        st.rerun()


# --------------------------------------------------
# SCREEN 2 – BREMSZUSTAND & PROGNOSE
# --------------------------------------------------

elif seite == "🔧 Bremszustand & Prognose":

    twin = st.session_state.twin_state

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
            f"{twin['brake_condition_percent']:.1f} %"
        )
        
        st.write(f"**Status:** {twin['status']}")
        st.write(
            f"**Messzeitpunkt:** "
            f"{format_date(brakes['measurement_date'])}"
        )

    with col_prediction:
        st.subheader("📈 Prognose")
    
        aktueller_zustand = twin["brake_condition_percent"]
    
        if aktueller_zustand > GRENZE_SERVICE:
            benoetigter_verschleiss = (
                aktueller_zustand - GRENZE_SERVICE
            )
    
            wartungsbedarf_km = (
                benoetigter_verschleiss
                / VERSCHLEISS_PRO_1000_KM
            ) * 1000
    
            wartungsbedarf_km = round(
                wartungsbedarf_km / 100
            ) * 100
    
            st.metric(
                "Erwarteter Wartungsbedarf",
                f"in ca. {format_km(wartungsbedarf_km)}"
            )
    
            st.write(
                "**Prognosestatus:** Servicebedarf absehbar"
            )
            
            st.write(
                f"**Hinweis:** Bei gleichbleibender synthetischer "
                f"Zustandsentwicklung wird in ca. "
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
        twin["mileage_km"],
        twin["mileage_km"] + 1000,
        twin["mileage_km"] + 2000,
        twin["mileage_km"] + 3000,
        twin["mileage_km"] + 4000,
        twin["mileage_km"] + 5000
    ]
    prognose_zustaende = [
        max(
            0,
            twin["brake_condition_percent"]
            - ((km - twin["mileage_km"]) / 1000)
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
            x=[twin["mileage_km"]],
            y=[twin["brake_condition_percent"]],
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
        "Bei gleichbleibender Zustandsentwicklung ist jedoch in 4.000 km mit einem Servicebedarf zu rechnen."
    )


# --------------------------------------------------
# SCREEN 3 – SIMULATION
# --------------------------------------------------

elif seite == "📈 Simulation":

    twin = st.session_state.twin_state
    
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

    aktuelle_km = twin["mileage_km"]
    aktueller_zustand = twin["brake_condition_percent"]

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
        simulierter_status = bestimme_status(simulierter_zustand)

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

            if twin["status"] == "Normal":
                st.success(f"Status: {twin['status']}")
            elif twin["status"] == "Beobachten":
                st.warning(f"Status: {twin['status']}")
            elif twin["status"] == "Service empfohlen":
                st.warning(f"Status: {twin['status']}")
            else:
                st.error(f"Status: {twin['status']}")

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
                "Bei weiterer Zustandsverschlechterung kann ein Servicebedarf entstehen."
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

    twin = st.session_state.twin_state
    
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
        zustand = twin["brake_condition_percent"]
        status = twin["status"]
        kilometerstand = twin["mileage_km"]

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
