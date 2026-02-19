import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ---------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="Energy Transition Tracker", layout="wide")

st.title("⚡ Europe Energy Transition Tracker")
st.caption("Electricity generation mix by country using Eurostat data")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data_processed/generation_by_source_country_year.csv")
    dom = pd.read_csv("data_processed/dominant_source_country_year.csv")
    return df, dom

df_grouped, dominant_source = load_data()

# ---------------------------------------------------
# COLORS
# ---------------------------------------------------
energy_colors = {
    "Hydro": "#6baed6",
    "Wind": "#ffd92f",
    "Coal": "#252525",
    "Natural Gas": "#74c476",
    "Nuclear": "#e41a1c",
    "Bioenergy": "#006d2c",
    "Geothermal": "#9ecae1"
}

# ---------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------
countries = sorted(df_grouped["geo"].unique())

country = st.sidebar.selectbox(
    "Select Country",
    countries
)

metric = st.sidebar.radio(
    "Metric",
    ["Share (%)", "Generation (GWh)"]
)

use_shares = metric == "Share (%)"

# ---------------------------------------------------
# EXECUTIVE METRICS 
# ---------------------------------------------------
dom_country = (
    dominant_source[dominant_source["geo"] == country]
    .sort_values("TIME_PERIOD")
)

if dom_country.empty:
    st.warning("No dominant-source data available for this country.")
else:
    latest = dom_country.iloc[-1]

    latest_year = int(latest["TIME_PERIOD"])
    latest_source = str(latest["energy_group"])
    latest_share = float(latest["share"]) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest dominant source", latest_source)
    col2.metric("Dominant share", f"{latest_share:.1f}%")
    col3.metric("Latest year", latest_year)

# ---------------------------------------------------
# TRANSITION INSIGHT
# ---------------------------------------------------
st.markdown("### Transition Insight")

if dom_country.empty:
    st.info("No transition insight available for this country (missing dominant-source data).")
else:
    first = dom_country.iloc[0]
    last = dom_country.iloc[-1]

    if first["energy_group"] == last["energy_group"]:
        st.info(
            f"{country} has remained primarily powered by "
            f"**{last['energy_group']}** since {int(first['TIME_PERIOD'])}."
        )
    else:
        st.success(
            f"{country} transitioned from **{first['energy_group']}** "
            f"to **{last['energy_group']}** between "
            f"{int(first['TIME_PERIOD'])} and {int(last['TIME_PERIOD'])}."
        )

# ---------------------------------------------------
# PLOT FUNCTION
# ---------------------------------------------------
def plot_country_mix(df_grouped, country, use_shares=True):

    metric_col = "share" if use_shares else "generation_gwh"
    ylabel = "Share (%)" if use_shares else "Generation (GWh)"

    d = df_grouped[df_grouped["geo"] == country]

    mix = (
        d.pivot(
            index="TIME_PERIOD",
            columns="energy_group",
            values=metric_col
        )
        .fillna(0)
        .sort_index()
    )

    # ---- FORCE CONSISTENT ENERGY ORDER ----
    energy_order = [
        "Hydro",
        "Wind",
        "Coal",
        "Natural Gas",
        "Nuclear",
        "Bioenergy",
        "Geothermal"
    ]

    # add missing sources as zero so legend/order stays stable
    for source in energy_order:
        if source not in mix.columns:
            mix[source] = 0

    # lock column order
    mix = mix[energy_order]


    if use_shares:
        mix = mix * 100

    colors = [energy_colors.get(c, "#999999") for c in mix.columns]

    fig, ax = plt.subplots(figsize=(12, 6))
    mix.plot.area(ax=ax, color=colors, linewidth=0.6, alpha=0.95)

    ax.set_title(f"{country} Electricity Generation Mix")
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.2)

    ax.legend(title="Energy Source", frameon=False)

    plt.tight_layout()
    return fig

# ---------------------------------------------------
# DISPLAY CHART
# ---------------------------------------------------
st.subheader("Country Energy Mix")

fig = plot_country_mix(df_grouped, country, use_shares)
st.pyplot(fig)
