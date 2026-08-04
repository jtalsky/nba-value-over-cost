"""
Loads cleaned NBA stats and salary data from CSVs into the MySQL database.
"""

import unicodedata
import re
import pandas as pd

from src.db import get_connection
from src.config import RAW_DATA_DIR, CURRENT_SEASON

def normalize_name(name: str) -> str:
    """
    Normalize a player name for matching across data sources.
    (Same logic as our earlier overlap check.)
    """
    normalized = unicodedata.normalize("NFKD", name)
    no_accents = "".join(c for c in normalized if not unicodedata.combining(c))
    no_suffix = re.sub(r"\s+(Jr\.?|Sr\.?|II|III|IV)$", "", no_accents)
    return no_suffix.lower().strip()

def load_players(cursor, all_normalized_names: set) -> dict:
    """
    Insert every unique player into the players table (if not already there),
    and return a lookup of normalized_name -> player_id for use by other tables.

    Args:
        cursor: an open database cursor
        all_normalized_names: set of (full_name, name_normalized) tuples

    Returns:
        A dict mapping name_normalized -> player_id
    """
    for full_name, name_normalized in all_normalized_names:
        cursor.execute(
            """
            INSERT IGNORE INTO players (full_name, name_normalized)
            VALUES (%s, %s)
            """,
            (full_name, name_normalized)
        )

    # Build the lookup we'll need for the other tables
    cursor.execute("SELECT player_id, name_normalized FROM players")
    return {name: pid for pid, name in cursor.fetchall()}

def load_stats(cursor, stats_df: pd.DataFrame, name_to_id: dict):
    """Insert player_stats rows, linking each to its player_id."""
    for _, row in stats_df.iterrows():
        player_id = name_to_id.get(row["name_normalized"])
        if player_id is None:
            continue

        cursor.execute(
            """
            INSERT INTO player_stats
                (player_id, season, games_played, points, assists, rebounds,
                 offensive_rebounds, defensive_rebounds, steals, blocks, turnovers,
                 personal_fouls, field_goals_made, field_goals_attempted,
                 free_throws_made, free_throws_attempted, minutes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                player_id, CURRENT_SEASON,
                row["GP"], row["PTS"], row["AST"], row["REB"],
                row["OREB"], row["DREB"], row["STL"], row["BLK"], row["TOV"],
                row["PF"], row["FGM"], row["FGA"], row["FTM"], row["FTA"], row["MIN"]
            )
        )

def load_salaries(cursor, salaries_df: pd.DataFrame, name_to_id: dict):
    """Insert player_salaries rows, linking each to its player_id.
    If a player appears multiple times (e.g. traded mid-season), keep only one row."""
    deduped_df = salaries_df.drop_duplicates(subset="name_normalized", keep="first")

    for _, row in deduped_df.iterrows():
        player_id = name_to_id.get(row["name_normalized"])
        if player_id is None:
            continue

        cursor.execute(
            """
            INSERT INTO player_salaries (player_id, season, team, salary)
            VALUES (%s, %s, %s, %s)
            """,
            (player_id, CURRENT_SEASON, row["team"], row["salary"])
        )

if __name__ == "__main__":
    stats_df = pd.read_csv(f"{RAW_DATA_DIR}/player_stats_2024-25.csv")
    salaries_df = pd.read_csv(f"{RAW_DATA_DIR}/salaries_2024-25.csv")

    stats_df["name_normalized"] = stats_df["PLAYER_NAME"].apply(normalize_name)
    salaries_df["name_normalized"] = salaries_df["name"].apply(normalize_name)

    valid_names = set(stats_df["name_normalized"]) & set(salaries_df["name_normalized"])
    stats_df = stats_df[stats_df["name_normalized"].isin(valid_names)]
    salaries_df = salaries_df[salaries_df["name_normalized"].isin(valid_names)]

    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing data first so re-running this script is always safe
    # (child tables before parent, to respect foreign key constraints)
    cursor.execute("DELETE FROM player_stats")
    cursor.execute("DELETE FROM player_salaries")
    cursor.execute("DELETE FROM players")

    all_players = set(zip(stats_df["PLAYER_NAME"], stats_df["name_normalized"]))
    name_to_id = load_players(cursor, all_players)

    load_stats(cursor, stats_df, name_to_id)
    load_salaries(cursor, salaries_df, name_to_id)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Loaded {len(valid_names)} players into the database.")