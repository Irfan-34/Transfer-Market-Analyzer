from typing import Dict, Any


def calculate_transfer_intelligence_score(
    ml_probability: float,
    source_reliability: float = 0.5,
    rumour_count: int = 1,
    positional_fit_score: float = 0.7
) -> Dict[str, Any]:
    """Computes a transparent composite score (0-100) combining ML probability, media track record, and rumor volume.
    
    Returns:
        Dict[str, Any]: Intelligence score breakdown and rating label.
    """
    # 1. ML Probability Component (0-40 points)
    ml_component = max(0.0, min(1.0, ml_probability)) * 40.0

    # 2. Source Reliability Component (0-30 points)
    source_component = max(0.0, min(1.0, source_reliability)) * 30.0

    # 3. Report Count Component (0-15 points) - log scale up to 5 reports
    count_factor = min(1.0, rumour_count / 5.0)
    count_component = count_factor * 15.0

    # 4. Positional Fit Component (0-15 points)
    fit_component = max(0.0, min(1.0, positional_fit_score)) * 15.0

    total_score = round(ml_component + source_component + count_component + fit_component, 1)

    # Rating label
    if total_score >= 80.0:
        rating = "VERY HIGH CONFIDENCE"
    elif total_score >= 65.0:
        rating = "HIGH LIKELIHOOD"
    elif total_score >= 45.0:
        rating = "MODERATE LINK"
    elif total_score >= 25.0:
        rating = "SPECULATIVE"
    else:
        rating = "UNLIKELY"

    return {
        "intelligence_score": total_score,
        "rating": rating,
        "breakdown": {
            "ml_probability_points": round(ml_component, 1),
            "source_reliability_points": round(source_component, 1),
            "rumour_volume_points": round(count_component, 1),
            "positional_fit_points": round(fit_component, 1)
        }
    }
