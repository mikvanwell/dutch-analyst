import streamlit as st
import pandas as pd

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
    "The Player Analysis helps you identify the best options for your Fantasy Voetbal "
    "squad based on expected points (xPTS). Instead of relying solely on historical "
    "points, player reputation or current ownership, the model estimates how many "
    "Fantasy points each player is expected to score."
)

st.markdown(
    "The gameweek projections are particularly useful when planning transfers and "
    "squad selection. By comparing expected points across upcoming gameweeks, you can "
    "identify players who offer strong short-term potential, while metrics such as "
    "total xPTS and xPTS per € provide a broader indication of season-long value."
)


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_excel("xpts_playground.xlsx")

    return df


# ---------------------------------------------------------
# Prepare data
# ---------------------------------------------------------

def prepare_data(df):

    # Columns that should be displayed
    columns = [
        "name",
        "team",
        "position",
        "€",
        "xMins",
        "xPTS/M",
        "Total xPTS",
        "xPTS/€"
    ]

    # Add gameweek columns
    gameweek_columns = [
        f"GW{i}"
        for i in range(1, 35)
        if f"GW{i}" in df.columns
    ]

    columns += gameweek_columns

    df = df[columns].copy()

    # Rename columns for display
    df = df.rename(columns={
        "name": "Player",
        "team": "Team",
        "position": "Pos",
        "€": "Price"
    })

    # Sort by total expected points
    df = df.sort_values(
        "Total xPTS",
        ascending=False
    ).reset_index(drop=True)

    return df


# ---------------------------------------------------------
# Style dataframe
# ---------------------------------------------------------

def style_dataframe(df):

    # Columns containing numbers
    number_columns = [
        "Price",
        "xMins",
        "xPTS/M",
        "Total xPTS",
        "xPTS/€"
    ]

    gameweek_columns = [
        col for col in df.columns
        if col.startswith("GW")
    ]

    number_columns += gameweek_columns

    # Alternating row colours
    def row_style(row):

        if row.name % 2 == 0:
            return [
                "background-color: #ffffff;"
                "font-family: 'DM Sans', sans-serif;"
            ] * len(row)

        return [
            "background-color: #f5f5f5;"
            "font-family: 'DM Sans', sans-serif;"
        ] * len(row)

    styled = df.style.apply(
        row_style,
        axis=1
    )

    # Number formatting
    format_dict = {
        "Price": "€{:.1f}",
        "xMins": "{:.1f}",
        "xPTS/M": "{:.2f}",
        "Total xPTS": "{:.1f}",
        "xPTS/€": "{:.2f}"
    }

    for column in gameweek_columns:
        format_dict[column] = "{:.2f}"

    styled = styled.format(format_dict)

    # Hide pandas index
    styled = styled.hide(axis="index")

    return styled


# ---------------------------------------------------------
# Table CSS
# ---------------------------------------------------------

TABLE_CSS = """
<style>

.player-analysis-table {
    width: 100%;
    overflow-x: auto;
}

.player-analysis-table table {
    border-collapse: collapse;
    width: 100%;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
}

.player-analysis-table th {
    background-color: #f2f2f2;
    color: #222;
    font-weight: 700;
    border: 1px solid #d9d9d9;
    padding: 9px 12px;
    text-align: center;
    white-space: nowrap;
}

.player-analysis-table td {
    border: 1px solid #e0e0e0;
    padding: 8px 12px;
    text-align: center;
    white-space: nowrap;
    font-family: 'DM Sans', sans-serif;
}

/* Left-align player and team names */
.player-analysis-table td:nth-child(1),
.player-analysis-table td:nth-child(2) {
    text-align: left;
}

/* Sticky player column */
.player-analysis-table th:first-child,
.player-analysis-table td:first-child {
    position: sticky;
    left: 0;
    z-index: 5;
}

/* Sticky team column */
.player-analysis-table th:nth-child(2),
.player-analysis-table td:nth-child(2) {
    position: sticky;
    left: 120px;
    z-index: 4;
}

/* Keep sticky cells white/grey depending on row */
.player-analysis-table tbody tr:nth-child(odd) td:first-child,
.player-analysis-table tbody tr:nth-child(odd) td:nth-child(2) {
    background-color: #ffffff;
}

.player-analysis-table tbody tr:nth-child(even) td:first-child,
.player-analysis-table tbody tr:nth-child(even) td:nth-child(2) {
    background-color: #f5f5f5;
}

/* Slightly stronger border after player information */
.player-analysis-table th:nth-child(8),
.player-analysis-table td:nth-child(8) {
    border-right: 2px solid #bdbdbd;
}

</style>
"""


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    # Load Excel file
    try:

        player_data = load_data()

    except FileNotFoundError:

        st.error(
            "Please make sure 'xpts_playground.xlsx' "
            "is in the same directory as the Streamlit app."
        )

        return

    except Exception as e:

        st.error(
            f"Unable to read 'xpts_playground.xlsx': {e}"
        )

        return


    # Prepare data
    player_data = prepare_data(player_data)


    # -----------------------------------------------------
    # Filters
    # -----------------------------------------------------

    st.markdown("### Filter Players")

    col1, col2, col3 = st.columns(3)

    with col1:

        positions = ["All"] + sorted(
            player_data["Pos"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_position = st.selectbox(
            "Position",
            positions
        )

    with col2:

        teams = ["All"] + sorted(
            player_data["Team"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_team = st.selectbox(
            "Team",
            teams
        )

    with col3:

        minimum_xpts = st.number_input(
            "Minimum Total xPTS",
            min_value=0.0,
            value=0.0,
            step=5.0
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

    filtered_data = filtered_data[
        filtered_data["Total xPTS"] >= minimum_xpts
    ]


    # -----------------------------------------------------
    # Display table
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


if __name__ == "__main__":
    main()