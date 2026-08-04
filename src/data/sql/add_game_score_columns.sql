-- Migration: add columns needed for Game Score formula
DROP TABLE IF EXISTS player_stats;

CREATE TABLE player_stats (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    season VARCHAR(10) NOT NULL,
    games_played INT,
    points FLOAT,
    assists FLOAT,
    rebounds FLOAT,
    offensive_rebounds FLOAT,
    defensive_rebounds FLOAT,
    steals FLOAT,
    blocks FLOAT,
    turnovers FLOAT,
    personal_fouls FLOAT,
    field_goals_made FLOAT,
    field_goals_attempted FLOAT,
    free_throws_made FLOAT,
    free_throws_attempted FLOAT,
    minutes FLOAT,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);