import streamlit as st
import pandas as pd

from utilities.extract import get_team_logo
from utilities.plots import plot_rink_chart


def player_section(faceoff_df: pd.DataFrame, player_df: pd.DataFrame):

    player_agg_df = (
        faceoff_df.groupby("playerid_team")
        .agg(faceoffs=("gameID", "count"), wins=("win", "sum"))
        .reset_index()
    )
    player_agg_df["win_pct"] = (
        player_agg_df["wins"] / player_agg_df["faceoffs"]
    ).round(3)

    # Add proper checkbox column
    player_agg_df.insert(0, "selected", False)

    # Sort and pre-select first row
    player_agg_df = player_agg_df.sort_values("win_pct", ascending=False)
    player_agg_df.iloc[0, player_agg_df.columns.get_loc("selected")] = True

    st.space(size="small")
    st.subheader("Player Summary", divider="gray")

    cols = st.columns([3.5, 7])
    with cols[0]:
        edited_df = st.data_editor(
            data=player_agg_df,
            width="content",
            height=650,
            hide_index=True,
            disabled=["playerid_team", "faceoffs", "win_pct"],
            column_order=["selected", "playerid_team", "faceoffs", "win_pct"],
            column_config={
                "selected": st.column_config.CheckboxColumn(
                    " ", help="Select a single player"
                ),
                "playerid_team": st.column_config.NumberColumn(
                    "Player ID",
                    help="Unique identifier for each player.",
                ),
                "faceoffs": st.column_config.NumberColumn(
                    "Faceoffs",
                    help="Total number of faceoffs taken.",
                ),
                "win_pct": st.column_config.ProgressColumn(
                    "Win Rate", help="Faceoff win percentage."
                ),
            },
        )

    # Get selected row
    checked_row = edited_df[edited_df["selected"] == True]

    with cols[1]:
        if len(checked_row) > 1:
            st.error("Please only select a single player")
            st.stop()
        elif len(checked_row) == 0:
            st.error("No player selected")
        else:
            # Filter to the selected player
            selected_player_id = checked_row.iloc[0]["playerid_team"]
            player_df_sel = faceoff_df[
                faceoff_df["playerid_team"] == selected_player_id
            ]

            def win_rate(df):
                return df["win"].mean() if len(df) > 0 else 0

            st.subheader(f"Player ID: {selected_player_id}", divider="gray")

            # --- Top Row: Player Info + Rink Chart ---
            top_cols = st.columns([3, 7])

            # Player info
            with top_cols[0]:
                player_row = player_df[
                    player_df["playerid"] == selected_player_id
                ].iloc[0]

                with st.container(border=True):

                    st.image(
                        get_team_logo(st.session_state.selected_teamcode),
                    )

                    st.markdown(
                        f"""  
                            **Height (in):** {player_row['height']:.0f}  
                            **Weight (lb):** {player_row['weight']:.0f}  
                            **Hand:** {player_row['shoots']}  
                            **Overall Win Rate:** {win_rate(player_df_sel):.1%}
                            """
                    )

            # Rink chart
            with top_cols[1]:
                plot_rink_chart(
                    faceoff_df[faceoff_df["playerid_team"] == selected_player_id],
                    height=700,
                )

            # --- Bottom Row: Stats Tables ---
            # By Zone
            zone_wr = player_df_sel.groupby("zone")["win"].mean()

            # By Opponent Handedness
            hand_wr = player_df_sel.groupby("shoots_opponent")["win"].mean()

            # By Strength Situation
            strength_wr = pd.DataFrame(
                {
                    "Power Play": [
                        win_rate(player_df_sel[player_df_sel["power_play"] == 1])
                    ],
                    "Short Handed": [
                        win_rate(player_df_sel[player_df_sel["short_handed"] == 1])
                    ],
                }
            ).T.rename(columns={0: "Win Rate"})

            # By Goalie Situation
            goalie_wr = pd.DataFrame(
                {
                    "Empty Net": [
                        win_rate(player_df_sel[player_df_sel["empty_net"] == 1])
                    ],
                    "Extra Attacker": [
                        win_rate(player_df_sel[player_df_sel["extra_attacker"] == 1])
                    ],
                }
            ).T.rename(columns={0: "Win Rate"})

            # Create bottom row with 4 equal columns
            with st.container(border=True):

                st.markdown("### Win Rate in Dimensions")
                st.caption(
                    f"Quick View on Player {selected_player_id} win rates in different situations."
                )

                bottom_cols = st.columns(4)

                with bottom_cols[0]:
                    zone_wr_df = zone_wr.reset_index()  # Convert Series to DataFrame
                    zone_wr_df.rename(
                        columns={"zone": "Zone", "win": "Win Rate"}, inplace=True
                    )
                    zone_wr_df["Win Rate"] = zone_wr_df["Win Rate"].apply(
                        lambda x: f"{x:.1%}"
                    )
                    st.table(zone_wr_df.set_index("Zone"))

                with bottom_cols[1]:
                    hand_wr_df = hand_wr.reset_index()  # Convert Series to DataFrame
                    hand_wr_df.rename(
                        columns={
                            "shoots_opponent": "Opposing Hand",
                            "win": "Win Rate",
                        },
                        inplace=True,
                    )
                    hand_wr_df["Win Rate"] = hand_wr_df["Win Rate"].apply(
                        lambda x: f"{x:.1%}"
                    )
                    st.table(hand_wr_df.set_index("Opposing Hand"))

                with bottom_cols[2]:
                    st.table(strength_wr.style.format({"Win Rate": "{:.1%}"}))

                with bottom_cols[3]:
                    st.table(goalie_wr.style.format({"Win Rate": "{:.1%}"}))
