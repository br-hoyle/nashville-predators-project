import streamlit as st
import pandas as pd


@st.cache_resource(ttl=600)
def load_team_codes() -> pd.DataFrame:
    teamcode_df = pd.read_csv("data/nhl_teamcodes.csv").to_dict(orient="records")
    teamcode_dict = {team["TeamName"]: team["TeamCode"] for team in teamcode_df}
    return teamcode_dict


@st.cache_resource(ttl=600)
def get_team_logo(team_code: str) -> str:
    return "https://assets.nhle.com/logos/nhl/svg/{}_dark.svg".format(team_code)


@st.cache_data(ttl=600)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    faceoffs_df = pd.read_excel(
        "data/Data Analyst Faceoff Project Data.xlsx", sheet_name="NHLFaceOffs"
    )
    player_df = pd.read_excel(
        "data/Data Analyst Faceoff Project Data.xlsx", sheet_name="PlayerInfo"
    )
    return faceoffs_df, player_df
