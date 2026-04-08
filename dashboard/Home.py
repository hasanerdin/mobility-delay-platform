import plotly.express as px
import streamlit as st

from api_client import get_delays_by_hour, get_stations, get_top_delayed_stations

st.set_page_config(
    page_title="Mobility Delay Platform",
    page_icon="🚆",
    layout="wide",
)

st.title("🚆 Deutsche Bahn Delay Analytics")
st.caption("Real-time and historical delay analysis for German railway stations.")

# --- Sidebar: station selector ---
# st.sidebar puts widgets in the left panel, shared across the page.
stations = get_stations()
selected_station = st.sidebar.selectbox(
    "Select Station",
    options=stations,
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown("Data source: Deutsche Bahn API + historical dataset")

# --- Load data for selected station ---
df_hour = get_delays_by_hour(selected_station)

# --- KPI metrics row ---
# st.columns splits the page into N equal-width columns.
if not df_hour.empty:
    total_trips = int(df_hour["total_trips"].sum())
    avg_delay = round(float(df_hour["avg_delay"].mean()), 1)
    total_delayed = int(df_hour["delayed_trips"].sum())
    overall_delay_rate = round(total_delayed / total_trips * 100, 1) if total_trips > 0 else 0
    peak_hour = int(df_hour.loc[df_hour["avg_delay"].idxmax(), "hour"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trips Recorded", f"{total_trips:,}")
    col2.metric("Avg Delay (minutes)", avg_delay)
    col3.metric("Delay Rate", f"{overall_delay_rate}%")
    col4.metric("Peak Delay Hour", f"{peak_hour:02d}:00")

    st.markdown("---")

    # --- Avg delay by hour bar chart ---
    st.subheader(f"Average Delay by Hour — Station {selected_station}")

    fig = px.bar(
        df_hour,
        x="hour",
        y="avg_delay",
        labels={"hour": "Hour of Day", "avg_delay": "Avg Delay (min)"},
        color="avg_delay",
        color_continuous_scale="Reds",
        text_auto=".1f",
    )
    fig.update_layout(
        xaxis=dict(tickmode="linear", tick0=0, dtick=1),
        coloraxis_showscale=False,
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Top delayed stations ---
    st.markdown("---")
    st.subheader("Top 10 Most Delayed Stations")

    df_top = get_top_delayed_stations(limit=10)
    if not df_top.empty:
        fig2 = px.bar(
            df_top.sort_values("avg_delay"),
            x="avg_delay",
            y="station_id",
            orientation="h",
            labels={"avg_delay": "Avg Delay (min)", "station_id": "Station"},
            color="avg_delay",
            color_continuous_scale="Oranges",
            text_auto=".1f",
        )
        fig2.update_layout(coloraxis_showscale=False, height=400)
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning(f"No data available for station {selected_station}.")
