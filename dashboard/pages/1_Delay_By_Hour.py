import plotly.express as px
import streamlit as st

from api_client import get_delays_by_hour, get_stations

st.set_page_config(page_title="Delay By Hour", page_icon="⏱️", layout="wide")

st.title("⏱️ Delay Patterns by Hour")
st.caption("Understand at which hours of the day trains are most delayed.")

stations = get_stations()
selected_station = st.sidebar.selectbox("Select Station", options=stations, index=0)

df = get_delays_by_hour(selected_station)

if df.empty:
    st.warning(f"No data for station {selected_station}.")
    st.stop()

# --- Two charts side by side ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Avg Delay per Hour")
    fig1 = px.line(
        df,
        x="hour",
        y="avg_delay",
        markers=True,
        labels={"hour": "Hour", "avg_delay": "Avg Delay (min)"},
    )
    fig1.update_traces(line_color="#e63946")
    fig1.update_layout(xaxis=dict(tickmode="linear", dtick=1), height=350)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Delay Rate per Hour (%)")
    # delay_rate from API is 0.0–1.0, convert to percentage for display
    df["delay_rate_pct"] = df["delay_rate"] * 100
    fig2 = px.bar(
        df,
        x="hour",
        y="delay_rate_pct",
        labels={"hour": "Hour", "delay_rate_pct": "Delay Rate (%)"},
        color="delay_rate_pct",
        color_continuous_scale="Blues",
    )
    fig2.update_layout(
        xaxis=dict(tickmode="linear", dtick=1),
        coloraxis_showscale=False,
        height=350,
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Raw data table ---
# st.expander collapses a section — good for showing raw data without cluttering the page
with st.expander("Show raw data"):
    st.dataframe(
        df[["hour", "total_trips", "avg_delay", "delayed_trips", "delay_rate"]],
        use_container_width=True,
    )
