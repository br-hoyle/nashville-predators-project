import streamlit as st
import pandas as pd
from utilities.extract import get_team_logo, load_data, load_team_codes


def setup_app():

    # Set page configuration
    st.set_page_config(
        layout="wide",
        page_title="NHL Faceoff Data Analysis",
        initial_sidebar_state="expanded",
        page_icon="🏒",
    )

    # Load team code mapping
    teamcode_mapping = load_team_codes()

    # Sidebar for team selection
    with st.sidebar:

        @st.dialog("README", width="large")
        def show_readme():
            st.markdown(
                """
                *Built by **Benjamin Hoyle** (November 2025)*

                This application has been developed to assist the coaching staff of NHL teams in analyzing faceoff 
                data - specifically, to *help identify deeper insights into which players are most effective in various faceoff situations*.

                The provided dataset included detailed information on faceoffs taken during NHL games, including game context (e.g. period, 
                time remaining/elapsed, score, team strength, and faceoff location) and some basic player information
                (e.g., height, weight, handedness).

                This application provides deeper insights using the following methods:
                - **Team Level Analysis**: Analyzing overall team faceoff win percentages across different zones, periods, and situations.
                - **Player Level Analysis**: Evaluating individual player performance in faceoffs, including win percentages in various zones and situations.
                - **Situational Analysis**: Breaking down faceoff performance based on game context, such as score differential, period, and strength situations for different players.
                
                The goal is to empower coaching staff with actionable insights to optimize faceoff strategies and player deployment during games.
                """
            )

        if st.button("Display README", width="stretch", type="primary"):
            show_readme()

        with st.form("team_selection_form"):
            selected_teamname = st.selectbox(
                label="Select Team",
                options=list(teamcode_mapping.keys()),
                index=list(teamcode_mapping.keys()).index("Nashville Predators"),
                key="selected_team",
            )
            submitted = st.form_submit_button("Load Team", type="primary")

        st.markdown("*Built by **Benjamin Hoyle** (November 2025)*")

    # Set team name and code
    st.session_state.selected_teamcode = teamcode_mapping[selected_teamname]

    # Add team logo
    st.logo(
        get_team_logo(st.session_state.selected_teamcode),
        size="large",
    )

    # Load and cache data, and add to session state
    faceoffs_df, player_df = load_data()

    st.session_state["faceoffs_df__raw"] = faceoffs_df
    st.session_state["player_df__raw"] = player_df


def page_footer():

    # Use columns with equal vertical alignment
    st.write("---")
    cols = st.columns([1.5, 6, 1.5])

    with cols[1]:
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
                <img src="https://media.d3.nhle.com/image/private/t_q-best/prd/assets/nhl/logos/nhl_shield_wm_on_dark_fqkbph"
                    style="height:25px;"/>
                <p style="margin: 0; font-size: 0.9rem;">
                    | &nbsp;&nbsp;&nbsp; Developed by <strong>Benjamin Hoyle</strong> |
                    &copy;2025 NHL Faceoff Data Analysis
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
