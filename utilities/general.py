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
