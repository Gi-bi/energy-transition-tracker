import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#e5e7eb",
    "axes.labelcolor": "#374151",
    "xtick.color": "#6b7280",
    "ytick.color": "#6b7280",
    "text.color": "#111827",
    "font.size": 12,
    "axes.titleweight": "bold",
    "axes.titlesize": 16,
})


# ---------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="Energy Transition Tracker", layout="wide")

st.markdown(
    """
    <div style="padding:16px 0 12px 0; border-bottom:1px solid #e5e7eb; margin-bottom:16px;">
        <div style="font-size:50px; font-weight:800; line-height:1.1;">Europe Energy Transition Tracker</div>
        <div style="font-size:20px; color:#6b7280; margin-top:6px;">
            Electricity generation mix by country using Eurostat data
        </div>
        <div style="font-size:16px; color:#9ca3af; margin-top:6px;">
            Built by <b>Jessica Grubbs</b> • Data: Eurostat
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

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

# Consistent ordering across all plots/legends
ENERGY_ORDER = ["Hydro", "Wind", "Coal", "Natural Gas", "Nuclear", "Bioenergy", "Geothermal"]

# ---------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------
countries = sorted(df_grouped["geo"].unique())

country = st.sidebar.selectbox("Select Country", countries)

metric = st.sidebar.radio("Metric", ["Share (%)", "Generation (GWh)"])
use_shares = metric == "Share (%)"

# ---------------------------------------------------
# TABS
# ---------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Country Explorer", "Europe Overview", "Compare Countries", "Transition Stability"]
)

# ---------------------------------------------------
# PLOT FUNCTION
# ---------------------------------------------------
def plot_country_mix(df_grouped, country, use_shares=True):
    metric_col = "share" if use_shares else "generation_gwh"
    ylabel = "Share (%)" if use_shares else "Generation (GWh)"

    d = df_grouped[df_grouped["geo"] == country]

    mix = (
        d.pivot(index="TIME_PERIOD", columns="energy_group", values=metric_col)
        .fillna(0)
        .sort_index()
    )

    # ---- FORCE CONSISTENT ENERGY ORDER ----
    for source in ENERGY_ORDER:
        if source not in mix.columns:
            mix[source] = 0
    mix = mix[ENERGY_ORDER]

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
    ax.grid(axis="y", color="#e5e7eb", linewidth=1)

    ax.legend(title="Energy Source", frameon=False)

    plt.tight_layout()
    return fig

# ---------------------------------------------------
# TAB 1: COUNTRY EXPLORER
# ---------------------------------------------------
with tab1:
    # ---- Executive metrics ----
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

    # ---- Transition insight ----
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

    # ---- Country chart ----
    st.subheader("Country Energy Mix")
    fig = plot_country_mix(df_grouped, country, use_shares)
    st.pyplot(fig)

# ---------------------------------------------------
# TAB 2: EUROPE OVERVIEW
# ---------------------------------------------------
with tab2:
    st.header("Europe Energy Transition Overview")

    eu_transition = (
        dominant_source
        .groupby(["TIME_PERIOD", "energy_group"])
        .size()
        .reset_index(name="country_count")
    )

    eu_pivot = (
        eu_transition
        .pivot(index="TIME_PERIOD", columns="energy_group", values="country_count")
        .fillna(0)
        .sort_index()
    )

    # Keep consistent ordering
    for src in ENERGY_ORDER:
        if src not in eu_pivot.columns:
            eu_pivot[src] = 0
    eu_pivot = eu_pivot[ENERGY_ORDER]

    fig2, ax2 = plt.subplots(figsize=(12, 6))
    colors2 = [energy_colors.get(c, "#999999") for c in eu_pivot.columns]

    eu_pivot.plot.area(ax=ax2, color=colors2, linewidth=0.6, alpha=0.95)

    ax2.set_title("Dominant Electricity Source Across Europe (Country Count)")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Number of Countries")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", alpha=0.2)
    ax2.legend(title="Energy Source", frameon=False)

    plt.tight_layout()
    st.pyplot(fig2)

    # ---- Year snapshot table ----
    st.subheader("🔎 Europe Snapshot by Year")

    min_year = int(dominant_source["TIME_PERIOD"].min())
    max_year = int(dominant_source["TIME_PERIOD"].max())

    year_selected = st.slider(
        "Pick a year",
        min_value=min_year,
        max_value=max_year,
        value=max_year,
        step=1
    )

    snapshot = dominant_source[dominant_source["TIME_PERIOD"] == year_selected].copy()
    snapshot["share_pct"] = snapshot["share"] * 100
    snapshot = snapshot.sort_values("share_pct", ascending=False)

    st.caption(f"Dominant source per country in {year_selected} (sorted by dominant share).")
    display_df = snapshot[["geo", "energy_group", "share_pct"]].rename(
        columns={"geo": "Country", "energy_group": "Dominant Source", "share_pct": "Dominant Share (%)"}
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ---- Download snapshot as CSV ----
    csv_bytes = display_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label=f"Download {year_selected} snapshot (CSV)",
        data=csv_bytes,
        file_name=f"europe_snapshot_{year_selected}.csv",
        mime="text/csv"
    )

with tab3:
    st.header("Compare Countries")

    view = st.radio(
        "View",
        ["Rankings (snapshot)", "Timeline (trend)"],
        horizontal=True,
        key="compare_view"
    )

    if view == "Rankings (snapshot)":
        # Choose year + energy source
        min_year = int(df_grouped["TIME_PERIOD"].min())
        max_year = int(df_grouped["TIME_PERIOD"].max())

        year_cmp = st.slider(
            "Year",
            min_value=min_year,
            max_value=max_year,
            value=max_year,
            step=1,
            key="year_cmp"
        )

        sources = ["All"] + ENERGY_ORDER
        source_cmp = st.selectbox("Energy source", sources, index=0, key="source_cmp")

        metric_cmp = st.radio(
            "Compare by",
            ["Share (%)", "Generation (GWh)"],
            horizontal=True,
            key="metric_cmp"
        )
        use_share_cmp = metric_cmp == "Share (%)"

        # Build a country-year table from df_grouped
        d = df_grouped[df_grouped["TIME_PERIOD"] == year_cmp].copy()

        if use_share_cmp:
            d["value"] = d["share"] * 100
            value_label = "Share (%)"
        else:
            d["value"] = d["generation_gwh"]
            value_label = "Generation (GWh)"

        # Optional filter by source
        if source_cmp != "All":
            d = d[d["energy_group"] == source_cmp]

        # Rank table (top N)
        top_n = st.slider("Top N", 5, 30, 10, 1, key="top_n_rank")

        # If source is All, pick dominant value per country for that year
        if source_cmp == "All":
            ranked = (
                d.sort_values(["geo", "value"], ascending=[True, False])
                 .groupby("geo", as_index=False)
                 .first()
                 .sort_values("value", ascending=False)
            )
            ranked = ranked.rename(columns={"energy_group": "Dominant Source"})
        else:
            ranked = d.sort_values("value", ascending=False).rename(columns={"energy_group": "Source"})
            ranked["Dominant Source"] = ranked["Source"]

        ranked_display = ranked.head(top_n)[["geo", "Dominant Source", "value"]].rename(
            columns={"geo": "Country", "value": value_label}
        )

        st.caption(
            f"Top {top_n} countries in {year_cmp} by {value_label} "
            f"({'dominant source' if source_cmp == 'All' else source_cmp})."
        )
        st.dataframe(ranked_display, use_container_width=True, hide_index=True)

        # Download
        csv_bytes = ranked_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download comparison table (CSV)",
            data=csv_bytes,
            file_name=f"country_comparison_{year_cmp}.csv",
            mime="text/csv",
            key="download_rank_csv"
        )

    else:
        st.caption("Compare how strongly each country’s dominant source leads over time.")

        compare_countries = st.multiselect(
            "Select countries to compare",
            countries,
            default=["Germany", "France", "Spain"],
            key="compare_line_countries"
        )

        if compare_countries:
            compare_df = dominant_source[dominant_source["geo"].isin(compare_countries)].copy()
            compare_df["share_pct"] = compare_df["share"] * 100

            fig3, ax3 = plt.subplots(figsize=(12, 6))

            for c in compare_countries:
                dc = compare_df[compare_df["geo"] == c].sort_values("TIME_PERIOD")
                ax3.plot(
                    dc["TIME_PERIOD"],
                    dc["share_pct"],
                    linewidth=2.5,
                    label=c
                )

            ax3.set_title("Dominant Energy Share Over Time")
            ax3.set_xlabel("Year")
            ax3.set_ylabel("Dominant Share (%)")
            ax3.spines["top"].set_visible(False)
            ax3.spines["right"].set_visible(False)
            ax3.grid(axis="y", color="#e5e7eb")
            ax3.legend(frameon=False)

            plt.tight_layout()
            st.pyplot(fig3)
        else:
            st.info("Select at least one country to display the timeline.")


with tab4:
    st.header("Transition Stability (Volatility)")

    st.caption(
        "Counts how many times each country changes its dominant electricity source over time. "
        "Higher = more volatile transition. Lower = more stable."
    )

    # Ensure correct ordering
    dom_sorted = dominant_source.sort_values(["geo", "TIME_PERIOD"]).copy()

    # For each country, compare each year to previous year and count changes
    dom_sorted["prev_source"] = dom_sorted.groupby("geo")["energy_group"].shift(1)
    dom_sorted["changed"] = (dom_sorted["energy_group"] != dom_sorted["prev_source"]) & dom_sorted["prev_source"].notna()

    volatility = (
        dom_sorted.groupby("geo")["changed"]
        .sum()
        .reset_index(name="dominant_source_changes")
        .sort_values("dominant_source_changes", ascending=False)
    )

    # Add first/last info for storytelling
    first_last = (
        dom_sorted.groupby("geo")
        .agg(
            first_year=("TIME_PERIOD", "min"),
            last_year=("TIME_PERIOD", "max")
        )
        .reset_index()
    )

    volatility = volatility.merge(first_last, on="geo", how="left")

    # Controls
    top_n = st.slider("Show top N most volatile countries", 5, 50, 15, 1, key="vol_topn")

    st.subheader("Most volatile transitions")
    st.dataframe(
        volatility.head(top_n).rename(columns={
            "geo": "Country",
            "dominant_source_changes": "Dominant Source Changes",
            "first_year": "First Year",
            "last_year": "Last Year"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Most stable transitions")
    st.dataframe(
        volatility.sort_values("dominant_source_changes", ascending=True).head(top_n).rename(columns={
            "geo": "Country",
            "dominant_source_changes": "Dominant Source Changes",
            "first_year": "First Year",
            "last_year": "Last Year"
        }),
        use_container_width=True,
        hide_index=True
    )

    # Download full table
    csv_bytes = volatility.rename(columns={
        "geo": "Country",
        "dominant_source_changes": "Dominant Source Changes",
        "first_year": "First Year",
        "last_year": "Last Year"
    }).to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download stability table (CSV)",
        data=csv_bytes,
        file_name="transition_stability_volatility.csv",
        mime="text/csv"
    )

