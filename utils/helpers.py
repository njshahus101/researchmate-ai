"""
Helper Functions

Utility functions used across the ResearchMate AI application.
"""

from google.genai import types
from typing import Dict, Any, List
import os


def create_retry_config() -> types.HttpRetryOptions:
    """
    Create retry configuration for HTTP requests to LLM.

    Returns:
        HttpRetryOptions configured based on environment or defaults
    """
    return types.HttpRetryOptions(
        attempts=int(os.getenv("RETRY_ATTEMPTS", "5")),
        exp_base=int(os.getenv("RETRY_EXP_BASE", "7")),
        initial_delay=int(os.getenv("RETRY_INITIAL_DELAY", "1")),
        http_status_codes=[429, 500, 503, 504],
    )


def format_sources_list(sources: List[Dict[str, Any]]) -> str:
    """
    Format a list of sources into a readable citation list.

    Args:
        sources: List of source dictionaries with url, title, etc.

    Returns:
        Formatted string with numbered citations
    """
    if not sources:
        return "No sources available."

    formatted = "## Sources\n\n"

    for i, source in enumerate(sources, 1):
        title = source.get("title", "Untitled")
        url = source.get("url", "No URL")
        domain = source.get("domain", "Unknown domain")
        credibility = source.get("credibility_score", "N/A")

        formatted += f"[{i}] **{title}**\n"
        formatted += f"    - URL: {url}\n"
        formatted += f"    - Domain: {domain}\n"
        formatted += f"    - Credibility: {credibility}/10\n\n"

    return formatted


def extract_key_topics(query: str) -> List[str]:
    """
    Extract key topics from a query (simple keyword extraction).

    Args:
        query: User query string

    Returns:
        List of extracted topics
    """
    # This is a simplified implementation
    # In production, you might use NLP libraries or LLM for better extraction

    # Remove common words
    stop_words = {
        'what', 'is', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'by', 'from', 'about', 'can', 'you', 'tell',
        'me', 'best', 'good', 'how', 'why', 'when', 'where', 'which'
    }

    # Simple tokenization and filtering
    words = query.lower().split()
    topics = [word.strip('?,.:;!') for word in words if word.lower() not in stop_words]

    # Remove duplicates while preserving order
    seen = set()
    unique_topics = []
    for topic in topics:
        if topic not in seen and len(topic) > 2:  # Filter very short words
            seen.add(topic)
            unique_topics.append(topic)

    return unique_topics


def estimate_research_time(query_type: str, num_sources: int) -> float:
    """
    Estimate research time based on query type and sources.

    Args:
        query_type: Type of query (factual, comparative, exploratory)
        num_sources: Number of sources to research

    Returns:
        Estimated time in seconds
    """
    base_times = {
        "factual": 3,      # 3 seconds
        "comparative": 10,  # 10 seconds base
        "exploratory": 15,  # 15 seconds base
        "monitoring": 8     # 8 seconds base
    }

    base_time = base_times.get(query_type, 10)

    # Add time per source
    time_per_source = 5  # 5 seconds per additional source

    total_time = base_time + (max(0, num_sources - 1) * time_per_source)

    return total_time


def calculate_time_saved(traditional_time_hours: float, ai_time_seconds: float) -> Dict[str, Any]:
    """
    Calculate time saved by using ResearchMate AI.

    Args:
        traditional_time_hours: Traditional research time in hours
        ai_time_seconds: AI research time in seconds

    Returns:
        Dictionary with time saved metrics
    """
    traditional_seconds = traditional_time_hours * 3600
    ai_hours = ai_time_seconds / 3600

    time_saved_seconds = traditional_seconds - ai_time_seconds
    time_saved_hours = time_saved_seconds / 3600

    percent_saved = (time_saved_seconds / traditional_seconds) * 100

    return {
        "traditional_time_hours": traditional_time_hours,
        "ai_time_seconds": ai_time_seconds,
        "ai_time_hours": ai_hours,
        "time_saved_hours": time_saved_hours,
        "percent_saved": percent_saved,
        "speedup_factor": traditional_seconds / ai_time_seconds if ai_time_seconds > 0 else 0
    }


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid, False otherwise
    """
    from urllib.parse import urlparse

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


if __name__ == "__main__":
    # Test helper functions
    print("Testing helper functions...\n")

    # Test retry config
    retry_config = create_retry_config()
    print(f"✅ Retry config: {retry_config.attempts} attempts\n")

    # Test source formatting
    sources = [
        {
            "title": "Understanding AI Agents",
            "url": "https://example.com/ai-agents",
            "domain": "example.com",
            "credibility_score": 9
        },
        {
            "title": "Multi-Agent Systems",
            "url": "https://research.org/multi-agent",
            "domain": "research.org",
            "credibility_score": 10
        }
    ]
    print(format_sources_list(sources))

    # Test topic extraction
    query = "What are the best wireless headphones under $200 for working out?"
    topics = extract_key_topics(query)
    print(f"✅ Topics from query: {topics}\n")

    # Test time estimation
    time_est = estimate_research_time("comparative", 5)
    print(f"✅ Estimated research time: {time_est} seconds\n")

    # Test time saved calculation
    savings = calculate_time_saved(2.5, 45)
    print(f"✅ Time saved: {savings['time_saved_hours']:.2f} hours ({savings['percent_saved']:.1f}% faster)\n")

    # Test URL validation
    print(f"✅ Valid URL check: {validate_url('https://example.com')}")
    print(f"✅ Invalid URL check: {validate_url('not a url')}")
