import hashlib
import re
import feedparser
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.data.db import SessionLocal, query_duckdb
from src.data.schema import NewsArticle, Rumour, RumourStatus
from src.data.validators import validate_rumours
from src.utils.logging import get_logger

logger = get_logger("data.news_ingestion")

# Public RSS feeds for transfer news
RSS_FEEDS = [
    {"source": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/football/rss.xml"},
    {"source": "Sky Sports", "url": "https://www.skysports.com/rss/12040"},  # Football transfer news
    {"source": "The Guardian", "url": "https://www.theguardian.com/football/transfers/rss"}
]


def generate_content_hash(text: str) -> str:
    """Computes SHA-256 hash for deduplication."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_entities_regex(text: str) -> Dict[str, Any]:
    """Uses regex heuristics to extract player names, linked clubs, and status from news text."""
    # Heuristic transfer verbs
    verbs = r"(?:linked with|set to join|nearing move to|agrees deal with|transfers to|signs for|targets|bids for)"
    pattern = rf"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+{verbs}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"

    match = re.search(pattern, text)
    if match:
        player = match.group(1).strip()
        club = match.group(2).strip()
    else:
        player = None
        club = None

    # Status classification
    lower_text = text.lower()
    if "official" in lower_text or "confirmed" in lower_text or "signs" in lower_text:
        status = RumourStatus.CONFIRMED
    elif "denies" in lower_text or "rejects" in lower_text or "rules out" in lower_text:
        status = RumourStatus.DENIED
    elif "speculation" in lower_text or "suggests" in lower_text:
        status = RumourStatus.SPECULATION
    else:
        status = RumourStatus.RUMOUR

    return {
        "player_name": player,
        "to_club_name": club,
        "status": status
    }


def ingest_rss_news_feeds() -> Dict[str, Any]:
    """Ingests RSS feeds, deduplicates articles, extracts rumours, and persists records."""
    session = SessionLocal()
    articles_ingested = 0
    rumours_extracted = 0

    try:
        for feed_info in RSS_FEEDS:
            source_name = feed_info["source"]
            feed_url = feed_info["url"]
            logger.info(f"Polling RSS feed for {source_name}: {feed_url}")

            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = entry.get("summary", title).strip()

                if not title or not link:
                    continue

                content_hash = generate_content_hash(f"{title}|{link}")

                # Check deduplication
                existing = session.query(NewsArticle).filter(
                    (NewsArticle.url == link) | (NewsArticle.content_hash == content_hash)
                ).first()

                if existing:
                    continue

                article = NewsArticle(
                    title=title,
                    url=link,
                    source_name=source_name,
                    content_hash=content_hash,
                    summary=summary,
                    published_at=datetime.utcnow()
                )
                session.add(article)
                session.flush()
                articles_ingested += 1

                # Extract transfer entities
                extracted = extract_entities_regex(f"{title}. {summary}")
                if extracted["player_name"] and extracted["to_club_name"]:
                    rumour = Rumour(
                        article_id=article.id,
                        player_name=extracted["player_name"],
                        to_club_name=extracted["to_club_name"],
                        status=extracted["status"],
                        source_name=source_name,
                        source_url=link,
                        published_at=datetime.utcnow(),
                        confidence_score=0.75 if extracted["status"] == RumourStatus.CONFIRMED else 0.55
                    )
                    session.add(rumour)
                    rumours_extracted += 1

        session.commit()
        logger.info(f"News Ingestion finished. Ingested {articles_ingested} articles, extracted {rumours_extracted} rumours.")
        return {
            "articles_ingested": articles_ingested,
            "rumours_extracted": rumours_extracted,
            "status": "SUCCESS"
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error during news ingestion: {e}")
        return {
            "articles_ingested": articles_ingested,
            "rumours_extracted": rumours_extracted,
            "status": "ERROR",
            "error": str(e)
        }
    finally:
        session.close()
