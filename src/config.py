"""
Central configuration for the project.
Keeps constants and settings in one place instead of scattered across files.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # reads variables from .env into the environment

# Season we're analyzing — change this in one place, not everywhere it's used
CURRENT_SEASON = "2024-25"

# Where raw pulled data gets saved
RAW_DATA_DIR = "data/raw"