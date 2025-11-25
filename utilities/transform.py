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
    df.drop(columns=["Season", "GameNumber"], inplace=True)

    # Digitize period
    df["overtime"] = (df["Period"] == "OT").astype(int)
    df["period"] = df["Period"].replace("OT", 4).astype(str).str[0].astype(int)
    df.drop(columns=["Period"], inplace=True)

    # Transform "Time Remaining" and "TimeElapsed" to seconds remaining/elapsed
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

    df.drop(columns=["TimeRemaining", "TimeElapsed", "TotalSeconds"], inplace=True)

    # Split HomeStrengthID into HomePlayers and AwayPlayers
    df["players_home"] = df["HomeStrengthID"].astype(str).str[0].astype(int)
    df["players_away"] = df["HomeStrengthID"].astype(str).str[1].astype(int)
    df["players_diff"] = df["players_home"] - df["players_away"]
    df.drop(
        columns=["HomeStrengthID", "AwayStrengthID", "HomeStrength", "AwayStrength"],
        inplace=True,
    )

    # Drop other unused columns
    df.drop(columns="League", inplace=True)

    # Decode Zones
    df["HomeZone"] = df["HomeZone"].replace(
        {"Def": "defense", "Off": "offense", "Neu": "neutral"}
    )
    df["AwayZone"] = df["AwayZone"].replace(
        {"Def": "defense", "Off": "offense", "Neu": "neutral"}
    )

    # Set Score columns as integers and create difference
    df["score_home"] = df["HomeScore"].astype(int)
    df["score_away"] = df["AwayScore"].astype(int)
    df["score_diff"] = df["score_home"] - df["score_away"]

    ## ---------------------------------------- ##
    ## RE-ORGANIZE COLUMNS FOR TEAM OF INTEREST ##
    ## ---------------------------------------- ##

    df = df[(df["HomeTeam"] == team_of_interest) | (df["AwayTeam"] == team_of_interest)]

    # Team of Interest & Opponent
    df["team"] = team_of_interest
    df["opponent"] = np.where(
        df["HomeTeam"] == team_of_interest, df["AwayTeam"], df["HomeTeam"]
    )

    # Faceoff Zoning
    df["zone"] = np.where(
        df["HomeTeam"] == team_of_interest,
        df["HomeZone"],
        df["AwayZone"],
    )

    # Select and reorder final columns
    df = df[
        [
            "gameID",
            "team",
            "opponent",
            "season",
            "score_home",
            "score_away",
            "score_diff",
            "players_home",
            "players_away",
            "players_diff",
            "period",
            "overtime",
            "seconds_remaining__period",
            "seconds_remaining__game",
            "seconds_elapsed__period",
            "seconds_elapsed__game",
            "zone",
            "x",
            "y",
            "FOWinTeam",
            "FOWinner",
            "FOLoser",
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
    df.drop(columns=["Height", "Weight", "Shoots"], inplace=True)

    return df
