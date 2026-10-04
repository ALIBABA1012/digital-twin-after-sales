import json
import time
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import base64
import streamlit.components.v1 as components

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
        "last_update": time.time()
    }

if "fahrt_aktiv" not in st.session_state:
    st.session_state.fahrt_aktiv = False

if "twin_history" not in st.session_state:
    st.session_state.twin_history = [
        {
            "mileage_km": st.session_state.twin_state["mileage_km"],
            "brake_condition_percent":
                st.session_state.twin_state["brake_condition_percent"],
            "speed_kmh": st.session_state.twin_state["speed_kmh"]
        }
    ]

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

    # Synthetische Verschleißberechnung auf Basis
    # der zentral definierten Verschleißrate
    brake_wear = (
        simulated_distance / 1000
    ) * VERSCHLEISS_PRO_1000_KM
    
    twin["brake_condition_percent"] = max(
        0,
        twin["brake_condition_percent"] - brake_wear
    )

    twin["last_update"] = time.time()

    twin["status"] = bestimme_status(
        twin["brake_condition_percent"]
    )

    st.session_state.twin_history.append(
        {
            "mileage_km": twin["mileage_km"],
            "brake_condition_percent":
                twin["brake_condition_percent"],
            "speed_kmh": twin["speed_kmh"]
        }
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

def show_vehicle_3d():
    """Zeigt das 3D-Fahrzeug mit interaktivem Bremsbereich."""

    twin = st.session_state.twin_state

    brake_condition = twin["brake_condition_percent"]
    brake_status = twin["status"]
    mileage = twin["mileage_km"]
    mileage_formatted = f"{mileage:,.0f}".replace(",", ".")

    with open("assets/CarConcept.glb", "rb") as model_file:
        model_data = base64.b64encode(
            model_file.read()
        ).decode("utf-8")

    # Statusabhängige Farbe der Bremsanzeige
    if brake_status == "Normal":
        status_color = "#2e7d32"
    elif brake_status == "Beobachten":
        status_color = "#ed6c02"
    elif brake_status == "Service empfohlen":
        status_color = "#f57c00"
    else:
        status_color = "#b71c1c"

    html = f"""
    <script type="module"
        src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js">
    </script>

    <style>
        body {{
            margin: 0;
            background: transparent;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }}

        .vehicle-container {{
            position: relative;
            width: 100%;
            height: 520px;
        }}

        model-viewer {{
            width: 100%;
            height: 520px;
            background-color: transparent;
        }}

        /* Hotspot am Vorderrad */
        .brake-hotspot {{
            width: 38px;
            height: 38px;

            border-radius: 50%;
            border: 2px solid white;

            background: {status_color};
            color: white;

            font-size: 18px;
            cursor: pointer;

            display: flex;
            align-items: center;
            justify-content: center;

            box-shadow: 0 0 10px rgba(0, 0, 0, 0.7);

            transition:
                transform 0.2s ease,
                box-shadow 0.2s ease;
        }}

        .brake-hotspot:hover {{
            transform: scale(1.15);
            box-shadow: 0 0 14px rgba(255, 255, 255, 0.4);
        }}

        /* Bremsdetail */
        .brake-panel {{
            position: absolute;

            top: 20px;
            right: 20px;

            width: 260px;

            padding: 18px;

            background: rgba(20, 22, 27, 0.96);

            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 12px;

            color: white;

            display: none;

            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);

            z-index: 10;
        }}

        .brake-panel.visible {{
            display: block;
        }}

        .panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;

            margin-bottom: 14px;
        }}

        .panel-title {{
            font-size: 16px;
            font-weight: bold;
        }}

        .close-button {{
            border: none;
            background: transparent;
            color: #bbbbbb;

            font-size: 22px;
            cursor: pointer;
        }}

        /* Vereinfachte Bremsscheibe */
        .brake-visual {{
            width: 105px;
            height: 105px;

            margin: 8px auto 18px auto;

            border-radius: 50%;

            border: 12px solid #777;

            background: #303030;

            position: relative;

            box-shadow:
                inset 0 0 0 5px #aaaaaa,
                0 0 14px rgba(0, 0, 0, 0.5);
        }}

        .brake-visual::after {{
            content: "";

            position: absolute;

            width: 28px;
            height: 58px;

            right: -16px;
            top: 23px;

            background: {status_color};

            border-radius: 6px;
        }}

        .detail-row {{
            display: flex;
            justify-content: space-between;

            gap: 10px;

            padding: 7px 0;

            border-bottom:
                1px solid rgba(255, 255, 255, 0.08);

            font-size: 14px;
        }}

        .detail-value {{
            font-weight: bold;
            text-align: right;
        }}

        .status-value {{
            color: {status_color};
        }}

        .sync-info {{
            margin-top: 14px;

            padding-top: 10px;

            font-size: 12px;
            color: #b7b7b7;
        }}

        .sync-dot {{
            display: inline-block;

            width: 8px;
            height: 8px;

            margin-right: 6px;

            border-radius: 50%;

            background: #43a047;
        }}
    </style>


    <div class="vehicle-container">

        <model-viewer
            src="data:model/gltf-binary;base64,{model_data}"

            camera-controls
            disable-zoom
            interaction-prompt="none"

            shadow-intensity="1"
            exposure="1"

            camera-orbit="45deg 75deg auto"

            min-camera-orbit="-180deg 60deg auto"
            max-camera-orbit="180deg 90deg auto">

            <button
                id="brakeHotspot"

                class="brake-hotspot"

                slot="hotspot-brake-front"

                data-position="0.85m 0.35m 1.55m"
                data-normal="0m 0m 1m"

                aria-label="Bremszustand anzeigen">

                🔧

            </button>

        </model-viewer>


        <div
            id="brakePanel"
            class="brake-panel">

            <div class="panel-header">

                <div class="panel-title">
                    🔧 Bremssystem – vorne
                </div>

                <button
                    id="closeBrakePanel"
                    class="close-button"
                    aria-label="Detailansicht schließen">

                    ×

                </button>

            </div>


            <div class="brake-visual"></div>


            <div class="detail-row">

                <span>
                    Bremsbelagzustand
                </span>

                <span class="detail-value">
                    {brake_condition:.1f} %
                </span>

            </div>


            <div class="detail-row">

                <span>
                    Status
                </span>

                <span class="detail-value status-value">
                    {brake_status}
                </span>

            </div>


            <div class="detail-row">

                <span>
                    Kilometerstand
                </span>

                <span class="detail-value">
                    {mileage_formatted} km
                </span>

            </div>


            <div class="sync-info">

                <span class="sync-dot"></span>

                Mit Digital Twin DT-001 synchronisiert

            </div>

        </div>

    </div>


    <script>

        const hotspot =
            document.getElementById("brakeHotspot");

        const panel =
            document.getElementById("brakePanel");

        const closeButton =
            document.getElementById("closeBrakePanel");


        hotspot.addEventListener(
            "click",
            function(event) {{

                event.stopPropagation();

                panel.classList.add("visible");

            }}
        );


        closeButton.addEventListener(
            "click",
            function() {{

                panel.classList.remove("visible");

            }}
        );

    </script>
    """

    components.html(
        html,
        height=520,
        scrolling=False
    )
        
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

    st.divider()

    st.subheader("🚗 Virtuelle Fahrzeugrepräsentation")

    col_3d, col_twin_info = st.columns([2, 1])

    with col_3d:
        show_vehicle_3d()
    
        st.caption(
            "Interaktive 3D-Repräsentation der virtuellen "
            "Fahrzeuginstanz DT-001. Das Fahrzeug kann horizontal "
            "um 360° sowie vertikal in einem begrenzten Bereich "
            "betrachtet werden."
        )
        
    with col_twin_info:
        st.markdown("### Digital Twin DT-001")

        st.write(
            f"**Betriebszustand:** {twin['operating_state']}"
        )

        st.write(
            f"**Geschwindigkeit:** {twin['speed_kmh']} km/h"
        )

        st.write(
            f"**Kilometerstand:** {format_km(twin['mileage_km'])}"
        )

        st.write(
            f"**Bremsbelagzustand:** "
            f"{twin['brake_condition_percent']:.1f} %"
        )

        st.write(
            f"**Zustandsbewertung:** {twin['status']}"
        )

        st.divider()

        st.markdown("#### Überwachte Komponente")

        st.write("🔧 **Bremssystem / Bremsbeläge**")

        st.write(
            "Der markierte Radbereich repräsentiert die "
            "im Anwendungsszenario betrachtete Komponente."
        )

    st.divider()

    st.subheader("📡 Live-Fahrzeugdaten")

    history_df = pd.DataFrame(
        st.session_state.twin_history
    )

    fig_live = go.Figure()

    fig_live.add_trace(
        go.Scatter(
            x=history_df["mileage_km"],
            y=history_df["brake_condition_percent"],
            mode="lines+markers",
            name="Bremsbelagzustand",
            customdata=[
                f"{wert:,.0f}".replace(",", ".")
                for wert in history_df["mileage_km"]
            ],
            hovertemplate=(
                "Kilometerstand: %{customdata} km<br>"
                "Bremsbelagzustand: %{y:.1f} %"
                "<extra></extra>"
            )
        )
    )

    x_min_live = int(history_df["mileage_km"].min())
    x_max_live = int(history_df["mileage_km"].max())
    
    tick_start_live = (x_min_live // 500) * 500
    tick_end_live = ((x_max_live // 500) + 1) * 500
    
    tickvals_live = list(
        range(tick_start_live, tick_end_live + 1, 500)
    )
    
    ticktext_live = [
        f"{wert:,}".replace(",", ".")
        for wert in tickvals_live
    ]
    
    fig_live.update_layout(
        xaxis=dict(
            title="Kilometerstand [km]",
            tickmode="array",
            tickvals=tickvals_live,
            ticktext=ticktext_live
        ),
        yaxis=dict(
            title="Bremsbelagzustand [%]",
            range=[0, 100]
        ),
        height=330,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        showlegend=False
    )

    st.plotly_chart(
        fig_live,
        use_container_width=True,
        config={
            "locale": "de"
        }
    )

    st.caption(
        "Der Verlauf zeigt die während der simulierten "
        "Fahrzeugnutzung kontinuierlich aktualisierten "
        "Zustandsdaten der virtuellen Fahrzeuginstanz DT-001."
    )

    st.divider()

    st.subheader("🔄 Datenfluss des Digital-Twin-Demonstrators")

    col_flow1, col_arrow1, col_flow2, col_arrow2, col_flow3, col_arrow3, col_flow4 = st.columns(
        [2, 0.4, 2, 0.4, 2, 0.4, 2]
    )

    with col_flow1:
        st.markdown(
            """
            #### 🚗 Fahrzeug
            Simulierte Fahrzeugnutzung
            """
        )

    with col_arrow1:
        st.markdown("### →")

    with col_flow2:
        st.markdown(
            """
            #### 📡 Fahrzeugdaten
            Synthetische Zustandsdaten
            """
        )

    with col_arrow2:
        st.markdown("### →")

    with col_flow3:
        st.markdown(
            """
            #### 🔄 Synchronisation
            Kontinuierliche Zustandsaktualisierung
            """
        )

    with col_arrow3:
        st.markdown("### →")

    with col_flow4:
        st.markdown(
            """
            #### 🚘 Digital Twin
            Virtuelle Instanz DT-001
            """
        )

    col_analysis1, col_analysis2, col_analysis3 = st.columns(3)

    with col_analysis1:
        st.info(
            "🔧 **Bremszustand & Prognose**\n\n"
            "Bewertung und zukünftige Zustandsentwicklung"
        )

    with col_analysis2:
        st.info(
            "📈 **Simulation**\n\n"
            "What-if-Analyse zusätzlicher Fahrzeugnutzung"
        )

    with col_analysis3:
        st.info(
            "👤 **Serviceinformation**\n\n"
            "Ableitung verständlicher Serviceinformationen"
        )

    st.caption(
        "Die kontinuierliche Datenübertragung eines realen "
        "Fahrzeugs wird im Demonstrator durch synthetisch "
        "erzeugte Fahrzeugdaten simuliert."
    )

    st.divider()

    # Fahrzeugstammdaten
    st.subheader("🚗 Fahrzeuginformationen")

    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.write(
            f"**Fahrzeug-ID:** {vehicle['vehicle_id']}"
        )

        st.write(
            f"**Modell:** {vehicle['model']}"
        )

    with col_info2:
        st.write(
            f"**Baujahr:** {vehicle['year']}"
        )

        st.write("**Antrieb:** Elektro")

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
        letzte_sync = time.strftime(
            "%d.%m.%Y – %H:%M:%S",
            time.localtime(twin["last_update"])
        )
        
        st.write(
            f"**Letzte Synchronisation:** {letzte_sync}"
        )

    with col_prediction:
        st.subheader("📈 Prognose")
    
        aktueller_zustand = twin["brake_condition_percent"]
    
        if aktueller_zustand > GRENZE_BEOBACHTEN:
            benoetigter_verschleiss = (
                aktueller_zustand - GRENZE_BEOBACHTEN
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
                f"{format_km(wartungsbedarf_km)} "
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
            customdata=[
                f"{wert:,.0f}".replace(",", ".")
                for wert in historische_km
            ],
            hovertemplate=(
                "Kilometerstand: %{customdata} km<br>"
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
            customdata=[
                f"{wert:,.0f}".replace(",", ".")
                for wert in prognose_km
            ],
            line=dict(
                dash="dash"
            ),
            hovertemplate=(
                "Kilometerstand: %{customdata} km<br>"
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
            customdata=[
                format_km(twin["mileage_km"]).replace(" km", "")
            ],
            marker=dict(
                size=15,
                color="green",
                line=dict(
                    width=2,
                    color="white"
                )
            ),
            hovertemplate=(
                "Kilometerstand: %{customdata} km<br>"
                "Bremsbelagzustand: %{y:.0f} %"
                "<extra></extra>"
            )
        )
    )

    tickvals_prognose = list(
        range(30000, 50001, 5000)
    )
    
    ticktext_prognose = [
        f"{wert:,}".replace(",", ".")
        for wert in tickvals_prognose
    ]
    
    fig.update_layout(
        xaxis=dict(
            title="Kilometerstand [km]",
            tickmode="array",
            tickvals=tickvals_prognose,
            ticktext=ticktext_prognose
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
        use_container_width=True,
        config={
            "locale": "de"
        }
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

    if twin["status"] == "Normal":
        st.success(
            "Aktuell besteht kein unmittelbarer Servicebedarf. "
            f"Bei gleichbleibender Zustandsentwicklung wird der "
            f"Bereich „Service empfohlen“ voraussichtlich in "
            f"{format_km(wartungsbedarf_km)} erreicht."
        )

    elif twin["status"] == "Beobachten":
        st.warning(
            "Der Bremsbelagzustand sollte weiter beobachtet werden. "
            f"Bei gleichbleibender Zustandsentwicklung wird der "
            f"Bereich „Service empfohlen“ voraussichtlich in "
            f"{format_km(wartungsbedarf_km)} erreicht."
        )

    elif twin["status"] == "Service empfohlen":
        st.warning(
            "Der definierte Bereich für eine Serviceempfehlung "
            "ist erreicht. Eine Überprüfung des Bremssystems "
            "wird empfohlen."
        )

    else:
        st.error(
            "Der Bremsbelagzustand befindet sich im definierten "
            "kritischen Bereich. Eine zeitnahe Überprüfung des "
            "Bremssystems wird empfohlen."
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
            "Der zugrunde liegende Bremsbelagzustand befindet sich "
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
            "Der Bremsbelagzustand befindet sich im "
            "definierten Beobachtungsbereich."
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
            "Der zugrunde liegende Bremsbelagzustand befindet sich "
            "im definierten Bereich für eine Serviceempfehlung."
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
            "Der zugrunde liegende Bremsbelagzustand befindet sich "
            "im definierten kritischen Bereich."
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
