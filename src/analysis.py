"""
Computes each player's Game Score (John Hollinger's production metric)
and their value relative to salary.
"""

import pandas as pd
from src.db import get_connection

def compute_value_scores() -> pd.DataFrame:
    """
    Pull joined player/stats/salary data from the database, compute each
    player's season-total Game Score, then value relative to salary.

    Returns:
        A DataFrame sorted by value_score, highest (best value) first.
    """
    conn = get_connection()

    query = """
        SELECT
            p.full_name,
            sal.team,
            s.games_played,
            s.minutes,
            s.points,
            s.field_goals_made,
            s.field_goals_attempted,
            s.free_throws_made,
            s.free_throws_attempted,
            s.offensive_rebounds,
            s.defensive_rebounds,
            s.assists,
            s.steals,
            s.blocks,
            s.personal_fouls,
            s.turnovers,
            sal.salary
        FROM players p
        JOIN player_stats s ON p.player_id = s.player_id
        JOIN player_salaries sal ON p.player_id = sal.player_id
    """
    df = pd.read_sql(query, conn)
    conn.close()

    df = df[df["minutes"] > 0].copy()

    # John Hollinger's Game Score formula
    df["game_score"] = (
        df["points"]
        + 0.4 * df["field_goals_made"]
        - 0.7 * df["field_goals_attempted"]
        - 0.4 * (df["free_throws_attempted"] - df["free_throws_made"])
        + 0.7 * df["offensive_rebounds"]
        + 0.3 * df["defensive_rebounds"]
        + df["steals"]
        + 0.7 * df["assists"]
        + 0.7 * df["blocks"]
        - 0.4 * df["personal_fouls"]
        - df["turnovers"]
    )

    # value = production per million dollars of salary
    df["value_score"] = df["game_score"] / (df["salary"] / 1_000_000)

    return df.sort_values("value_score", ascending=False).reset_index(drop=True)

if __name__ == "__main__":
    results = compute_value_scores()

    print("Top 10 best VALUES (high Game Score, low cost):")
    print(results[["full_name", "team", "game_score", "value_score", "salary"]].head(10))

    print("\nBottom 10 worst values (low Game Score, high cost):")
    print(results[["full_name", "team", "game_score", "value_score", "salary"]].tail(10))

    output_path = "data/processed/value_scores.csv"
    results.to_csv(output_path, index=False)
    print(f"\nSaved full results to {output_path}")