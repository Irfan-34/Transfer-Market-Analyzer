# Deployment Guide

This guide covers local environment setup, testing, and containerized Docker deployment.

---

## 1. Local Development Setup

### Backend (Python + FastAPI)
```bash
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI Server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Dashboard (React + Vite)
```bash
cd dashboard
npm install
npm run dev
```

---

## 2. Docker Deployment

### Run using Docker Compose
```bash
docker-compose up --build
```

Services exposed:
- **Backend API**: `http://localhost:8000`
- **Dashboard UI**: `http://localhost:5173`

---

## 3. Running Unit & Integration Tests
```bash
pytest tests/
```
