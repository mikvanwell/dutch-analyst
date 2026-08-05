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
    "This page helps you identify the best options for your Fantasy Voetbal "
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

    df = pd.read_excel("xpts_schedule.xlsx")

    return df


# ---------------------------------------------------------
# Prepare data
# ---------------------------------------------------------

def prepare_data(df):

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

    return df


# ---------------------------------------------------------
# Style dataframe
# ---------------------------------------------------------
# Uses Streamlit's theme CSS variables so the alternating stripe colours
# (and the text colour) automatically match whichever theme (light/dark)
# the user has selected, instead of being hardcoded to white/black.

def style_dataframe(df):

    gameweek_columns = [
        col for col in df.columns
        if col.startswith("GW")
    ]

    def row_style(row):

        if row.name % 2 == 0:

            return [
                "background-color: var(--background-color); "
                "color: var(--text-color);"
            ] * len(row)

        return [
            "background-color: var(--secondary-background-color); "
            "color: var(--text-color);"
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
# Backgrounds, text and borders below use Streamlit's theme CSS variables
# (--background-color, --secondary-background-color, --text-color) rather
# than hardcoded hex values, so the table follows the app's light/dark
# theme automatically. Borders use a translucent grey (rgba) so they read
# correctly against either a light or dark background.

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
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    font-weight: 700;
    border: 1px solid rgba(128, 128, 128, 0.35);
    padding: 9px 12px;
    text-align: center;
    white-space: nowrap;
}

.player-analysis-table td {
    border: 1px solid rgba(128, 128, 128, 0.25);
    padding: 8px 12px;
    text-align: center;
    white-space: nowrap;
}

/* Player and team names */
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

/* Keep sticky cell consistent with alternating rows */
.player-analysis-table tbody tr:nth-child(odd) td:first-child {
    background-color: var(--background-color);
}

.player-analysis-table tbody tr:nth-child(even) td:first-child {
    background-color: var(--secondary-background-color);
}

/* Separate player information from gameweek data */
.player-analysis-table th:nth-child(8),
.player-analysis-table td:nth-child(8) {
    border-right: 2px solid rgba(128, 128, 128, 0.45);
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
            "Please make sure 'xpts_schedule.xlsx' "
            "is in the same directory as the Streamlit app."
        )

        return

    except Exception as e:

        st.error(
            f"Unable to read 'xpts_schedule.xlsx': {e}"
        )

        return


    # Prepare data
    player_data = prepare_data(player_data)


    # -----------------------------------------------------
    # Filters & sorting
    # -----------------------------------------------------

    st.markdown("### Filter & Sort Players")

    col1, col2, col3, col4 = st.columns([1, 1, 1.5, 1])


    # Position filter
    with col1:

        positions = ["All"] + sorted(
            player_data["Pos"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_position = st.selectbox(
            "Position",
            options=positions
        )


    # Team filter
    with col2:

        teams = ["All"] + sorted(
            player_data["Team"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_team = st.selectbox(
            "Team",
            options=teams
        )


    # Price filter
    with col3:

        min_price = float(
            player_data["Price"].min()
        )

        max_price = float(
            player_data["Price"].max()
        )

        selected_price = st.slider(
            "Price (€)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=0.1
        )


    # Sort column
    with col4:

        sort_options = [
            "Total xPTS",
            "xPTS/M",
            "xPTS/€",
            "Price",
            "xMins",
            "Player",
            "Team",
            "Pos"
        ]

        selected_sort = st.selectbox(
            "Sort by",
            options=sort_options
        )


    # -----------------------------------------------------
    # Sort direction
    # -----------------------------------------------------

    sort_ascending = st.radio(
        "Sort direction",
        options=["Highest → Lowest", "Lowest → Highest"],
        horizontal=True
    )

    ascending = sort_ascending == "Lowest → Highest"


    # -----------------------------------------------------
    # Apply filters
    # -----------------------------------------------------

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
        (filtered_data["Price"] >= selected_price[0])
        & (filtered_data["Price"] <= selected_price[1])
    ]


    # -----------------------------------------------------
    # Sort data
    # -----------------------------------------------------

    filtered_data = filtered_data.sort_values(
        by=selected_sort,
        ascending=ascending
    ).reset_index(drop=True)


    # -----------------------------------------------------
    # Display number of players
    # -----------------------------------------------------

    st.caption(
        f"Showing {len(filtered_data)} of {len(player_data)} players"
    )


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