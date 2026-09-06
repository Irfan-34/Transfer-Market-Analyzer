# Data Pipeline & Ingestion Architecture

The data pipeline manages data validation, cleaning, news ingestion, entity matching, and monitoring routines.

---

## 1. Validation & Cleaning Rules
- **Transfers**:
  - Flags duplicate transfers (`player_id`, `transfer_date`, `from_club_id`, `to_club_id`).
  - Corrects negative transfer fees to 0.0 EUR (logs warning).
  - Identifies transfers where selling club equals buying club.
- **Player Bios**:
  - Flag impossible ages (<14 or >50).
  - Standardizes height ranges (140cm to 220cm).
- **Rumours & News**:
  - Deduplicates articles by URL and SHA-256 content hash.
  - Normalizes player and club names.

---

## 2. Ingestion & Entity Extraction
- **RSS News Feeds**: Polls BBC Sport, Sky Sports, and The Guardian.
- **Entity Matching**: Regex patterns extract `Player Name`, `Buying Club`, and `Rumour Status`.
- **Classification**:
  - `CONFIRMED`: Official quotes, "signs for", "deal completed".
  - `RUMOUR`: Standard reporting links.
  - `SPECULATION`: Suggestive headlines.
  - `DENIED`: "rejects", "rules out".

---

## 3. Real-Time Monitor Job
- Scheduled background task in `src/data/monitor.py`.
- Configurable polling interval (`POLL_INTERVAL_SECONDS`).
- Automatically logs run metadata to `ingestion_runs` table.
