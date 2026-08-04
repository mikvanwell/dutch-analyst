import streamlit as st
import pandas as pd
import numpy as np

from utils import load_css


st.set_page_config(
    page_title="Team Data",
    page_icon="📊",
    layout="wide"
)

# Load global styling
load_css()


st.title("Team Data")

st.markdown(
    "Underlying data (non-penalty and adjusted expected goals) for every Eredivisie team, "
    "based on their 25/26 performance. "
    "The data will be updated throughout the 26/27 season and those changes will also be reflected in the FDR Schedule."
)


# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("fdr_data.csv")
    return df


def prepare_data(df):

    # Keep only relevant columns
    df = df[
        [
            "team_id",
            "npxG",
            "npxGA",
            "adjxG_per",
            "adjxGA_per",
            "xGA_pershot"
        ]
    ].copy()

    # Rename columns
    df = df.rename(columns={
        "team_id": "Team",
        "adjxG_per": "adjxG",
        "adjxGA_per": "adjxGA"
    })

    # Goal difference columns
    df["npxG_diff"] = df["npxG"] - df["npxGA"]
    df["adjxG_diff"] = df["adjxG"] - df["adjxGA"]

    # Rank teams based on adjusted xG difference
    df["xRank"] = (
        df["adjxG_diff"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    # Sort by rank
    df = df.sort_values("xRank").reset_index(drop=True)

    # Final column order
    df = df[
        [
            "Team",
            "xRank",
            "adjxG",
            "adjxGA",
            "adjxG_diff",
            "npxG",
            "npxGA",
            "npxG_diff",
            "xGA_pershot"
        ]
    ]

    return df


# Convert score to heatmap color
def get_color_from_score(score):

    if pd.isna(score):
        return "background-color: white"

    elif score < 0.15:
        return "background-color: #006400; color: white"

    elif score < 0.4:
        return "background-color: #01fc79"

    elif score < 0.6:
        return "background-color: #e7e7e7"

    elif score < 0.85:
        return "background-color: #ff1751; color: white"

    else:
        return "background-color: #80082e; color: white"


# Calculate heatmap score based on standard deviations from mean
def get_heatmap_score(
    value,
    mean_val,
    std_val,
    higher_is_better
):

    if pd.isna(value) or std_val == 0 or pd.isna(std_val):
        return np.nan

    z = (value - mean_val) / std_val

    # Limit influence of extreme outliers
    z = max(-2, min(2, z))

    if higher_is_better:
        return 0.5 - z / 4

    return 0.5 + z / 4


def style_dataframe(df):

    adjxg_mean = df["adjxG"].mean()
    adjxg_std = df["adjxG"].std()

    adjxga_mean = df["adjxGA"].mean()
    adjxga_std = df["adjxGA"].std()

    def apply_color(val, col_name):

        if col_name == "adjxG":

            score = get_heatmap_score(
                val,
                adjxg_mean,
                adjxg_std,
                higher_is_better=True
            )

            return get_color_from_score(score)

        elif col_name == "adjxGA":

            score = get_heatmap_score(
                val,
                adjxga_mean,
                adjxga_std,
                higher_is_better=False
            )

            return get_color_from_score(score)

        return ""

    styled = df.style.apply(
        lambda x: [
            apply_color(val, x.name)
            for val in x
        ],
        axis=0
    )

    # Number formatting
    styled = styled.format({
        "xRank": "{:.0f}",
        "adjxG": "{:.2f}",
        "adjxGA": "{:.2f}",
        "adjxG_diff": "{:+.2f}",
        "npxG": "{:.2f}",
        "npxGA": "{:.2f}",
        "npxG_diff": "{:+.2f}",
        "xGA_pershot": "{:.3f}",
    })

    # Hide index
    styled = styled.hide(axis="index")

    # Display column names
    styled = styled.relabel_index(
        [
            "Team",
            "xRank",
            "adjxG",
            "adjxGA",
            "adjxG diff",
            "npxG",
            "npxGA",
            "npxG diff",
            "xGA per shot"
        ],
        axis="columns"
    )

    return styled


# Page-specific table CSS
TABLE_CSS = """
<style>

.team-data-table table {
    border-collapse: separate;
    border-spacing: 0;
    width: 100%;
    font-size: 14px;
}

.team-data-table th,
.team-data-table td {
    border: 1px solid #ddd;
    padding: 10px 14px;
    text-align: center;
}

.team-data-table th {
    background-color: #f2f2f2;
    font-weight: 700;
}

.team-data-table th:first-child,
.team-data-table td:first-child {
    position: sticky;
    left: 0;
    background-color: white;
    border-right: 2px solid #ddd;
}

</style>
"""


def main():

    try:
        fdr_data = load_data()

    except FileNotFoundError:

        st.error(
            "Please make sure 'fdr_data.csv' is in the same directory."
        )

        return

    team_data = prepare_data(fdr_data)

    styled_data = style_dataframe(team_data)

    st.markdown(
        TABLE_CSS,
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="team-data-table">'
        f'{styled_data.to_html()}'
        f'</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()