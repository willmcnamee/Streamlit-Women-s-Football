import streamlit as st
import pandas as pd
import numpy as np

df = pd.read_csv("C:\\Users\\Willm\\MSc\\Workshops\\8\\ewf_matches.csv")

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
df2 = pd.read_csv("C:\\Users\\Willm\\MSc\\Workshops\\8\\ewf_standings.csv")

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

