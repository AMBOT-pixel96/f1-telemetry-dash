import streamlit as st
import fastf1
from fastf1 import plotting
import pandas as pd
import plotly.express as px
import os

# Fix for Streamlit Cloud: use /tmp for caching
cache_dir = "/tmp/f1cache"
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

st.set_page_config(
    page_title="F1 Telemetry Lab",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 Telemetry Lab")
st.caption("Sidequest: Built by Amlan on stubbornness and caffeine.")

# Sidebar controls
st.sidebar.header("Session Selector")

year = st.sidebar.selectbox("Season", list(reversed(range(2018, 2025))), index=0)
gp_name = st.sidebar.text_input("Grand Prix name (e.g. 'Monza', 'Bahrain', 'Brazil')", "Monza")
session_type = st.sidebar.selectbox("Session", ["R", "Q", "FP1", "FP2", "FP3"])

load_btn = st.sidebar.button("Load Session Data")

if load_btn:
    with st.spinner("Summoning FIA servers..."):
        try:
            session = fastf1.get_session(year, gp_name, session_type)
            session.load()

            st.success(f"Loaded: {year} {gp_name} {session_type}")

            laps = session.laps
            drivers = laps['Driver'].unique()

            col1, col2 = st.columns(2)

            with col1:
                driver1 = st.selectbox("Driver 1", drivers, index=0)
                laps_d1 = laps.pick_driver(driver1)
                lap1 = laps_d1.pick_fastest()
                st.write(f"**Driver 1:** {driver1}, Fastest lap: {lap1['LapTime']}")

            with col2:
                driver2 = st.selectbox("Driver 2", drivers, index=1 if len(drivers) > 1 else 0)
                laps_d2 = laps.pick_driver(driver2)
                lap2 = laps_d2.pick_fastest()
                st.write(f"**Driver 2:** {driver2}, Fastest lap: {lap2['LapTime']}")

            # Get telemetry for both drivers
            tel1 = lap1.get_car_data().add_distance()
            tel2 = lap2.get_car_data().add_distance()

            # Speed comparison chart
            st.subheader("📈 Speed vs Distance")

            fig_speed = px.line(
                pd.DataFrame({
                    "Distance": tel1['Distance'],
                    f"{driver1} Speed": tel1['Speed']
                }),
                x="Distance",
                y=f"{driver1} Speed",
                labels={"Distance": "Distance (m)", f"{driver1} Speed": "Speed (km/h)"},
            )

            fig_speed.add_scatter(
                x=tel2['Distance'],
                y=tel2['Speed'],
                mode='lines',
                name=f"{driver2} Speed"
            )

            st.plotly_chart(fig_speed, use_container_width=True)

            # Throttle / Brake comparison
            st.subheader("🦶 Throttle & Brake (Driver 1 vs Driver 2)")

            col_t1, col_t2 = st.columns(2)

            with col_t1:
                fig_throttle_1 = px.line(
                    tel1,
                    x="Distance",
                    y="Throttle",
                    title=f"{driver1} Throttle %"
                )
                st.plotly_chart(fig_throttle_1, use_container_width=True)

                fig_brake_1 = px.line(
                    tel1,
                    x="Distance",
                    y="Brake",
                    title=f"{driver1} Brake"
                )
                st.plotly_chart(fig_brake_1, use_container_width=True)

            with col_t2:
                fig_throttle_2 = px.line(
                    tel2,
                    x="Distance",
                    y="Throttle",
                    title=f"{driver2} Throttle %"
                )
                st.plotly_chart(fig_throttle_2, use_container_width=True)

                fig_brake_2 = px.line(
                    tel2,
                    x="Distance",
                    y="Brake",
                    title=f"{driver2} Brake"
                )
                st.plotly_chart(fig_brake_2, use_container_width=True)

        except Exception as e:
            st.error(f"Session failed to load. Reason: {e}")
            st.info("Tip: Check GP spelling and that FastF1 supports this season/session.")
else:
    st.info("Select a season, grand prix and session from the sidebar, then hit **Load Session Data**.")