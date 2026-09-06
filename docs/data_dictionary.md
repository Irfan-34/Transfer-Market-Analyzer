# Data Dictionary: Transfermarkt DuckDB Database

This document details the schema, column definitions, data types, and primary/foreign key relationships of the historical football transfer dataset stored in `data/raw/transfermarkt.duckdb`.

---

## Tables Overview

1. `transfers` (175,165 rows) — Historical transfer events between clubs.
2. `players` (50,149 rows) — Master player profiles and bios.
3. `player_valuations` (656,301 rows) — Historical market value snapshots.
4. `appearances` (1,894,350 rows) — Match-level player participation statistics.
5. `clubs` (796 rows) — Master club profiles.
6. `competitions` (65 rows) — Domestic leagues and international tournaments.
7. `games` (88,958 rows) — Match schedules, scores, and metadata.
8. `club_games` (177,916 rows) — Team performance records per match.
9. `game_events` (1,274,469 rows) — Minute-by-minute match events (goals, cards, substitutions).
10. `game_lineups` (3,179,016 rows) — Match starting lineups and substitutes.
11. `countries` (124 rows) — Country metadata.
12. `national_teams` (124 rows) — National team statistics and rankings.
13. `version` (1 row) — Data snapshot commit hash.

---

## Detailed Schema Specifications

### 1. `transfers`
- **`player_id`** (`INTEGER`): Reference to `players.player_id`.
- **`player_name`** (`VARCHAR`): Full name of the transferred player.
- **`transfer_date`** (`DATE`): Date when the transfer was completed.
- **`transfer_season`** (`VARCHAR`): Transfer season label (e.g., `'23/24'`).
- **`from_club_id`** (`INTEGER`): Selling club ID (references `clubs.club_id`).
- **`to_club_id`** (`INTEGER`): Buying club ID (references `clubs.club_id`).
- **`from_club_name`** (`VARCHAR`): Name of the selling club.
- **`to_club_name`** (`VARCHAR`): Name of the buying club.
- **`transfer_fee`** (`DECIMAL(18,3)`): Recorded transfer fee in EUR (0.0 for free transfers / missing).
- **`market_value_in_eur`** (`DECIMAL(18,3)`): Player market value at the time of transfer in EUR.

### 2. `players`
- **`player_id`** (`INTEGER`, Primary Key): Unique player identifier.
- **`first_name`** (`VARCHAR`): Player's first name.
- **`last_name`** (`VARCHAR`): Player's last name.
- **`name`** (`VARCHAR`): Full display name.
- **`last_season`** (`VARCHAR`): Last recorded active season.
- **`current_club_id`** (`VARCHAR`): Current club identifier.
- **`player_code`** (`VARCHAR`): URL slug code.
- **`country_of_birth`** (`VARCHAR`): Birth country.
- **`city_of_birth`** (`VARCHAR`): Birth city.
- **`country_of_citizenship`** (`VARCHAR`): Primary nationality.
- **`date_of_birth`** (`TIMESTAMP`): Birth date.
- **`position`** (`VARCHAR`): Main position group (`Attack`, `Midfield`, `Defender`, `Goalkeeper`).
- **`sub_position`** (`VARCHAR`): Specific role (`Centre-Forward`, `Central Midfield`, `Right-Back`, etc.).
- **`foot`** (`VARCHAR`): Dominant foot (`right`, `left`, `both`).
- **`height_in_cm`** (`INTEGER`): Height in centimeters.
- **`contract_expiration_date`** (`TIMESTAMP`): Contract end date.
- **`agent_name`** (`VARCHAR`): Representative agency or agent.
- **`image_url`** (`VARCHAR`): URL for player avatar photo.
- **`international_caps`** (`INTEGER`): Senior national team appearances.
- **`international_goals`** (`INTEGER`): Senior national team goals.
- **`current_national_team_id`** (`VARCHAR`): Current national team ID.
- **`url`** (`VARCHAR`): Transfermarkt profile URL.
- **`current_club_domestic_competition_id`** (`VARCHAR`): Domestic league ID.
- **`current_club_name`** (`VARCHAR`): Current club display name.
- **`market_value_in_eur`** (`INTEGER`): Latest estimated market value in EUR.
- **`highest_market_value_in_eur`** (`INTEGER`): Career peak market value in EUR.

### 3. `player_valuations`
- **`player_id`** (`INTEGER`): Foreign key to `players.player_id`.
- **`date`** (`DATE`): Valuation snapshot date.
- **`market_value_in_eur`** (`INTEGER`): Estimated valuation in EUR.
- **`current_club_name`** (`VARCHAR`): Club name at time of valuation.
- **`current_club_id`** (`INTEGER`): Club ID at time of valuation.
- **`player_club_domestic_competition_id`** (`VARCHAR`): Competition ID.

### 4. `appearances`
- **`appearance_id`** (`VARCHAR`, Primary Key): Unique match-player ID.
- **`game_id`** (`INTEGER`): Match ID.
- **`player_id`** (`INTEGER`): Player ID.
- **`player_club_id`** (`INTEGER`): Club player represented.
- **`player_current_club_id`** (`VARCHAR`): Current club ID.
- **`date`** (`DATE`): Match date.
- **`player_name`** (`VARCHAR`): Player name.
- **`competition_id`** (`VARCHAR`): Tournament/League ID.
- **`yellow_cards`** (`INTEGER`): Yellow cards issued.
- **`red_cards`** (`INTEGER`): Red cards issued.
- **`goals`** (`INTEGER`): Goals scored.
- **`assists`** (`INTEGER`): Assists provided.
- **`minutes_played`** (`INTEGER`): Minutes played in match.

### 5. `clubs`
- **`club_id`** (`VARCHAR`, Primary Key): Unique club identifier.
- **`club_code`** (`VARCHAR`): Short URL slug code.
- **`name`** (`VARCHAR`): Full club name.
- **`domestic_competition_id`** (`VARCHAR`): Primary domestic league ID.
- **`total_market_value`** (`FLOAT`): Total squad market value in EUR.
- **`squad_size`** (`INTEGER`): Total roster count.
- **`average_age`** (`FLOAT`): Average squad age.
- **`foreigners_number`** (`INTEGER`): Non-domestic player count.
- **`foreigners_percentage`** (`FLOAT`): Non-domestic player percentage.
- **`national_team_players`** (`INTEGER`): International caps count in squad.
- **`stadium_name`** (`VARCHAR`): Home stadium name.
- **`stadium_seats`** (`INTEGER`): Stadium capacity.
- **`net_transfer_record`** (`VARCHAR`): Overall net balance text.
- **`coach_name`** (`VARCHAR`): Current head manager.
- **`last_season`** (`VARCHAR`): Season year.
- **`url`** (`VARCHAR`): Transfermarkt club URL.

### 6. `competitions`
- **`competition_id`** (`VARCHAR`, Primary Key): Competition code (e.g., `'GB1'`, `'L1'`).
- **`competition_code`** (`VARCHAR`): League slug.
- **`name`** (`VARCHAR`): Display name (e.g., `'premier-league'`).
- **`sub_type`** (`VARCHAR`): Subcategory (`first_tier`, `domestic_cup`, etc.).
- **`type`** (`VARCHAR`): Category (`domestic_league`, `international_cup`).
- **`country_id`** (`INTEGER`): Home country ID.
- **`country_name`** (`VARCHAR`): Country name.
- **`domestic_league_code`** (`VARCHAR`): Parent league code.
- **`confederation`** (`VARCHAR`): Governing body (e.g., `'europa'`).
- **`total_clubs`** (`INTEGER`): Total participating clubs.

---

## Application Extension Schema (PostgreSQL / SQLite / Application Analytical Layer)

To fulfill real-time monitoring, news, rumours, ML runs, and probability scoring, the following tables are introduced:

1. **`rumours`**: Extracted transfer links (`id`, `player_id`, `player_name`, `from_club_id`, `to_club_id`, `transfer_direction`, `status`, `source_id`, `url`, `published_at`, `confidence_score`, `created_at`).
2. **`news_articles`**: Scraped/ingested RSS news feeds (`id`, `title`, `url`, `source_name`, `content_hash`, `summary`, `published_at`, `ingested_at`).
3. **`source_reliability`**: Historical track record of media outlets/journalists (`source_name`, `rumours_reported`, `confirmed_outcomes`, `false_rumours`, `accuracy_rate`, `reliability_score`).
4. **`transfer_predictions`**: ML model generated transfer probabilities (`id`, `player_id`, `buying_club_id`, `transfer_probability`, `confidence`, `expected_fee`, `model_version`, `predicted_at`).
5. **`model_runs`**: Training and evaluation audit trail (`id`, `model_name`, `model_type`, `metrics_json`, `feature_list`, `trained_at`).
6. **`ingestion_runs`**: Data sync log (`id`, `source_type`, `items_ingested`, `status`, `log_message`, `ran_at`).
