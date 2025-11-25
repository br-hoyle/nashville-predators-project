import streamlit as st
import pandas as pd


def transform_MMSS_to_seconds(time_str: str) -> int:
    minutes, seconds = map(int, time_str.split(":"))
    return minutes * 60 + seconds


def height_to_inches(h):
    try:
        feet, inches = str(h).split("'")
        return int(feet) * 12 + int(inches)
    except:
        return None


def filter_faceoff_df(df: pd.DataFrame) -> pd.DataFrame:
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
            (filtered_df["power_play"] == 0) & (filtered_df["short_handed"] == 0)
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
            (filtered_df["empty_net"] == 0) & (filtered_df["extra_attacker"] == 0)
        ]

    # Apply score state filter
    if st.session_state.scorestate_filter != "All":
        filtered_df = filtered_df[
            filtered_df["score_state"].lower()
            == st.session_state.scorestate_filter.lower()
        ]

    return filtered_df
