import streamlit as st
import pandas as pd
import plotly.express as px

# Import modules
from utilities.global_setup import setup_app, page_footer
from utilities.extract import get_team_logo, load_team_codes
from utilities.transform import faceoff_cleaning, player_cleaning
from utilities.plots import plot_rink_chart

from sections.team import team_section
from sections.player import player_section


def main():

    st.markdown(
        """
        <style>
            /* Remove padding above the main container */
            .block-container {
                padding-top: 2.5rem !important;
                padding-left: 5rem !important;
            }
            
    """,
        unsafe_allow_html=True,
    )

    # Setup the app
    setup_app()

    # Clean the faceoff data
    faceoff_df = faceoff_cleaning(
        st.session_state.faceoffs_df__raw,
        team_of_interest=st.session_state.selected_teamcode,
    )

    # Clean the player data
    player_df = player_cleaning(
        st.session_state.player_df__raw,
    )

    # Map Player Info into FaceOff Data
    faceoff_df = pd.merge(
        left=faceoff_df,
        right=player_df.rename(
            columns={
                col: f"{col}_team" for col in player_df.columns if col != "playerid"
            }
        ).rename(columns={"playerid": "playerid_team"}),
        on="playerid_team",
        copy=False,
        how="inner",
    )
    faceoff_df = pd.merge(
        left=faceoff_df,
        right=player_df.rename(
            columns={
                col: f"{col}_opponent" for col in player_df.columns if col != "playerid"
            }
        ).rename(columns={"playerid": "playerid_opponent"}),
        on="playerid_opponent",
        how="inner",
    )

    # Load cleaned data into session state
    st.session_state["faceoff_df"], st.session_state["player_df"] = (
        faceoff_df,
        player_df,
    )

    ## -------------------------------------------------------------- ##
    ## PAGE TITLE
    ## -------------------------------------------------------------- ##
    cols = st.columns([1.5, 10, 1])
    with cols[0]:
        st.image(get_team_logo(st.session_state.selected_teamcode), width="stretch")
    with cols[1]:
        st.title(st.session_state.selected_team)

    ## -------------------------------------------------------------- ##
    ## LOAD NECESSARY DATAFRAMES
    ## -------------------------------------------------------------- ##

    teamcode_mapping = load_team_codes()
    faceoff_df = st.session_state.faceoff_df
    player_df = st.session_state.player_df

    ## ------------------------------------------------------------------ ##
    ## CREATE TABS
    ## ------------------------------------------------------------------ ##
    summary_tab, predict_tab = st.tabs(["Summary", "ML Model"])

    with summary_tab:

        ## -------------------------------------------------------------- ##
        ## FILTERS
        ## -------------------------------------------------------------- ##
        with st.expander("Filters", expanded=False):
            with st.form("filter_form"):

                st.markdown("#### Match")
                st.multiselect(
                    label="Select Opponent",
                    options=sorted(
                        st.session_state.faceoff_df["opponent"].unique().tolist()
                    ),
                    format_func=lambda x: (
                        list(teamcode_mapping.keys())[
                            list(teamcode_mapping.values()).index(x)
                        ]
                    ),
                    placeholder="All Teams",
                    key="opponent_filter",
                )

                cols = st.columns(3)
                with cols[0]:
                    st.pills(
                        "Select Season",
                        options=sorted(
                            st.session_state.faceoff_df["season"].unique().tolist()
                        ),
                        default=sorted(
                            st.session_state.faceoff_df["season"].unique().tolist()
                        ),
                        selection_mode="multi",
                        width="stretch",
                        key="season_filter",
                    )
                with cols[1]:
                    st.pills(
                        "Select Period",
                        options=sorted(
                            st.session_state.faceoff_df["period"].unique().tolist()
                        ),
                        default=sorted(
                            st.session_state.faceoff_df["period"].unique().tolist()
                        ),
                        selection_mode="multi",
                        width="stretch",
                        format_func=lambda x: f"{x}" if x < 4 else "Overtime",
                        key="period_filter",
                    )
                with cols[2]:
                    st.pills(
                        "Select Zone",
                        options=sorted(
                            st.session_state.faceoff_df["zone"].unique().tolist()
                        ),
                        default=sorted(
                            st.session_state.faceoff_df["zone"].unique().tolist()
                        ),
                        selection_mode="multi",
                        format_func=lambda x: x.title(),
                        width="stretch",
                        key="zone_filter",
                    )

                st.radio(
                    "Select Location",
                    options=["All", "Home", "Away"],
                    horizontal=True,
                    index=0,
                    width="stretch",
                    key="home_filter",
                )

                st.markdown("#### Situation")

                cols = st.columns(3)
                with cols[0]:
                    st.selectbox(
                        "Strength",
                        options=["All", "Power Play", "Even Strength", "Short Handed"],
                        placeholder="All",
                        help="Strength of the selected team: \n - Are they on a Power Play? Select 'Power Play' \n - Are both teams at Even Strength? Select 'Even Strength' \n - Are they Short Handed? Select 'Short Handed'",
                        key="strength_filter",
                    )
                with cols[1]:
                    st.selectbox(
                        "Net Situation",
                        options=["All", "Standard", "Empty Net", "Extra Attacker"],
                        help="Situation the Home Team is facing: \n - Do both teams have their goalies in play? Select 'Standard' \n - Are they attacking an empty net? Select 'Empty Net' \n - Do they have an extra attacker? Select 'Extra Attacker'",
                        placeholder="All",
                        key="net_filter",
                    )
                with cols[2]:
                    st.selectbox(
                        "Score State",
                        options=["All", "Leading", "Tied", "Trailing"],
                        help="Score state of the selected team at the time of the faceoff: \n - Are they leading? Select 'Leading' \n - Is the score tied? Select 'Tied' \n - Are they trailing? Select 'Trailing'",
                        placeholder="All",
                        key="scorestate_filter",
                    )

                submitted = st.form_submit_button("Apply Filters")

        ## ------------------------------------------------------------------ ##
        ## APPLY FILTERS TO DATAFRAME
        ## ------------------------------------------------------------------ ##

        def filter_faceoff_df(df: pd.DataFrame) -> pd.DataFrame:
            """Apply filters from session state to faceoff dataframe."""
            filtered_df = df.copy()

            # Apply Home Filter
            if st.session_state.home_filter == "Home":
                filtered_df = filtered_df[filtered_df["home"] == 1]
            elif st.session_state.home_filter == "Away":
                filtered_df = filtered_df[filtered_df["home"] == 0]

            # Apply opponent filter
            if st.session_state.opponent_filter != []:
                filtered_df = filtered_df[
                    filtered_df["opponent"].isin(st.session_state.opponent_filter)
                ]

            # Apply season filter
            if st.session_state.season_filter != []:
                filtered_df = filtered_df[
                    filtered_df["season"].isin(st.session_state.season_filter)
                ]
            # Apply period filter
            if st.session_state.period_filter != []:
                filtered_df = filtered_df[
                    filtered_df["period"].isin(st.session_state.period_filter)
                ]
            # Apply zone filter
            if st.session_state.zone_filter != []:
                filtered_df = filtered_df[
                    filtered_df["zone"].isin(st.session_state.zone_filter)
                ]

            # Apply strength filter
            if st.session_state.strength_filter == "Power Play":
                filtered_df = filtered_df[filtered_df["power_play"] == 1]
            elif st.session_state.strength_filter == "Even Strength":
                filtered_df = filtered_df[
                    (filtered_df["power_play"] == 0)
                    & (filtered_df["short_handed"] == 0)
                ]
            elif st.session_state.strength_filter == "Short Handed":
                filtered_df = filtered_df[filtered_df["short_handed"] == 1]

            # Apply net situation filter
            if st.session_state.net_filter == "Empty Net":
                filtered_df = filtered_df[filtered_df["empty_net"] == 1]
            elif st.session_state.net_filter == "Extra Attacker":
                filtered_df = filtered_df[filtered_df["extra_attacker"] == 1]
            elif st.session_state.net_filter == "Standard":
                filtered_df = filtered_df[
                    (filtered_df["empty_net"] == 0)
                    & (filtered_df["extra_attacker"] == 0)
                ]

            # Apply score state filter
            if st.session_state.scorestate_filter != "All":
                filtered_df = filtered_df[
                    filtered_df["score_state"].lower()
                    == st.session_state.scorestate_filter.lower()
                ]

            return filtered_df

        faceoff_df = filter_faceoff_df(faceoff_df)

        ## ------------------------------------------------------------------ ##
        ## TEAM METRICS & CHART
        ## ------------------------------------------------------------------ ##

        team_section(faceoff_df=faceoff_df)

        ## ------------------------------------------------------------------ ##
        ## PLAYER ANALYSIS
        ## ------------------------------------------------------------------ ##

        player_section(faceoff_df=faceoff_df, player_df=player_df)

    ## ---------------------------------------------------------------------------------------------------- ##
    ## ---------------------------------------------------------------------------------------------------- ##
    ## ---------------------------------------------------------------------------------------------------- ##

    with predict_tab:

        ## -------------------------------------------------------------- ##
        ## FILTERS
        ## -------------------------------------------------------------- ##

        st.write("hello!")


if __name__ == "__main__":
    main()
    page_footer()
