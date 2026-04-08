import plotly.express as px
import streamlit as st

from api_client import get_delays_by_hour, get_stations, get_top_delayed_stations

st.set_page_config(page_title="Station Comparison", page_icon="📊", layout="wide")

st.title("📊 Station Comparison")
st.caption("Compare delay performance across multiple stations.")

stations = get_stations()

# st.multiselect lets the user pick multiple values from a list
selected_stations = st.multiselect(
    "Select stations to compare",
    options=stations,
    default=stations[:3] if len(stations) >= 3 else stations,
)

if not selected_stations:
    st.info("Select at least one station above.")
    st.stop()

# --- Build a combined dataframe from multiple API calls ---
# Each call is cached, so switching selections is fast after the first load.
import pandas as pd

frames = []
for station in selected_stations:
    df = get_delays_by_hour(station)
    df["station_id"] = station
    frames.append(df)

df_all = pd.concat(frames, ignore_index=True)

# --- Side-by-side avg delay comparison ---
st.subheader("Avg Delay by Hour — Multi-Station")
fig = px.line(
    df_all,
    x="hour",
    y="avg_delay",
    color="station_id",
    markers=True,
    labels={"hour": "Hour", "avg_delay": "Avg Delay (min)", "station_id": "Station"},
)
fig.update_layout(xaxis=dict(tickmode="linear", dtick=1), height=400)
st.plotly_chart(fig, use_container_width=True)

# --- Overall ranking table ---
st.markdown("---")
st.subheader("Overall Station Ranking")

df_top = get_top_delayed_stations(limit=50)
df_top = df_top[df_top["station_id"].isin(selected_stations)].reset_index(drop=True)
df_top.index += 1  # rank starts at 1

df_top_display = df_top.rename(columns={
    "station_id": "Station",
    "total_trips": "Total Trips",
    "avg_delay": "Avg Delay (min)",
    "delayed_trips": "Delayed Trips",
    "delay_rate": "Delay Rate",
})
df_top_display["Delay Rate"] = (df_top_display["Delay Rate"] * 100).round(1).astype(str) + "%"

st.dataframe(df_top_display, use_container_width=True)
