-- Schema for the NBA Value-Over-Cost project.
-- Run this once to set up all tables.

CREATE TABLE players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    name_normalized VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE player_stats (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    season VARCHAR(10) NOT NULL,
    games_played INT,
    points FLOAT,
    assists FLOAT,
    rebounds FLOAT,
    steals FLOAT,
    blocks FLOAT,
    turnovers FLOAT,
    minutes FLOAT,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE TABLE player_salaries (
    salary_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    season VARCHAR(10) NOT NULL,
    team VARCHAR(100),
    salary BIGINT,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);