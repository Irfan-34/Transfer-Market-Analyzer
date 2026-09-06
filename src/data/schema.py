from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class RumourStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    RUMOUR = "RUMOUR"
    SPECULATION = "SPECULATION"
    DENIED = "DENIED"
    COMPLETED = "COMPLETED"


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    source_name = Column(String(100), nullable=False, index=True)
    content_hash = Column(String(64), unique=True, nullable=False, index=True)
    summary = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow)

    rumours = relationship("Rumour", back_populates="article")


class Rumour(Base):
    __tablename__ = "rumours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=True)
    player_id = Column(Integer, nullable=True, index=True)
    player_name = Column(String(200), nullable=False, index=True)
    from_club_id = Column(Integer, nullable=True)
    from_club_name = Column(String(200), nullable=True)
    to_club_id = Column(Integer, nullable=True)
    to_club_name = Column(String(200), nullable=False, index=True)
    transfer_direction = Column(String(50), default="INCOMING")
    status = Column(SQLEnum(RumourStatus), default=RumourStatus.RUMOUR, nullable=False)
    source_name = Column(String(100), nullable=False, index=True)
    source_url = Column(String(1000), nullable=True)
    published_at = Column(DateTime, nullable=True)
    confidence_score = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)

    article = relationship("NewsArticle", back_populates="rumours")


class SourceReliability(Base):
    __tablename__ = "source_reliability"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(100), unique=True, nullable=False, index=True)
    rumours_reported = Column(Integer, default=0)
    confirmed_outcomes = Column(Integer, default=0)
    false_rumours = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    reliability_score = Column(Float, default=0.5)  # Penalized prior for small samples
    last_updated = Column(DateTime, default=datetime.utcnow)


class TransferPrediction(Base):
    __tablename__ = "transfer_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, nullable=False, index=True)
    player_name = Column(String(200), nullable=False)
    current_club_name = Column(String(200), nullable=True)
    buying_club_id = Column(Integer, nullable=True)
    buying_club_name = Column(String(200), nullable=False, index=True)
    transfer_probability = Column(Float, nullable=False)  # 0.0 to 1.0
    confidence = Column(String(50), default="MEDIUM")      # LOW, MEDIUM, HIGH
    expected_fee_eur = Column(Float, nullable=True)
    fee_range_low_eur = Column(Float, nullable=True)
    fee_range_high_eur = Column(Float, nullable=True)
    intelligence_score = Column(Float, nullable=True)    # Composite score (0-100)
    model_version = Column(String(50), nullable=False)
    predicted_at = Column(DateTime, default=datetime.utcnow)


class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(100), nullable=False)
    metrics_json = Column(Text, nullable=False)
    features_json = Column(Text, nullable=False)
    trained_at = Column(DateTime, default=datetime.utcnow)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_type = Column(String(100), nullable=False)
    items_ingested = Column(Integer, default=0)
    status = Column(String(50), default="SUCCESS")
    log_message = Column(Text, nullable=True)
    ran_at = Column(DateTime, default=datetime.utcnow)
