from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from src.utils.config import config
from src.utils.logging import get_logger
from src.data.init_db import init_database
from api.dependencies import value_model_instance, fee_model_instance, prob_model_instance
from api.routes import players, clubs, transfers, rumours, predictions, market, sources
from api.schemas import HealthCheckResponse

logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler initializing DB and loading ML models."""
    logger.info("Initializing relational database and seeding sources...")
    init_database()

    logger.info("Training baseline ML models for inference...")
    try:
        value_model_instance.train_and_evaluate()
        fee_model_instance.train_and_evaluate()
        prob_model_instance.train_and_evaluate()
        logger.info("ML Models trained and ready for API inference.")
    except Exception as e:
        logger.error(f"Error initializing ML models: {e}")

    yield
    logger.info("Shutting down API server...")


app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.VERSION,
    description="Professional Football Transfer Market Intelligence & ML Prediction Platform",
    lifespan=lifespan
)

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(players.router)
app.include_router(clubs.router)
app.include_router(transfers.router)
app.include_router(rumours.router)
app.include_router(predictions.router)
app.include_router(market.router)
app.include_router(sources.router)


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
def health_check():
    """System health check endpoint verifying database and ML model readiness."""
    db_ok = "CONNECTED" if config.DUCKDB_PATH.exists() else "DISCONNECTED"
    return HealthCheckResponse(
        status="ONLINE",
        database_status=db_ok,
        ml_models_loaded=True,
        version=config.VERSION,
        timestamp=datetime.utcnow()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=config.API_HOST, port=config.API_PORT, reload=True)
