import streamlit as st
import pandas as pd
import numpy as np
from utilities.extract import load_team_codes
from utilities.general import transform_MMSS_to_seconds, height_to_inches


def faceoff_cleaning(df: pd.DataFrame, team_of_interest: str) -> pd.DataFrame:

    ## --------------------- ##
    ## GENERIC DATA CLEANING ##
    ## --------------------- ##

    # Replace Team Names with Team Codes
    teamcodes = load_team_codes()
    df["HomeTeam"] = df["HomeTeam"].map(teamcodes)
    df["AwayTeam"] = df["AwayTeam"].map(teamcodes)
    df["FOWinTeam"] = df["FOWinTeam"].map(teamcodes)

    # Digitize season & GameNumber
    df["season"] = df["Season"].str[:4].astype(int)
    df["gameID"] = df["GameNumber"].astype(int)

    # Digitize period
    df["overtime"] = (df["Period"] == "OT").astype(int)
    df["period"] = df["Period"].replace("OT", 4).astype(str).str[0].astype(int)

    # Transform "Time Remaining" and "TimeElapsed" to seconds
    df["seconds_remaining__period"] = df["TimeRemaining"].apply(
        transform_MMSS_to_seconds
    )
    df["seconds_remaining__game"] = np.where(
        df["overtime"] == 1,
        df["seconds_remaining__period"],
        (3 - df["period"]) * 20 * 60 + df["seconds_remaining__period"],
    )
    df["seconds_elapsed__period"] = df["TimeElapsed"].apply(transform_MMSS_to_seconds)
    df["seconds_elapsed__game"] = (df["period"] - 1) * 20 * 60 + df[
        "seconds_elapsed__period"
    ]

    # Extract strength info
    df["players_home"] = df["HomeStrengthID"].astype(str).str[0].astype(int)
    df["players_away"] = df["HomeStrengthID"].astype(str).str[1].astype(int)

    df["power_play"] = df["HomeStrength"].isin(["PP EN", "PP EA", "PP"]).astype(int)
    df["short_handed"] = df["HomeStrength"].isin(["SH EN", "SH EA", "SH"]).astype(int)
    df["empty_net"] = df["HomeStrength"].isin(["SH EN", "PP EN", "EN"]).astype(int)
    df["extra_attacker"] = df["HomeStrength"].isin(["SH EA", "PP EA", "EA"]).astype(int)

    df.drop(columns="League", inplace=True)

    # Decode Zones
    df["HomeZone"] = df["HomeZone"].replace(
        {"Def": "defense", "Off": "offense", "Neu": "neutral"}
    )
    df["AwayZone"] = df["AwayZone"].replace(
        {"Def": "defense", "Off": "offense", "Neu": "neutral"}
    )

    # Scores
    df["score_home"] = df["HomeScore"].astype(int)
    df["score_away"] = df["AwayScore"].astype(int)

    ## ---------------------------------------- ##
    ## RE-ORGANIZE COLUMNS FOR TEAM OF INTEREST ##
    ## ---------------------------------------- ##

    df = df[(df["HomeTeam"] == team_of_interest) | (df["AwayTeam"] == team_of_interest)]

    # Team & Opponent
    df["team"] = team_of_interest
    df["opponent"] = np.where(
        df["HomeTeam"] == team_of_interest, df["AwayTeam"], df["HomeTeam"]
    )
    df["home"] = (df["HomeTeam"] == team_of_interest).astype(int)

    # Re-map scores to team/opponent perspective
    df["score_team"] = np.where(
        df["HomeTeam"] == team_of_interest, df["score_home"], df["score_away"]
    )
    df["score_opponent"] = np.where(
        df["HomeTeam"] == team_of_interest, df["score_away"], df["score_home"]
    )
    df["score_diff"] = df["score_team"] - df["score_opponent"]

    # Players on ice for team/opponent
    df["players_team"] = np.where(
        df["HomeTeam"] == team_of_interest, df["players_home"], df["players_away"]
    )
    df["players_opponent"] = np.where(
        df["HomeTeam"] == team_of_interest, df["players_away"], df["players_home"]
    )
    df["players_diff"] = df["players_team"] - df["players_opponent"]

    # Score State
    df["score_state"] = np.where(
        df["score_diff"] > 0,
        "leading",
        np.where(df["score_diff"] < 0, "trailing", "tied"),
    )

    # Faceoff Zone
    df["zone"] = np.where(
        df["HomeTeam"] == team_of_interest, df["HomeZone"], df["AwayZone"]
    )

    # Winner / Loser perspective
    df["playerid_team"] = np.where(
        df["FOWinTeam"] == df["team"], df["FOWinner"], df["FOLoser"]
    )
    df["playerid_opponent"] = np.where(
        df["FOWinTeam"] == df["opponent"], df["FOWinner"], df["FOLoser"]
    )
    df["winner_team"] = df["FOWinTeam"]
    df["winner_playerid"] = df["FOWinner"]
    df["win"] = (df["team"] == df["winner_team"]).astype(int)

    # Final column selection
    df = df[
        [
            "gameID",
            "team",
            "opponent",
            "season",
            "home",
            "score_team",
            "score_opponent",
            "score_diff",
            "score_state",
            "players_team",
            "players_opponent",
            "players_diff",
            "power_play",
            "short_handed",
            "empty_net",
            "extra_attacker",
            "period",
            "overtime",
            "seconds_remaining__period",
            "seconds_remaining__game",
            "seconds_elapsed__period",
            "seconds_elapsed__game",
            "zone",
            "x",
            "y",
            "playerid_team",
            "playerid_opponent",
            "winner_team",
            "winner_playerid",
            "win",
        ]
    ]

    return df


def player_cleaning(df: pd.DataFrame) -> pd.DataFrame:

    # Transform height to inches, and fill missing with median
    df["height"] = df["Height"].apply(height_to_inches)
    df["height"].fillna(df["height"].median(), inplace=True)

    # Fill missing weight with median
    df["weight"] = df["Weight"].fillna(df["Weight"].median())

    # Fill missing shooting hand with mode (most common)
    df["shoots"] = df["Shoots"].fillna(df["Shoots"].mode()[0])

    # Drop original columns
    df.drop(columns=["Height", "Weight", "Shoots", "Nationality"], inplace=True)

    df.columns = map(str.lower, df.columns)

    return df


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


def calculate_team_aggregate_win_rates(teams_df: pd.DataFrame):
    home_faceoffs = st.session_state.faceoffs_df__raw.rename(
        columns={"HomeTeam": "teamcode"}
    ).assign(location="home")
    away_faceoffs = st.session_state.faceoffs_df__raw.rename(
        columns={"AwayTeam": "teamcode"}
    ).assign(location="away")

    # Combine them
    all_faceoffs = pd.concat([home_faceoffs, away_faceoffs], ignore_index=True)

    # Add a column indicating if the team won this faceoff
    all_faceoffs["faceoff_won"] = all_faceoffs["teamcode"] == all_faceoffs["FOWinTeam"]

    # Group by team and aggregate
    faceoff_stats = (
        all_faceoffs.groupby("teamcode")
        .agg(
            total_faceoffs=("faceoff_won", "count"),
            faceoffs_won=("faceoff_won", "sum"),
        )
        .reset_index()
    )

    # Calculate win rate
    faceoff_stats["win_rate"] = (
        faceoff_stats["faceoffs_won"] / faceoff_stats["total_faceoffs"]
    )

    # Join with team names
    teams_df = faceoff_stats.merge(teams_df, on="teamcode")

    # Reorder columns as desired
    teams_df = teams_df[
        ["teamcode", "teamname", "total_faceoffs", "faceoffs_won", "win_rate"]
    ]

    return teams_df


def create_ml_df():
    faceoff_df_ml = st.session_state.faceoff_df

    # Create Scoring Booleans
    faceoff_df_ml["score__trailing"] = (faceoff_df_ml["score_diff"] < 0).astype(int)
    faceoff_df_ml["score__leading"] = (faceoff_df_ml["score_diff"] > 0).astype(int)

    # Create Zone Booleans
    faceoff_df_ml["zone__offense"] = (faceoff_df_ml["zone"] == "offense").astype(int)
    faceoff_df_ml["zone__defense"] = (faceoff_df_ml["zone"] == "defense").astype(int)

    # Create player differences
    faceoff_df_ml["height_diff"] = (
        faceoff_df_ml["height_team"] - faceoff_df_ml["height_opponent"]
    )
    faceoff_df_ml["weight_diff"] = (
        faceoff_df_ml["weight_team"] - faceoff_df_ml["weight_opponent"]
    )

    # Create Shoots Same Boolean
    faceoff_df_ml["shoots_same"] = (
        faceoff_df_ml["shoots_team"] == faceoff_df_ml["shoots_opponent"]
    ).astype(int)

    # Player Features
    player_agg_df = (
        st.session_state.faceoff_df.groupby("playerid_team")
        .agg(
            playerid_team__faceoffs=("gameID", "count"),
            playerid_team__wins=("win", "sum"),
        )
        .reset_index()
    )
    player_agg_df["playerid_team__win_rate"] = (
        player_agg_df["playerid_team__wins"] / player_agg_df["playerid_team__faceoffs"]
    ).round(3)

    faceoff_df_ml = pd.merge(
        left=faceoff_df_ml, right=player_agg_df, how="inner", on="playerid_team"
    )

    # Create dataframe of team codes
    teamcodes_df = pd.DataFrame.from_dict(
        load_team_codes(), orient="index"
    ).reset_index(drop=False)
    teamcodes_df.columns = ["teamname", "teamcode"]

    teamcodes_df = calculate_team_aggregate_win_rates(teams_df=teamcodes_df)

    # Add opposing team win rate as feature
    faceoff_df_ml = pd.merge(
        left=faceoff_df_ml,
        right=teamcodes_df.rename(
            columns={
                "teamcode": "opponent",
                "win_rate": "opposing_team__win_rate",
            }
        )[["opponent", "opposing_team__win_rate"]],
        how="left",
        on="opponent",
    )

    return faceoff_df_ml
