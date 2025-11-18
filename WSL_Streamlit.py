import streamlit as st
import pandas as pd
import numpy as np

df = pd.read_csv("ewf_matches.csv")

df["total_goals"] = df["home_team_score"] + df["away_team_score"]


st.write("Average attendance by season")


# Convert obvious NA-like strings to NaN
df["attendance"] = df["attendance"].replace(["NA", "N/A", "-", "--", ""], np.nan)

# Now force numeric conversion
df["attendance"] = pd.to_numeric(df["attendance"], errors="coerce")

# Now calculate average by season
avg_attendance = df.groupby("season")["attendance"].mean()


#st.write(avg_attendance)


avg_att_df = avg_attendance.reset_index()  # convert Series → DataFrame

st.bar_chart(avg_att_df, x="season", y="attendance")


#st.write("Goals per game by season")

# Now calculate average by season
#goals_per_game = df.groupby("season")["total_goals"].mean()

#avg_g_df = goals_per_game.reset_index()  # convert Series → DataFrame

#st.line_chart(avg_g_df, x="season", y="total_goals")

# filter
df2 = pd.read_csv("ewf_standings.csv")

st.write("Total points in the WSL since 2010/11")

total_points = df2[df2.tier == 1].groupby("team_name")["points"].sum()

# total_points_df should have team_name and points
total_points_df = (
    df2[df2.tier == 1]
    .groupby("team_name")["points"]
    .sum()
    .reset_index()
    .sort_values(by="points", ascending=False)  # best to worst
)

total_points_df["Rank"] = range(1, len(total_points_df) + 1)

# Reorder columns so Rank is first
total_points_df = total_points_df[["Rank", "team_name", "points"]]

# Reset index completely and drop the old index
total_points_df = total_points_df.reset_index(drop=True)

st.table(total_points_df)

import altair as alt
# Use Altair (rendered natively by Streamlit) instead of matplotlib so charts
# are interactive and avoid an extra heavy dependency. Altair integrates
# well with Streamlit and provides tooltips and responsive rendering.
from pathlib import Path

st.set_page_config(page_title="Women Football Dashboard", layout="wide")

# Default data paths (use workspace-relative `data/` folder so the app runs inside
# this project without needing absolute user-specific paths)
BASE = Path(__file__).resolve().parent
DEFAULT_STANDINGS =  "ewf_standings.csv"
DEFAULT_MATCHES = "ewf_matches.csv"

@st.cache_data
def load_csv(path: Path):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"Could not read CSV at {path}: {e}")
        return None


def plot_top_teams_bar(standings: pd.DataFrame, top_n: int = 5):
    """Return an Altair bar chart for the top N teams by total points."""
    team_points = (
        standings.groupby("team_name")["points"].sum().sort_values(ascending=False).head(top_n)
    )
    df = team_points.reset_index().rename(columns={"team_name": "team", "points": "points"})

    base = (
        alt.Chart(df)
        .encode(
            x=alt.X("team:N", sort="-y", axis=alt.Axis(labelAngle=30, title="Team")),
            y=alt.Y("points:Q", title="Total Points"),
            tooltip=[alt.Tooltip("team:N", title="Team"), alt.Tooltip("points:Q", title="Points")],
        )
    )

    bars = base.mark_bar(color="#2b8cbe").properties(
        title=f"Top {top_n} Teams by Total Points (All Seasons & Tiers)", width=700, height=350
    )

    labels = base.mark_text(dy=-6, color="black").encode(text=alt.Text("points:Q"))

    return (bars + labels)


def plot_donut(values, labels, center_text="", title=""):
    """Return an Altair donut chart (arc with inner radius)."""
    df = pd.DataFrame({"label": labels, "value": values})

    chart = (
        alt.Chart(df)
        .encode(
            theta=alt.Theta("value:Q", stack=True),
            color=alt.Color("label:N", legend=alt.Legend(title=None)),
            tooltip=[alt.Tooltip("label:N", title="Type"), alt.Tooltip("value:Q", title="Count")],
        )
        .mark_arc(innerRadius=60)
        .properties(width=300, height=300, title=title)
    )

    return chart


def main():
    st.title("Women Football — Visualizations from Notebook")
    st.write("This app reproduces the charts from your notebook `women football.ipynb`.")

    # Sidebar controls for file paths and options
    st.sidebar.header("Data & Options")
    standings_path = st.sidebar.text_input("Standings CSV path", str(DEFAULT_STANDINGS))
    matches_path = st.sidebar.text_input("Matches CSV path", str(DEFAULT_MATCHES))

    top_n = st.sidebar.slider("Top N teams", min_value=3, max_value=20, value=5)
    show_points_bar = st.sidebar.checkbox("Show top teams bar chart", value=True)
    show_tier_points = st.sidebar.checkbox("Show tier points donut", value=True)
    show_tier_goals = st.sidebar.checkbox("Show tier goals donut", value=True)
    show_match_outcomes = st.sidebar.checkbox("Show match outcomes donut", value=True)

    standings = load_csv(Path(standings_path))
    matches = load_csv(Path(matches_path))

    if standings is None or matches is None:
        st.stop()

    # Quick data inspection
    st.subheader("Standings — sample")
    st.dataframe(standings.head())

    st.subheader("Matches — sample")
    st.dataframe(matches.head())

    # Top teams bar
    if show_points_bar:
        st.subheader(f"Top {top_n} Teams by Total Points")
        chart = plot_top_teams_bar(standings, top_n=top_n)
        st.altair_chart(chart, use_container_width=True)

    # Tier points donut
    tier_points = standings.groupby("tier")["points"].sum()
    if show_tier_points:
        st.subheader("Points Distribution: Tier 1 vs Tier 2")
        labels = [f"Tier {int(idx)}" for idx in tier_points.index]
        center_text = f"{int(tier_points.sum())} pts"
        chart = plot_donut(tier_points.values, labels, center_text=center_text, title="Points Distribution by Tier")
        st.altair_chart(chart, use_container_width=False)
        st.markdown(f"**{center_text}**")

    # Tier goals donut
    if "goals_for" in standings.columns:
        tier_goals = standings.groupby("tier")["goals_for"].sum()
        if show_tier_goals:
            st.subheader("Goals Scored Distribution: Tier 1 vs Tier 2")
            labels = [f"Tier {int(idx)}" for idx in tier_goals.index]
            center_text = f"{int(tier_goals.sum())} goals"
            chart = plot_donut(tier_goals.values, labels, center_text=center_text, title="Goals by Tier")
            st.altair_chart(chart, use_container_width=False)
            st.markdown(f"**{center_text}**")
    else:
        st.info("No 'goals_for' column found in standings; skipping goals chart.")

    # Match outcomes donut
    # Notebook used 'home_team_win', 'away_team_win', 'draw' columns as booleans or ints
    st.subheader("Match Outcomes")
    needed_cols = ["home_team_win", "away_team_win", "draw"]
    if all(c in matches.columns for c in needed_cols):
        home_wins = int(matches['home_team_win'].sum())
        away_wins = int(matches['away_team_win'].sum())
        draws = int(matches['draw'].sum())
        values = [home_wins, away_wins, draws]
        labels = ["Home Wins", "Away Wins", "Draws"]

        if show_match_outcomes:
            # Render outcomes as a donut chart via Altair and show numeric summary
            chart = plot_donut(values, labels, title=f"Match Outcomes (Total Matches: {sum(values)})")
            st.altair_chart(chart, use_container_width=True)

            # Also show numeric summary
            st.write({"Home Wins": home_wins, "Away Wins": away_wins, "Draws": draws})
    else:
        st.info(f"Matches file missing one of the columns: {needed_cols}")


if __name__ == "__main__":
    main()




