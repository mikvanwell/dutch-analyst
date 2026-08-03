import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Player Analysis",
    page_icon="⚽",
    layout="wide"
)

st.title("Player Analysis")
st.markdown(
    "Expected points (xPTS) data for every Eredivisie player, based on 25/26 underlying performance."
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('xpts_srteamlit.csv')
    return df

def prepare_data(df):
    df = df.copy()

    # Rename the underlying metric columns to their display names
    df = df.rename(columns={
        'npxG_per90_adjusted': 'npxG',
        'xA_per90_adjusted': 'xA',
        'Saves_per90_calc': 'Saves',
        'Yellow_cards_per90_raw': 'Yellow_cards',
    })

    # xPTS per euro of price
    df['xPTS_per_€'] = df['xPTS_per90'] / df['€']

    # Scale Start% to a 0-100 range since NumberColumn's format string doesn't auto-multiply
    df['Start%'] = df['Start%'] * 100

    # Column order: everything up to predicted_to_start unchanged, then on_pens, then the
    # requested metric order, then xPTS_per_€ at the end.
    df = df[[
        'player_id', 'name', 'team', 'position', '€', 'Start%', 'Mins/Start', 'Minutes played',
        'predicted_to_start', 'on_pens', 'xPTS_per90', 'npxG', 'xA', 'Saves', 'Yellow_cards', 'xPTS_per_€'
    ]]

    df = df.sort_values('€', ascending=False).reset_index(drop=True)
    return df

# Convert a 0-1 score to a heatmap color (dark green = best, dark purple/pink = worst)
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
        return 'background-color: #ff1751; color: white'  # Light pink
    else:
        return 'background-color: #80082e; color: white'  # Dark purple/pink

# Score a value by its relative distance from the column's mean (in standard deviations),
# same approach as the Team Data page: 0.5 (grey) at the mean, +/-2 std devs reach full color.
def get_heatmap_score(value, mean_val, std_val, higher_is_better):
    if pd.isna(value) or std_val == 0 or pd.isna(std_val):
        return np.nan
    z = (value - mean_val) / std_val
    z = max(-2, min(2, z))
    return (0.5 - z / 4) if higher_is_better else (0.5 + z / 4)

def style_dataframe(df):
    xpts_mean, xpts_std = df['xPTS_per90'].mean(), df['xPTS_per90'].std()

    def apply_color(val, col_name):
        if col_name == 'xPTS_per90':
            score = get_heatmap_score(val, xpts_mean, xpts_std, higher_is_better=True)
            return get_color_from_score(score)
        return ''

    styled = df.style.apply(
        lambda x: [apply_color(val, x.name) for val in x], axis=0
    )
    return styled

def main():
    try:
        xpts_data = load_data()
    except FileNotFoundError:
        st.error("Please make sure 'xpts_srteamlit.csv' is in the same directory.")
        return

    player_data = prepare_data(xpts_data)
    styled_data = style_dataframe(player_data)

    st.dataframe(
        styled_data,
        column_config={
            "player_id": st.column_config.TextColumn("Player ID"),
            "name": st.column_config.TextColumn("Name"),
            "team": st.column_config.TextColumn("Team"),
            "position": st.column_config.TextColumn("Position"),
            "€": st.column_config.NumberColumn("€", format="€%.1f"),
            "Start%": st.column_config.NumberColumn("Start %", format="%.0f %%"),
            "Mins/Start": st.column_config.NumberColumn("Mins/Start", format="%.0f"),
            "Minutes played": st.column_config.NumberColumn("Minutes played", format="%d"),
            "predicted_to_start": st.column_config.CheckboxColumn("Predicted to start"),
            "on_pens": st.column_config.CheckboxColumn("On pens"),
            "xPTS_per90": st.column_config.NumberColumn("xPTS per 90", format="%.2f"),
            "npxG": st.column_config.NumberColumn("npxG p90", format="%.2f"),
            "xA": st.column_config.NumberColumn("xA p90", format="%.2f"),
            "Saves": st.column_config.NumberColumn("Saves p90", format="%.2f"),
            "Yellow_cards": st.column_config.NumberColumn("Yellow cards p90", format="%.2f"),
            "xPTS_per_€": st.column_config.NumberColumn("xPTS per €", format="%.3f"),
        },
        hide_index=True,
        width='stretch',
        height=600
    )

if __name__ == "__main__":
    main()