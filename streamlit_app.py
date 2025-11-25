import streamlit as st

# Import modules
from utilities.global_setup import setup_app
from utilities.transform import faceoff_cleaning, player_cleaning


def main():
    # Setup the app
    setup_app()

    # Clean the faceoff data
    faceoff_df = faceoff_cleaning(
        st.session_state.faceoffs_df,
        team_of_interest=st.session_state.selected_teamcode,
    )
    player_df = player_cleaning(
        st.session_state.player_df,
    )
    st.dataframe(player_df.head(100))

    st.dataframe(
        faceoff_df.head(10000),
    )

    faceoff_df.head(10000).to_csv("data/cleaned_faceoff_data.csv", index=False)


if __name__ == "__main__":
    main()
