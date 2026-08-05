import streamlit as st
import pandas as pd
import numpy as np

from utils import load_css


st.set_page_config(
    page_title="FDR Schedule",
    page_icon="🔮",
    layout="wide"
)

# Load global styling
load_css()


st.title("FDR Schedule")

st.markdown(
    "The Fixture Difficulty Rating schedule below can help you plan your transfers "
    "and team selection strategy. "
    "FDR is determined based on recent relative offensive and defensive performance. "
    "More information about the calculation can be found "
    "[here](https://open.substack.com/pub/mikvanwell/p/calculating-fixture-difficulty?"
    "r=4l6fci&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)."
)

st.markdown(
    "You can choose which position group you want to optimise the schedule for. "
    "If you want to see an 'overall' schedule, select the DEF schedule, "
    "as it covers both offensive and defensive difficulty."
)


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

@st.cache_data
def load_data():

    fdr_schedule = pd.read_csv("fdr_schedule.csv")
    fdr_small = pd.read_csv("fdr_small.csv")

    return fdr_schedule, fdr_small


# ---------------------------------------------------------
# Precompute fixture -> score dictionaries
# ---------------------------------------------------------

@st.cache_data
def build_score_maps(fdr_small):

    return {
        "KEE": (
            fdr_small
            .set_index("fixture")["fdr_kee"]
            .to_dict()
        ),

        "DEF": (
            fdr_small
            .set_index("fixture")["fdr_def"]
            .to_dict()
        ),

        "MID/ATT": (
            fdr_small
            .set_index("fixture")["fdr_mid_att"]
            .to_dict()
        ),
    }


# ---------------------------------------------------------
# FDR colour scheme
# ---------------------------------------------------------
# NOTE: the FDR bands use fixed accent colours (green -> grey -> red)
# regardless of light/dark theme, since these are meaningful data colours,
# not chrome. Each band explicitly sets a text colour with guaranteed
# contrast against its own background, so it stays legible in either theme.

def get_color_from_score(score):

    if pd.isna(score):
        # Let the alternating row colour show through instead of forcing
        # a hardcoded light background.
        return "background-color: transparent;"

    elif score < 0.15:
        return (
            "background-color: #006400;"
            "color: #ffffff;"
        )

    elif score < 0.4:
        return (
            "background-color: #01fc79;"
            "color: #063d1f;"
        )

    elif score < 0.6:
        return (
            "background-color: #e7e7e7;"
            "color: #1a1a1a;"
        )

    elif score < 0.85:
        return (
            "background-color: #ff1751;"
            "color: #ffffff;"
        )

    else:
        return (
            "background-color: #80082e;"
            "color: #ffffff;"
        )


# ---------------------------------------------------------
# Style dataframe
# ---------------------------------------------------------

def style_dataframe(df, score_map):

    # Columns containing fixtures
    fixture_columns = [
        column
        for column in df.columns
        if column != "Team"
    ]


    # -----------------------------------------------------
    # Alternating row styling
    # -----------------------------------------------------
    # Uses Streamlit's theme CSS variables so the stripe colours (and the
    # text colour) automatically match whichever theme (light/dark) the
    # user has selected, instead of being hardcoded to white/black.

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


    # -----------------------------------------------------
    # Apply FDR colours to fixture cells
    # -----------------------------------------------------

    def apply_fdr_color(value, column):

        if column == "Team":
            return ""

        score = (
            score_map.get(value, np.nan)
            if pd.notna(value)
            else np.nan
        )

        return get_color_from_score(score)


    styled = styled.apply(
        lambda column: [
            apply_fdr_color(
                value,
                column.name
            )
            for value in column
        ],
        axis=0
    )


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

.fdr-table {
    width: 100%;
    overflow-x: auto;
}

.fdr-table table {
    /* Separate borders prevent sticky-cell rendering issues */
    border-collapse: separate;
    border-spacing: 0;
    width: 100%;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
}


/* ---------------------------------------------------------
   Header
   --------------------------------------------------------- */

.fdr-table th {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    font-weight: 700;
    border-top: 1px solid rgba(128, 128, 128, 0.35);
    border-bottom: 1px solid rgba(128, 128, 128, 0.35);
    border-right: 1px solid rgba(128, 128, 128, 0.35);
    padding: 9px 10px;
    text-align: center;
    white-space: nowrap;
}

.fdr-table th:first-child {
    border-left: 1px solid rgba(128, 128, 128, 0.35);
}


/* ---------------------------------------------------------
   Cells
   --------------------------------------------------------- */

.fdr-table td {
    border-bottom: 1px solid rgba(128, 128, 128, 0.25);
    border-right: 1px solid rgba(128, 128, 128, 0.25);
    padding: 8px 10px;
    text-align: center;
    white-space: nowrap;
}

.fdr-table td:first-child {
    border-left: 1px solid rgba(128, 128, 128, 0.25);
}


/* ---------------------------------------------------------
   Team names
   --------------------------------------------------------- */

.fdr-table td:first-child {
    text-align: left;
}


/* ---------------------------------------------------------
   STICKY TEAM COLUMN
   --------------------------------------------------------- */

/*
   The Team column gets an explicit opaque background and a
   high z-index so that fixture cells can never show through
   while horizontally scrolling.
*/

.fdr-table th:first-child,
.fdr-table td:first-child {
    position: sticky;
    left: 0;

    /* Keep Team column above all fixture cells */
    z-index: 10;

    /* Important: opaque background */
    background-color: var(--background-color);

    min-width: 120px;

    /* Visual separation */
    box-shadow:
        3px 0 6px -3px rgba(0, 0, 0, 0.45);

    /* Prevent background bleed */
    isolation: isolate;
}


/* ---------------------------------------------------------
   Alternating colours for sticky Team cells
   --------------------------------------------------------- */

.fdr-table tbody tr:nth-child(odd) td:first-child {
    background-color: var(--background-color);
}

.fdr-table tbody tr:nth-child(even) td:first-child {
    background-color: var(--secondary-background-color);
}


/* ---------------------------------------------------------
   Sticky header
   --------------------------------------------------------- */

.fdr-table thead th:first-child {
    background-color: var(--secondary-background-color);
    z-index: 20;
}


/* ---------------------------------------------------------
   Extra opaque layer on right edge of sticky column
   --------------------------------------------------------- */

/*
   This provides a small solid buffer between the sticky Team
   column and the horizontally scrolling fixture columns.
   It prevents any underlying cells from visually bleeding
   through during horizontal scrolling.
*/

.fdr-table th:first-child::after,
.fdr-table td:first-child::after {
    content: "";
    position: absolute;

    top: 0;
    right: -4px;

    width: 5px;
    height: 100%;

    background-color: inherit;

    pointer-events: none;
}


/* ---------------------------------------------------------
   Keep non-sticky cells underneath
   --------------------------------------------------------- */

.fdr-table th:not(:first-child),
.fdr-table td:not(:first-child) {
    position: relative;
    z-index: 1;
}


/* ---------------------------------------------------------
   Separate Team column from fixture data
   --------------------------------------------------------- */

.fdr-table th:first-child,
.fdr-table td:first-child {
    border-right: 2px solid rgba(128, 128, 128, 0.45);
}


/* ---------------------------------------------------------
   Fixture cells
   --------------------------------------------------------- */

.fdr-table td:not(:first-child) {
    min-width: 42px;
}

</style>
"""


# ---------------------------------------------------------
# FDR Legend
# ---------------------------------------------------------
# The legend swatches also use fixed accent colours (matching the table),
# with a text colour chosen per swatch for guaranteed contrast in both
# light and dark themes.

def display_legend():

    st.markdown("### FDR Key:")

    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:

        st.markdown(
            """
            <div style="
                background-color: #006400;
                padding: 10px;
                text-align: center;
                color: #ffffff;
                border-radius: 5px;
                font-family: 'DM Sans', sans-serif;
            ">
                1 - Easiest
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
                color: #063d1f;
                border-radius: 5px;
                font-family: 'DM Sans', sans-serif;
            ">
                2
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
                color: #1a1a1a;
                border-radius: 5px;
                font-family: 'DM Sans', sans-serif;
            ">
                3
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
                color: #ffffff;
                border-radius: 5px;
                font-family: 'DM Sans', sans-serif;
            ">
                4
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
                color: #ffffff;
                border-radius: 5px;
                font-family: 'DM Sans', sans-serif;
            ">
                5 - Hardest
            </div>
            """,
            unsafe_allow_html=True
        )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    # Load data
    try:

        fdr_schedule, fdr_small = load_data()

    except FileNotFoundError:

        st.error(
            "Please make sure 'fdr_schedule.csv' and "
            "'fdr_small.csv' are in the same directory."
        )

        return


    # -----------------------------------------------------
    # Prepare schedule
    # -----------------------------------------------------

    fdr_schedule = (
        fdr_schedule
        .sort_values("team_id")
        .reset_index(drop=True)
        .rename(columns={"team_id": "Team"})
    )


    # -----------------------------------------------------
    # Position group selection
    # -----------------------------------------------------

    position_group = st.radio(
        "Select Position Group:",
        options=["KEE", "DEF", "MID/ATT"],
        index=1,  # DEF selected by default
        horizontal=True
    )


    # -----------------------------------------------------
    # Build lookup dictionaries
    # -----------------------------------------------------

    score_maps = build_score_maps(fdr_small)


    # -----------------------------------------------------
    # Style dataframe
    # -----------------------------------------------------

    styled_df = style_dataframe(
        fdr_schedule,
        score_maps[position_group]
    )


    # -----------------------------------------------------
    # Display table
    # -----------------------------------------------------

    st.markdown(
        TABLE_CSS,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="fdr-table">'
        + styled_df.to_html()
        + '</div>',
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # Legend
    # -----------------------------------------------------

    display_legend()


if __name__ == "__main__":
    main()