"""
Computes each player's Game Score (John Hollinger's production metric),
normalized to a per-36-minutes basis, and their value relative to salary.
"""

import pandas as pd
from src.db import get_connection
from src.config import MIN_MINUTES_PLAYED


def compute_value_scores() -> pd.DataFrame:
    """
    Pull joined player/stats/salary data from the database, compute each
    player's per-36-minute Game Score, then value relative to salary.

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

    # Filter out players with no playing time, and apply a minimum minutes
    # threshold to avoid small-sample noise skewing per-36 rates
    df = df[df["minutes"] > 0].copy()
    df = df[df["minutes"] >= MIN_MINUTES_PLAYED].copy()

    # Convert season totals to per-36-minutes rates, so players are compared
    # on a level playing-time basis regardless of role (starter vs bench)
    # or games played
    per_36_cols = [
        "points", "field_goals_made", "field_goals_attempted",
        "free_throws_made", "free_throws_attempted",
        "offensive_rebounds", "defensive_rebounds",
        "assists", "steals", "blocks", "personal_fouls", "turnovers"
    ]
    for col in per_36_cols:
        df[f"{col}_p36"] = df[col] / df["minutes"] * 36

    # John Hollinger's Game Score formula, applied per-36-minutes
    df["game_score"] = (
        df["points_p36"]
        + 0.4 * df["field_goals_made_p36"]
        - 0.7 * df["field_goals_attempted_p36"]
        - 0.4 * (df["free_throws_attempted_p36"] - df["free_throws_made_p36"])
        + 0.7 * df["offensive_rebounds_p36"]
        + 0.3 * df["defensive_rebounds_p36"]
        + df["steals_p36"]
        + 0.7 * df["assists_p36"]
        + 0.7 * df["blocks_p36"]
        - 0.4 * df["personal_fouls_p36"]
        - df["turnovers_p36"]
    )

    # value = per-36-minute production per million dollars of salary
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