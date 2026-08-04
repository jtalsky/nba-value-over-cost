"""
Shared database connection logic.
"""

import mysql.connector
from src.config import DB_CONFIG

def get_connection():
    """
    Open a new connection to the MySQL database using settings from config.

    Returns:
        A live mysql.connector connection object
    """
    return mysql.connector.connect(**DB_CONFIG)