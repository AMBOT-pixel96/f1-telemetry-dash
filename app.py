import streamlit as st
import fastf1
from fastf1 import plotting
import pandas as pd
import plotly.express as px
import os

# --------------------------------------------------------------------------------
# STREAMLIT-CLOUD SAFE CACHE PATH
# --------------------------------------------------------------------------------
cache_dir = "/tmp/f1cache"
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

# --------------------------------------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------------------------------------
st.set_page_config(
    page_title="F1 Telemetry Lab",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 Telemetry Lab")
st.caption("Sidequest: Built by Amlan on stubbornness, caffeine, and race-engineer delusion.")

# --------------------------------------------------------------------------------
# SESSION LOADER WITH CACHE
# --------------------------------------------------------------------------------
@st.cache_data(show_spinner=True)
def load_f1_session(year, gp_name, session_type):
    session = fastf1.get_session(year, gp_name, session_type)
    session.load()                     # loads laps, telemetry, weather, etc.
    return session


# --------------------------------------------------------------------------------
# SIDEBAR UI
# --------------------------------------------------------------------------------
st.sidebar.header("Session Selector")

year = st.sidebar.selectbox("Season", list(reversed(range(2018, 2025))), index=0)
gp_name = st.sidebar.text_input("Grand Prix (e.g. Monza, Bahrain, Brazil)", "Monza")
session_type = st.sidebar.selectbox("Session", ["R", "Q", "FP1", "FP2", "FP3"])

load_btn = st.sidebar.button("Load Session Data")


# --------------------------------------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------------------------------------
if load_btn:
    try:
        session = load_f1_session(year, gp_name, session_type)
        laps = session.laps
        drivers = laps['Driver'].unique()

        st.success(f"Loaded session: {year} {gp_name} {session_type}")

        # -------------------- DRIVER SELECTION --------------------
        col1, col2 = st.columns(2)

        with col1:
            driver1 = st.selectbox("Driver 1", drivers, index=0, key="driver1")
            lap1 = laps.pick_driver(driver1).pick_fastest()
            st.write(f"**Driver 1 Fastest Lap:** {lap1['LapTime']}")

        with col2:
            driver2 = st.selectbox("Driver 2", drivers, index=1 if len(drivers) > 1 else 0, key="driver2")
            lap2 = laps.pick_driver(driver2).pick_fastest()
            st.write(f"**Driver 2 Fastest Lap:** {lap2['LapTime']}")

        if lap1 is None or lap2 is None:
            st.error("One of the drivers has no fastest lap data.")
            st.stop()

        # -------------------- TELEMETRY --------------------
        tel1 = lap1.get_car_data().add_distance()
        tel2 = lap2.get_car_data().add_distance()

        # --------------------------------------------------------------------------------
        # SPEED COMPARISON
        # --------------------------------------------------------------------------------
        st.subheader("📈 Speed vs Distance")

        fig_speed = px.line(
            pd.DataFrame({
                "Distance": tel1['Distance'],
                f"{driver1} Speed": tel1['Speed']
            }),
            x="Distance",
            y=f"{driver1} Speed",
            labels={"Distance": "Distance (m)", f"{driver1} Speed": "Speed (km/h)"}
        )

        fig_speed.add_scatter(
            x=tel2['Distance'],
            y=tel2['Speed'],
            mode='lines',
            name=f"{driver2} Speed"
        )

        st.plotly_chart(fig_speed, use_container_width=True)


        # --------------------------------------------------------------------------------
        # THROTTLE & BRAKE (SIDE BY SIDE)
        # --------------------------------------------------------------------------------
        st.subheader("🦶 Throttle & Brake — Driver 1 vs Driver 2")

        col_t1, col_t2 = st.columns(2)

        # ---------------- DRIVER 1 ----------------
        with col_t1:
            st.markdown(f"### {driver1} Throttle %")
            fig_throttle_1 = px.line(
                tel1, x="Distance", y="Throttle"
            )
            st.plotly_chart(fig_throttle_1, use_container_width=True)

            st.markdown(f"### {driver1} Brake")
            fig_brake_1 = px.line(
                tel1, x="Distance", y="Brake"
            )
            st.plotly_chart(fig_brake_1, use_container_width=True)

        # ---------------- DRIVER 2 ----------------
        with col_t2:
            st.markdown(f"### {driver2} Throttle %")
            fig_throttle_2 = px.line(
                tel2, x="Distance", y="Throttle"
            )
            st.plotly_chart(fig_throttle_2, use_container_width=True)

            st.markdown(f"### {driver2} Brake")
            fig_brake_2 = px.line(
                tel2, x="Distance", y="Brake"
            )
            st.plotly_chart(fig_brake_2, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading session: {e}")
        st.info("Check GP spelling or FastF1 availability.")

else:
    st.info("Select a season, a race, and a session — then press **Load Session Data**.")