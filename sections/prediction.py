import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

from utilities.extract import load_team_codes
from utilities.transform import (
    calculate_team_aggregate_win_rates,
    create_ml_df,
)

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    roc_auc_score,
    RocCurveDisplay,
)
from statsmodels.stats.outliers_influence import variance_inflation_factor


def prediction_section(faceoff_df: pd.DataFrame):
    # Get Data for ML Model
    faceoff_df_ml = create_ml_df()

    # Model Filters & Params
    with st.expander("Model Features & Parameters", expanded=False):
        with st.form("ml_model_input"):

            # Feature Inclusion
            model_features = [
                "score_team",
                "score_diff",
                "home",
                "players_diff",
                "seconds_elapsed__game",
                "zone__offense",
                "zone__defense",
                "playerid_team__win_rate",
                "opposing_team__win_rate",
            ]

            cols = st.columns(5)
            with cols[0]:
                st.number_input(
                    label="Max Depth",
                    min_value=1,
                    max_value=10,
                    step=1,
                    value=4,
                    key="max_depth",
                )
            with cols[1]:
                st.number_input(
                    label="N-Estimators",
                    min_value=10,
                    max_value=200,
                    step=5,
                    value=200,
                    key="n_estimators",
                )
            with cols[2]:
                st.number_input(
                    label="Min Samples Split",
                    min_value=0.01,
                    max_value=0.25,
                    step=0.01,
                    value=0.1,
                    key="min_samples_split",
                )
            with cols[3]:
                st.number_input(
                    label="Min Samples Leaf",
                    min_value=0.0,
                    max_value=0.2,
                    step=0.01,
                    value=0.05,
                    key="min_samples_leaf",
                )
            with cols[4]:
                st.number_input(
                    label="Max Features",
                    min_value=None,
                    max_value=15,
                    step=1,
                    value=None,
                    key="max_features",
                )

            st.form_submit_button(label="Train Model", type="primary")

    # Trim Columns to Features and Target
    faceoff_df_ml = faceoff_df_ml[model_features + ["win"]]

    # Select features (exclude target 'win')
    X = faceoff_df_ml.drop(columns=["win"])
    y = faceoff_df_ml["win"]

    # Split Data & Fit and Predict Model
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = RandomForestClassifier(
        random_state=42,
        max_depth=st.session_state.max_depth,
        class_weight="balanced",
        n_estimators=st.session_state.n_estimators,
        min_samples_split=st.session_state.min_samples_split,
        min_samples_leaf=st.session_state.min_samples_leaf,
        max_features=st.session_state.max_features,
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    with st.expander("Model Evaluation", expanded=False):

        # Evaluation Metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)

        metrics = {
            "AUC": auc,
            "Accuracy": accuracy,
            "F1 Score": f1,
            "Precision": precision,
            "Recall": recall,
        }

        # Create 5 columns side-by-side
        cols = st.columns(len(metrics))

        # Loop and place each metric into its own st.metric cell
        for col, (label, value) in zip(cols, metrics.items()):
            with col:
                with st.container(border=True):
                    st.metric(label, f"{value:.1%}")
                    st.progress(value)

        # Check Multicollinearity using VIF
        # vif_data = pd.DataFrame()
        # vif_data["feature"] = X.columns
        # vif_data["VIF"] = [
        #     variance_inflation_factor(X, i) for i in range(X.shape[1])
        # ]

        # st.markdown("#### VIF Scores")
        # st.bar_chart(
        #     data=vif_data,
        #     x="feature",
        #     y="VIF",
        # )

        chart_cols = st.columns([0.97, 1, 0.8])
        # Confusion Matrix
        with chart_cols[0]:
            cm = confusion_matrix(y_test, y_pred)
            fig, ax = plt.subplots()
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
            ax.set_xlabel("Predicted")
            ax.set_ylabel("Actual")
            ax.set_title("Confusion Matrix")
            st.pyplot(fig)

        # Calibration Plot
        with chart_cols[1]:
            prob_true, prob_pred = calibration_curve(y_test, y_proba, n_bins=25)
            fig2, ax2 = plt.subplots()
            ax2.plot(prob_pred, prob_true, marker="o")
            ax2.plot([0, 1], [0, 1], linestyle="--", color="gray")
            ax2.set_xlabel("Predicted probability")
            ax2.set_ylabel("True probability")
            ax2.set_title("Calibration Curve")
            st.pyplot(fig2)

        # ROC Curve
        with chart_cols[2]:
            RocCurveDisplay.from_predictions(y_test, y_proba)
            plt.title("ROC Curve")
            st.pyplot(plt.gcf())

        # Feature Importances
        feat_importances = pd.DataFrame(
            {"feature": X.columns, "importance": model.feature_importances_}
        ).sort_values("importance", ascending=False)

        st.markdown("### Feature Importances")
        st.bar_chart(feat_importances, x="feature", y="importance")

    with st.form("Inputs"):

        st.subheader(
            "Predict Faceoff Winner:",
            divider="gray",
        )
        st.caption("Enter the game situation and match details to predict")

        # Match Description
        cols = st.columns(2)
        with cols[0]:
            st.checkbox(
                f"Is {st.session_state.selected_team} the home team?", key="home"
            )
        with cols[1]:
            st.selectbox(
                "Who is the game against?",
                options=load_team_codes().values(),
                key="opponent",
            )

        # Situation
        cols = st.columns(4)
        with cols[0]:
            st.number_input(
                f"How many more/less players does {st.session_state.selected_teamcode} have?",
                value=0,
                min_value=-2,
                max_value=2,
                key="players_diff",
            )
        with cols[1]:
            st.number_input(
                f"How many seconds have elapsed in the game?",
                min_value=0,
                max_value=(60 * 20 * 3) + (60 * 5),
                key="seconds_elapsed__game",
            )
        with cols[2]:
            st.checkbox(
                f"Is the faceoff in {st.session_state.selected_team} offensive zone?",
                key="zone__offense",
            )

        with cols[3]:
            st.checkbox(
                f"Is the faceoff in {st.session_state.selected_team} defensive zone?",
                key="zone__defense",
            )

        # Points
        cols = st.columns(2)
        with cols[0]:
            st.number_input(
                f"How many points does {st.session_state.selected_team} have?",
                min_value=0,
                value=0,
                key="score_team",
            )
        with cols[1]:
            st.number_input(
                f"How many points is {st.session_state.selected_team} up/down by?",
                value=0,
                key="score_diff",
            )

        st.form_submit_button(
            "Who should take this faceoff?", key="determine_faceoff_taker"
        )

    # Create Dataframe from Inputs
    input_data = {
        key: st.session_state[key]
        for key in [
            "home",
            "players_diff",
            "seconds_elapsed__game",
            "zone__offense",
            "zone__defense",
            "score_team",
            "score_diff",
        ]
    }
    input_df = pd.DataFrame([input_data])
    input_df[["home", "zone__defense", "zone__offense"]] = input_df[
        ["home", "zone__defense", "zone__offense"]
    ].astype(int)

    # Get player aggregate data
    player_agg_df = (
        faceoff_df.groupby("playerid_team")
        .agg(faceoffs=("gameID", "count"), wins=("win", "sum"))
        .reset_index()
    )
    player_agg_df["win_pct"] = (
        player_agg_df["wins"] / player_agg_df["faceoffs"]
    ).round(3)

    # Merge in Individual Team Player Data
    input_df = pd.merge(
        left=input_df,
        right=player_agg_df[["playerid_team", "win_pct"]],
        how="cross",
    )
    input_df.rename(columns={"win_pct": "playerid_team__win_rate"}, inplace=True)

    # Get Aggregate Team Win Rates
    teamcodes_df = pd.DataFrame.from_dict(
        load_team_codes(), orient="index"
    ).reset_index(drop=False)
    teamcodes_df.columns = ["teamname", "teamcode"]

    # Add Aggregate Opponent Win Rate
    teamcodes_df = calculate_team_aggregate_win_rates(teams_df=teamcodes_df)
    opposing_team_win_pct = teamcodes_df[
        teamcodes_df["teamcode"] == st.session_state.opponent
    ]["win_rate"].values[0]
    input_df["opposing_team__win_rate"] = opposing_team_win_pct

    # Trim Columns to Match X
    playerid_series = input_df["playerid_team"]
    input_df = input_df[X.columns]

    with st.expander("Input Dataframes", expanded=False):
        input_df_to_display = input_df.copy()
        input_df_to_display["playerid"] = playerid_series
        st.dataframe(input_df_to_display)

    # Predict Players & Make DataFrame
    predictions = model.predict_proba(input_df)
    predictions_df = pd.DataFrame(predictions)

    # Add Player Info
    predictions_df["playerid_team"] = playerid_series
    predictions_df = (
        predictions_df[["playerid_team", 1]]
        .rename(columns={1: "Chance to Win"})
        .sort_values("Chance to Win", ascending=False)
        .reset_index(drop=True)
    )
    best_players = predictions_df[
        predictions_df["Chance to Win"] == predictions_df["Chance to Win"].max()
    ]

    st.space("small")
    st.markdown(
        f"#### Player(s) with the Highest Chance to Win: {best_players['playerid_team'].tolist()}"
    )
    st.dataframe(
        predictions_df,
        column_config={
            "playerid_team": st.column_config.TextColumn("Player ID"),
            "Chance to Win": st.column_config.ProgressColumn("Win Probability"),
        },
        hide_index=True,
    )
