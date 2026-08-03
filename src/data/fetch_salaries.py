"""
Handles scraping NBA player salary data from ESPN.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_page_html(url: str, max_retries: int = 3) -> str:
    """
    Fetch raw HTML from a URL, retrying on transient failures.

    Args:
        url: the page to fetch
        max_retries: how many times to retry before giving up

    Returns:
        Raw HTML as a string
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (educational project; contact: your_email@example.com)"
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            wait_time = attempt * 3  # 3s, then 6s, then 9s
            print(f"Attempt {attempt} failed ({e}). Retrying in {wait_time}s...")
            time.sleep(wait_time)

    raise Exception(f"Failed to fetch {url} after {max_retries} attempts")

def parse_salary_table(html: str) -> list[dict]:
    """
    Extract player salary rows from a single page of HTML.

    Args:
        html: raw HTML from one ESPN salary page

    Returns:
        A list of dicts, one per player, e.g.
        [{"name": "Stephen Curry", "position": "G", "team": "Golden State Warriors", "salary": 51915615}, ...]
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find every row that's actually a data row (skip repeated header rows)
    rows = soup.find_all("tr", class_=["oddrow", "evenrow"])

    players = []
    for row in rows:
        cells = row.find_all("td")

        # Defensive check: skip anything that doesn't have exactly 4 cells
        if len(cells) != 4:
            continue

        # Cell 1: name + position, e.g. "Stephen Curry, G"
        name_cell_text = cells[1].get_text(strip=True)
        name, _, position = name_cell_text.partition(",")

        # Cell 2: team name
        team = cells[2].get_text(strip=True)

        # Cell 3: salary, e.g. "$51,915,615" -> need to convert to a real number
        salary_text = cells[3].get_text(strip=True)
        salary = int(salary_text.replace("$", "").replace(",", ""))

        players.append({
            "name": name.strip(),
            "position": position.strip(),
            "team": team,
            "salary": salary
        })

    return players

def fetch_all_salaries(season_year: str = "2024", num_pages: int = 12) -> pd.DataFrame:
    """
    Scrape all pages of ESPN's NBA salary rankings for a given season.

    Args:
        season_year: the year ESPN uses in the URL, e.g. "2024"
        num_pages: how many pages to scrape (ESPN shows this on the page itself)

    Returns:
        A DataFrame with one row per player across all pages
    """
    all_players = []

    for page_num in range(1, num_pages + 1):
        url = f"https://www.espn.com/nba/salaries/_/year/{season_year}/page/{page_num}"
        print(f"Fetching page {page_num}/{num_pages}...")

        html = get_page_html(url)
        players = parse_salary_table(html)
        all_players.extend(players)

        time.sleep(1)  # be polite — wait 1 second between requests

    return pd.DataFrame(all_players)

if __name__ == "__main__":
    df = fetch_all_salaries()
    print(f"\nTotal players scraped: {df.shape[0]}")
    print(df.head())

    output_path = "data/raw/salaries_2024-25.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")