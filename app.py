import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(
    page_title="F1 Telemetry Lab — OpenF1 Edition",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 Telemetry Lab — OpenF1 Edition")
st.caption("Powered by OpenF1 • Built by Amlan • Engineered for chaos & precision ⚡")

# -----------------------------
# API ENDPOINTS
# -----------------------------
OPENF1_SESSIONS = "https://api.openf1.org/v1/sessions"
OPENF1_CAR_DATA = "https://api.openf1.org/v1/car_data"
OPENF1_LAPS = "https://api.openf1.org/v1/laps"
OPENF1_DRIVERS = "https://api.openf1.org/v1/drivers"

# -----------------------------
# FETCH SESSION LIST
# -----------------------------
@st.cache_data(show_spinner=True)
def get_sessions(year):
    response = requests.get(OPENF1_SESSIONS, params={"year": year})
    df = pd.DataFrame(response.json())
    return df

# -----------------------------
# FETCH DRIVER LIST FOR A SESSION
# -----------------------------
@st.cache_data(show_spinner=True)
def get_drivers(session_key):
    response = requests.get(OPENF1_DRIVERS, params={"session_key": session_key})
    df = pd.DataFrame(response.json())
    return df

# -----------------------------
# FETCH TELEMETRY FOR A DRIVER
# -----------------------------
@st.cache_data(show_spinner=True)
def get_telemetry(session_key, driver_number):
    params = {
        "session_key": session_key,
        "driver_number": driver_number
    }
    response = requests.get(OPENF1_CAR_DATA, params=params)
    df = pd.DataFrame(response.json())
    return df

# -----------------------------
# SIDEBAR — SELECT SESSION
# -----------------------------
st.sidebar.header("Session Selector")

year = st.sidebar.selectbox("Season", list(reversed(range(2018, 2026))), index=0)

sessions_df = get_sessions(year)

if sessions_df.empty:
    st.warning("No sessions available for this year yet.")
    st.stop()

# Sort by date newest → oldest
sessions_df = sessions_df.sort_values("date_start", ascending=False)

session_label_map = {
    row['session_key']: f"{row['circuit_short_name']} — {row['session_name']} ({row['date_start'][:10]})"
    for _, row in sessions_df.iterrows()
}

session_key = st.sidebar.selectbox(
    "Select a Session",
    options=session_label_map.keys(),
    format_func=lambda x: session_label_map[x]
)

# -----------------------------
# DRIVER SELECTORS
# -----------------------------
drivers_df = get_drivers(session_key)

driver_numbers = drivers_df["driver_number"].unique()

col1, col2 = st.sidebar.columns(2)
driver1 = col1.selectbox("Driver 1", driver_numbers)
driver2 = col2.selectbox("Driver 2", driver_numbers)

# -----------------------------
# LOAD TELEMETRY
# -----------------------------
st.subheader(f"📊 Telemetry Comparison — Session {session_key}")

tel1 = get_telemetry(session_key, driver1)
tel2 = get_telemetry(session_key, driver2)

if tel1.empty or tel2.empty:
    st.error("Telemetry missing for one or both drivers.")
    st.stop()

# -----------------------------
# SPEED vs TIME
# -----------------------------
st.markdown("## 🏎️ Speed vs Time")

fig_speed = px.line(
    tel1,
    x="date",
    y="speed",
    title=f"Speed — Driver {driver1}",
    labels={"speed": "Speed (km/h)"}
)

fig_speed.add_scatter(
    x=tel2["date"],
    y=tel2["speed"],
    mode="lines",
    name=f"Driver {driver2}"
)

st.plotly_chart(fig_speed, use_container_width=True)

# -----------------------------
# THROTTLE & BRAKE
# -----------------------------
st.markdown("## 🦶 Throttle & Brake")

colA, colB = st.columns(2)

with colA:
    st.markdown(f"### Driver {driver1}")
    fig_t1 = px.line(tel1, x="date", y="throttle", title=f"{driver1} — Throttle")
    st.plotly_chart(fig_t1, use_container_width=True)

    fig_b1 = px.line(tel1, x="date", y="brake", title=f"{driver1} — Brake")
    st.plotly_chart(fig_b1, use_container_width=True)

with colB:
    st.markdown(f"### Driver {driver2}")
    fig_t2 = px.line(tel2, x="date", y="throttle", title=f"{driver2} — Throttle")
    st.plotly_chart(fig_t2, use_container_width=True)

    fig_b2 = px.line(tel2, x="date", y="brake", title=f"{driver2} — Brake")
    st.plotly_chart(fig_b2, use_container_width=True)

# -----------------------------
# RPM & GEAR
# -----------------------------
st.markdown("## ⚙️ RPM & Gear")

colC, colD = st.columns(2)

with colC:
    fig_rpm = px.line(tel1, x="date", y="rpm", title=f"RPM — Driver {driver1}")
    fig_rpm.add_scatter(x=tel2["date"], y=tel2["rpm"], mode="lines", name=f"{driver2}")
    st.plotly_chart(fig_rpm, use_container_width=True)

with colD:
    fig_gear = px.line(tel1, x="date", y="gear", title=f"Gear — Driver {driver1}")
    fig_gear.add_scatter(x=tel2["date"], y=tel2["gear"], mode="lines", name=f"{driver2}")
    st.plotly_chart(fig_gear, use_container_width=True)

# -----------------------------
# SUCCESS MESSAGE
# -----------------------------
st.success("Telemetry loaded successfully via OpenF1 ⚡")