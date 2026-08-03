"""
One-off check: how well do player names match between our two data sources?
"""

import unicodedata
import re
import pandas as pd


def normalize_name(name: str) -> str:
    """
    Normalize a player name for matching across data sources:
    strips accents, removes suffixes, lowercases, trims whitespace.

    Args:
        name: raw player name, e.g. "Nikola Jokić" or "Brandon Boston Jr."

    Returns:
        A normalized version for comparison, e.g. "nikola jokic" or "brandon boston"
    """
    # Strip accents: decompose characters into base letter + accent mark,
    # then discard anything that's just an accent mark
    normalized = unicodedata.normalize("NFKD", name)
    no_accents = "".join(c for c in normalized if not unicodedata.combining(c))

    # Remove common suffixes
    no_suffix = re.sub(r"\s+(Jr\.?|Sr\.?|II|III|IV)$", "", no_accents)

    return no_suffix.lower().strip()


stats_df = pd.read_csv("data/raw/player_stats_2024-25.csv")
salaries_df = pd.read_csv("data/raw/salaries_2024-25.csv")

# Raw exact-match check (what we did originally)
stats_names_raw = set(stats_df["PLAYER_NAME"])
salary_names_raw = set(salaries_df["name"])
matched_raw = stats_names_raw & salary_names_raw

# Normalized match check (accounting for accents/suffixes)
stats_df["name_normalized"] = stats_df["PLAYER_NAME"].apply(normalize_name)
salaries_df["name_normalized"] = salaries_df["name"].apply(normalize_name)

stats_names = set(stats_df["name_normalized"])
salary_names = set(salaries_df["name_normalized"])

matched = stats_names & salary_names
only_in_stats = stats_names - salary_names
only_in_salaries = salary_names - stats_names

print(f"Players in stats data: {len(stats_names_raw)}")
print(f"Players in salary data: {len(salary_names_raw)}")
print(f"Exact matches before normalization: {len(matched_raw)}")
print(f"Matches after normalization: {len(matched)}")

print(f"\nStill unmatched in stats ({len(only_in_stats)}):")
for name in sorted(only_in_stats):
    print(f"  {name}")

print(f"\nStill unmatched in salaries ({len(only_in_salaries)}):")
for name in sorted(only_in_salaries):
    print(f"  {name}")