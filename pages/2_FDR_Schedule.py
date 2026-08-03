import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="FDR Schedule",
    page_icon="🔮",
    layout="wide"
)

st.title("FDR Schedule")
st.markdown(
    "The Fixture Difficulty Rating schedule below can help you plan your transfers and team selection strategy. "
    "FDR is determined based on recent relative offensive and defensive performance. "
    "More information about the calculation can be found [here](https://open.substack.com/pub/mikvanwell/p/calculating-fixture-difficulty?r=4l6fci&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)."
)
st.markdown(
    "You can choose which position group you want to optimise the schedule for. "
    "If you want to see an 'overall' schedule, select the DEF schedule, as it covers both offensive and defensive difficulty."
)

# Load data
@st.cache_data
def load_data():
    fdr_schedule = pd.read_csv('fdr_schedule.csv')
    fdr_small = pd.read_csv('fdr_small.csv')
    return fdr_schedule, fdr_small

# Precompute fixture -> score dicts once, instead of filtering fdr_small per cell
@st.cache_data
def build_score_maps(fdr_small):
    return {
        'KEE': fdr_small.set_index('fixture')['fdr_kee'].to_dict(),
        'DEF': fdr_small.set_index('fixture')['fdr_def'].to_dict(),
        'MID/ATT': fdr_small.set_index('fixture')['fdr_mid_att'].to_dict(),
    }

# Convert numeric score to color
def get_color_from_score(score):
    if pd.isna(score):
        return 'background-color: white'
    elif score < 0.15:
        return 'background-color: #006400; color: white'  # Dark green
    elif score < 0.4:
        return 'background-color: #01fc79'  # Light green
    elif score < 0.6:
        return 'background-color: #e7e7e7'  # Grey
    elif score < 0.85:
        return 'background-color: #ff1751; color: white'  # Light red
    else:
        return 'background-color: #80082e; color: white'  # Dark red

# Apply colors to the dataframe using a precomputed dict (O(1) lookups, no per-cell filtering)
def style_dataframe(df, score_map):
    def apply_color(val, col_name):
        if col_name == 'Team':
            return 'background-color: white'
        score = score_map.get(val, np.nan) if pd.notna(val) else np.nan
        return get_color_from_score(score)

    styled = df.style.apply(
        lambda x: [apply_color(val, x.name) for val in x], axis=0
    )
    return styled

def main():
    # Load data
    try:
        fdr_schedule, fdr_small = load_data()
    except FileNotFoundError:
        st.error("Please make sure 'fdr_schedule.csv' and 'fdr_small.csv' are in the same directory.")
        return

    # Sort by team
    fdr_schedule = fdr_schedule.sort_values('team_id').reset_index(drop=True)
    fdr_schedule = fdr_schedule.rename(columns={'team_id': 'Team'})

    # Position group selection
    position_group = st.radio(
        "Select Position Group:",
        options=['KEE', 'DEF', 'MID/ATT'],
        index=0,
        horizontal=True
    )

    # Build lookup dicts once (cached across reruns since fdr_small doesn't change)
    score_maps = build_score_maps(fdr_small)

    # Style dataframe using the fast dict lookup for the selected position group
    styled_df = style_dataframe(fdr_schedule, score_maps[position_group])

    # Display the table with sticky Team column
    st.markdown("""
    <style>
    .stDataFrame {
        width: auto;
    }

    /* Make the first visible column sticky (Team) */
    .stDataFrame table thead tr th:nth-child(1),
    .stDataFrame table tbody tr td:nth-child(1) {
        position: sticky;
        left: 0;
        background-color: white;
        z-index: 10;
        border-right: 2px solid #ddd;
    }

    /* Table styling */
    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0;
    }
    .stDataFrame table th,
    .stDataFrame table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }
    .stDataFrame table th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # Calculate height so all rows fit without vertical scrolling
    row_height = 35
    header_height = 38
    table_height = header_height + (len(fdr_schedule) * row_height)

    st.dataframe(
        styled_df,
        width='content',
        height=table_height,
        hide_index=True
    )

    # FDR legend
    st.markdown("### FDR Key:")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown('<div style="background-color: #006400; padding: 10px; text-align: center; color: white; border-radius: 5px;">1 - Easiest</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="background-color: #01fc79; padding: 10px; text-align: center; border-radius: 5px;">2</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div style="background-color: #e7e7e7; padding: 10px; text-align: center; border-radius: 5px;">3</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div style="background-color: #ff1751; padding: 10px; text-align: center; color: white; border-radius: 5px;">4</div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div style="background-color: #80082e; padding: 10px; text-align: center; color: white; border-radius: 5px;">5 - Hardest</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
