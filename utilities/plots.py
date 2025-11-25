import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px


def plot_rink_chart(df: pd.DataFrame, height: int = 800):

    # Aggregate by location
    location_summary = (
        df.groupby(["x", "y"])
        .agg(faceoffs=("win", "count"), win_pct=("win", "mean"))
        .reset_index()
    )
    location_summary["label"] = location_summary["win_pct"].apply(lambda x: f"{x:.1%}")

    # Create scatter plot
    fig = px.scatter(
        location_summary,
        x="x",
        y="y",
        size="faceoffs",
        color="win_pct",
        color_continuous_scale="RdBu",
        hover_data={
            "faceoffs": True,
            "win_pct": ":.1%",
            "x": False,
            "y": False,
        },
        size_max=75,
        text="label",
    )

    # Add rink background image
    fig.update_layout(
        xaxis=dict(
            range=[-110, 110],
            showgrid=False,
            zeroline=False,
            visible=False,
        ),
        yaxis=dict(
            range=[-42.5, 42.5],
            showgrid=False,
            zeroline=False,
            visible=False,
            scaleanchor="x",
            scaleratio=1,
        ),
        width=height,
        height=(350 * height) / 800,
        coloraxis_colorbar=dict(title="Win Percentage"),
        images=[
            dict(
                source="https://st4.depositphotos.com/15640006/19621/v/450/depositphotos_196215850-stock-illustration-detailed-illustration-icehockey-rink-field.jpg",
                xref="x",
                yref="y",
                x=-125,
                y=62,
                sizex=250,
                sizey=125,
                sizing="stretch",
                layer="below",
            )
        ],
        margin=dict(l=0, r=0, t=0, b=0),
    )

    # Update trace labels
    fig.update_traces(
        textposition="middle center",
        textfont=dict(color="black", size=12, family="Arial Black"),
    )

    return st.plotly_chart(fig, use_container_width=False)
