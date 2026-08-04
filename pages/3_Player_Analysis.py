import streamlit as st
import pandas as pd
import numpy as np

from utils import load_css


st.set_page_config(
    page_title="Player Analysis",
    page_icon="⚽",
    layout="wide"
)

# Load global styling
load_css()


st.title("Player Analysis")

st.markdown(
    "Use the Player Analysis to identify the best Fantasy Voetbal options based on "
    "expected points (xPTS). Rather than relying solely on historical points or "
    "player reputation, the model estimates how many points each player is expected "
    "to score in every gameweek."
)

st.markdown(
    "This makes the analysis particularly useful when planning transfers and squad "
    "selection. A player's overall xPTS can indicate their value over the season, "
    "while the gameweek-by-gameweek projections help identify the best players to "
    "target for specific fixtures."
)


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_excel("xpts_playground.xlsx")

    return df


# ---------------------------------------------------------
# Heatmap colours
# ---------------------------------------------------------

def get_color_from_score(score):

    if pd.isna(score):
        return "background-color: white"

    elif score < 0.15:
        return "background-color: #006400; color: white"

    elif score < 0.40:
        return "background-color: #01fc79"

    elif score < 0.60:
        return "background-color: #e7e7e7"

    elif score < 0.85:
        return "background-color: #ff1751; color: white"

    else:
        return "background-color: #80082e; color: white"


def get_heatmap_score(value, mean_val, std_val, higher_is_better=True):

    if pd.isna(value) or pd.isna(std_val) or std_val == 0:
        return np.nan

    z = (value - mean_val) / std_val

    # Limit the impact of extreme outliers
    z = max(-2, min(2, z))

    if higher_is_better:
        return 0.5 + z / 4

    return 0.5 - z / 4


# ---------------------------------------------------------
# Prepare dataframe
# ---------------------------------------------------------

def prepare_data(df):

    # Columns to display
    base_columns = [
        "name",
        "team",
        "position",
        "€",
        "xMins",
        "xPTS/M",
        "Total xPTS",
        "xPTS/€"
    ]

    gameweek_columns = [
        f"GW{i}"
        for i in range(1, 35)
        if f"GW{i}" in df.columns
    ]

    columns = base_columns + gameweek_columns

    df = df[columns].copy()

    # Rename columns
    df = df.rename(columns={
        "name": "Player",
        "team": "Team",
        "position": "Pos",
        "€": "Price",
        "xMins": "xMins",
        "xPTS/M": "xPTS/M",
        "Total xPTS": "Total xPTS",
        "xPTS/€": "xPTS/€"
    })

    # Sort by Total xPTS
    df = df.sort_values(
        "Total xPTS",
        ascending=False
    ).reset_index(drop=True)

    return df


# ---------------------------------------------------------
# Style dataframe
# ---------------------------------------------------------

def style_dataframe(df):

    gameweek_columns = [
        col for col in df.columns
        if col.startswith("GW")
    ]

    # Calculate means and standard deviations for each GW
    gw_stats = {}

    for col in gameweek_columns:

        gw_stats[col] = (
            df[col].mean(),
            df[col].std()
        )

    def apply_color(value, column):

        # Gameweek heatmap
        if column in gameweek_columns:

            mean_val, std_val = gw_stats[column]

            score = get_heatmap_score(
                value,
                mean_val,
                std_val,
                higher_is_better=True
            )

            return get_color_from_score(score)

        return ""

    styled = df.style.apply(
        lambda row: [
            apply_color(value, row.name)
            for value in row
        ],
        axis=0
    )

    # Number formatting
    format_dict = {
        "Price": "€{:.1f}",
        "xMins": "{:.1f}",
        "xPTS/M": "{:.2f}",
        "Total xPTS": "{:.1f}",
        "xPTS/€": "{:.2f}",
    }

    for col in gameweek_columns:
        format_dict[col] = "{:.2f}"

    styled = styled.format(format_dict)

    # Hide pandas index
    styled = styled.hide(axis="index")

    return styled


# ---------------------------------------------------------
# Page-specific table CSS
# ---------------------------------------------------------

TABLE_CSS = """
<style>

.player-analysis-table {
    overflow-x: auto;
    width: 100%;
}

.player-analysis-table table {
    border-collapse: separate;
    border-spacing: 0;
    width: 100%;
    font-size: 14px;
}

.player-analysis-table th,
.player-analysis-table td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: center;
    white-space: nowrap;
}

.player-analysis-table th {
    background-color: #f2f2f2;
    font-weight: 700;
}

.player-analysis-table th:first-child,
.player-analysis-table td:first-child {
    position: sticky;
    left: 0;
    background-color: white;
    border-right: 2px solid #ddd;
    z-index: 5;
}

.player-analysis-table th:nth-child(2),
.player-analysis-table td:nth-child(2) {
    position: sticky;
    left: 100px;
    background-color: white;
    z-index: 4;
}

</style>
"""


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    # Load data
    try:

        player_data = load_data()

    except FileNotFoundError:

        st.error(
            "Please make sure 'xpts_playground.xlsx' "
            "is in the same directory as the Streamlit app."
        )

        return


    # Prepare data
    player_data = prepare_data(player_data)


    # -----------------------------------------------------
    # Filters
    # -----------------------------------------------------

    st.markdown("### Player Filters")

    col1, col2 = st.columns(2)

    with col1:

        positions = ["All"] + sorted(
            player_data["Pos"].dropna().unique().tolist()
        )

        selected_position = st.selectbox(
            "Position",
            options=positions
        )

    with col2:

        teams = ["All"] + sorted(
            player_data["Team"].dropna().unique().tolist()
        )

        selected_team = st.selectbox(
            "Team",
            options=teams
        )


    # Apply filters
    filtered_data = player_data.copy()

    if selected_position != "All":

        filtered_data = filtered_data[
            filtered_data["Pos"] == selected_position
        ]

    if selected_team != "All":

        filtered_data = filtered_data[
            filtered_data["Team"] == selected_team
        ]


    # -----------------------------------------------------
    # Table
    # -----------------------------------------------------

    styled_data = style_dataframe(filtered_data)

    st.markdown(
        TABLE_CSS,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="player-analysis-table">'
        + styled_data.to_html()
        + '</div>',
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # Legend
    # -----------------------------------------------------

    st.markdown("### xPTS Key")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.markdown(
            """
            <div style="
                background-color: #006400;
                padding: 10px;
                text-align: center;
                color: white;
                border-radius: 5px;
            ">
                Very high xPTS
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div style="
                background-color: #01fc79;
                padding: 10px;
                text-align: center;
                border-radius: 5px;
            ">
                High xPTS
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            """
            <div style="
                background-color: #e7e7e7;
                padding: 10px;
                text-align: center;
                border-radius: 5px;
            ">
                Average xPTS
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            """
            <div style="
                background-color: #ff1751;
                padding: 10px;
                text-align: center;
                color: white;
                border-radius: 5px;
            ">
                Low xPTS
            </div>
            """,
            unsafe_allow_html=True
        )

    with col5:

        st.markdown(
            """
            <div style="
                background-color: #80082e;
                padding: 10px;
                text-align: center;
                color: white;
                border-radius: 5px;
            ">
                Very low xPTS
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()