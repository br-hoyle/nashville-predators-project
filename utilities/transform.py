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
