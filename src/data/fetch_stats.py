"""
Handles pulling player stats from the NBA API.
"""

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats

from src.config import CURRENT_SEASON, RAW_DATA_DIR

def fetch_player_stats(season: str = CURRENT_SEASON) -> pd.DataFrame:
    """
    Pull season-long per-player stats from the NBA API.

    Args:
        season: NBA season string, e.g. "2024-25"

    Returns:
        A DataFrame with one row per player and their season stats.
    """
    stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season)
    df = stats.get_data_frames()[0]
    return df


if __name__ == "__main__":
    df = fetch_player_stats()
    print(f"Pulled {df.shape[0]} players, {df.shape[1]} columns")
    print(df.head())

    output_path = f"{RAW_DATA_DIR}/player_stats_{CURRENT_SEASON}.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")