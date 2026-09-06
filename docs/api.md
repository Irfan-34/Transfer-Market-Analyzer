# API Specification & Endpoints

The API server runs on port 8000. Interactive Swagger documentation is accessible at `http://localhost:8000/docs`.

---

## 1. System Health
- **`GET /health`**: Returns system status, DuckDB database connectivity, and ML model status.

## 2. Players Analytics
- **`GET /players?search={name}&position={pos}&league_id={id}&limit=20&offset=0`**: Paginated player list.
- **`GET /players/{player_id}`**: Full profile with total goals, assists, appearances, and valuation.
- **`GET /players/{player_id}/market-value`**: Historical market value curve.
- **`GET /players/{player_id}/transfer-history`**: Player transfer events.

## 3. Club Analytics
- **`GET /clubs?search={name}&league_id={id}&limit=20&offset=0`**: Paginated club list.
- **`GET /clubs/{club_id}`**: Club profile, squad size, total spend, total income, and net balance.
- **`GET /clubs/{club_id}/transfer-activity`**: Recent incoming and outgoing transfers.

## 4. Market Summary
- **`GET /market/summary`**: Macro stats (total transfers, total spend, average fee, median fee).
- **`GET /market/spending?limit=15`**: Annual spending by season.
- **`GET /market/leagues?limit=10`**: Top spending leagues.
- **`GET /market/top-transfers?limit=20`**: Record high-fee transfers.

## 5. Rumours & Sources
- **`GET /rumours?status=RUMOUR&limit=20`**: Ingested rumours.
- **`GET /rumours/hot`**: High-confidence active rumours.
- **`GET /sources/reliability`**: Empirical media source accuracy rankings.

## 6. Predictions & ML Inference
- **`POST /predictions/transfer`**: Predicts transfer probability $P(\text{Transfer})$ and composite Intelligence Score.
- **`POST /predictions/fee`**: Predicts expected transfer fee and lower/upper bound confidence range.
- **`GET /predictions/top`**: Curated high-probability transfer predictions.
