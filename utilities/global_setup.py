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
        with st.form("team_selection_form"):
            selected_teamname = st.selectbox(
                label="Select Team",
                options=list(teamcode_mapping.keys()),
                index=list(teamcode_mapping.keys()).index("Nashville Predators"),
                key="selected_team",
            )
            submitted = st.form_submit_button("Load Team")

    # Set team name and code
    st.session_state.selected_teamcode = teamcode_mapping[selected_teamname]

    # Add team logo
    st.logo(
        get_team_logo(st.session_state.selected_teamcode),
        size="large",
    )

    # Load and cache data, and add to session state
    faceoffs_df, player_df = load_data()

    st.session_state["faceoffs_df"] = faceoffs_df
    st.session_state["player_df"] = player_df
