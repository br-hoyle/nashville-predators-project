import streamlit as st
import pandas as pd
import plotly.express as px
from utilities.plots import plot_rink_chart


def team_section(faceoff_df: pd.DataFrame):

    st.subheader("Team Summary", divider="gray")

    cols = st.columns([3, 6])

    with cols[0]:
        # Total Faceoffs
        st.metric(
            label="Total Faceoffs",
            value=f"{len(faceoff_df):,}",
            border=True,
            help="Total number of faceoffs taken by the selected team in the filtered dataset.",
            width="stretch",
        )

        # Win Percentage
        st.metric(
            label="Total Faceoffs",
            value=f"{len(faceoff_df[faceoff_df["team"] == faceoff_df["winner_team"]]) / len(faceoff_df):.1%}",
            border=True,
            help="Faceoff win percentage for the selected team in the filtered dataset.",
            width="stretch",
        )

        # Players Used
        st.metric(
            label="Total Players Used",
            value=f"{len(faceoff_df['playerid_team'].unique()):,d}",
            border=True,
            help="Total number of unique players who took faceoffs for the selected team in the filtered dataset.",
            width="stretch",
        )

    with cols[1]:
        # Plot Rink Chart
        plot_rink_chart(df=faceoff_df, height=800)

    ## ------------------------------------------------------------------ ##
    ## TABLE EXPANDER
    ## ------------------------------------------------------------------ ##
    with st.expander("Summary Table by Selected Dimensions", expanded=False):
        dimensions = st.multiselect(
            label="Select Dimensions for Summary Table",
            options=[
                "opponent",
                "season",
                "period",
                "zone",
                "power_play",
                "short_handed",
                "empty_net",
                "extra_attacker",
                "score_state",
            ],
            default=["opponent"],
            help="Select dimensions to group by for the summary table below",
            key="table_dimensions",
        )

        # Show error if no dimensions selected
        if dimensions == []:
            st.error(
                "Please select at least one dimension to display the summary table."
            )
        else:
            # Calculate Win Percentage by Dimensions
            summary_df = (
                faceoff_df.groupby(dimensions)
                .agg(faceoffs=("gameID", "count"), wins=("win", "sum"))
                .reset_index()
            )
            summary_df["win_pct"] = summary_df["wins"] / summary_df["faceoffs"]

            # Show Dataframe
            st.dataframe(
                summary_df.rename(columns=lambda x: x.replace("_", " ").title()),
                column_config={
                    "Win Pct": st.column_config.ProgressColumn(
                        "Win Percentage",
                    ),
                },
                use_container_width=True,
                hide_index=True,
                height=275,
            )
