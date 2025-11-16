"""
Source Authority Scoring Module

Provides functions to score the authority and credibility of web sources.
"""

from urllib.parse import urlparse
from typing import Dict, List, Any
import re


# Domain authority lists
HIGH_AUTHORITY_DOMAINS = {
    # Educational
    '.edu', '.ac.uk', '.edu.au',
    # Government
    '.gov', '.gov.uk', '.gc.ca',
    # International organizations
    '.org', '.int',
}

TRUSTED_NEWS_OUTLETS = {
    'bbc.com', 'bbc.co.uk', 'reuters.com', 'apnews.com', 'npr.org',
    'theguardian.com', 'nytimes.com', 'washingtonpost.com', 'wsj.com',
    'economist.com', 'forbes.com', 'bloomberg.com', 'cnbc.com',
    'scientificamerican.com', 'nature.com', 'sciencemag.org'
}

TECH_AUTHORITY_SITES = {
    'stackoverflow.com', 'github.com', 'docs.python.org', 'developer.mozilla.org',
    'techcrunch.com', 'arstechnica.com', 'theverge.com', 'wired.com',
    'microsoft.com', 'google.com', 'apple.com', 'aws.amazon.com'
}

MEDICAL_AUTHORITY_SITES = {
    'nih.gov', 'cdc.gov', 'who.int', 'mayoclinic.org', 'webmd.com',
    'health.harvard.edu', 'hopkinsmedicine.org', 'pubmed.ncbi.nlm.nih.gov'
}

# Low quality indicators
UNRELIABLE_INDICATORS = {
    'blogspot.com', 'wordpress.com', 'tumblr.com', 'medium.com',
    'quora.com', 'answers.yahoo.com'
}


def calculate_authority_score(url: str, title: str = "", content: str = "") -> Dict[str, Any]:
    """
    Calculate an authority score for a web source (1-10 scale).

    Scoring criteria:
    - Domain authority: .edu, .gov, major news sites, etc.
    - Content quality indicators
    - Domain reputation

    Args:
        url: The URL to score
        title: Page title (optional, for additional context)
        content: Page content (optional, for quality indicators)

    Returns:
        Dictionary with:
        - score: Integer 1-10
        - category: Type of authority (academic, government, news, etc.)
        - reasons: List of reasons for the score
    """
    score = 5  # Start at neutral
    reasons = []
    category = "general"

    # Parse URL
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
    except Exception:
        return {
            "score": 1,
            "category": "invalid",
            "reasons": ["Invalid URL format"]
        }

    # Check for HTTPS (security)
    if parsed.scheme == 'https':
        score += 0.5
        reasons.append("Secure connection (HTTPS)")

    # Check domain type
    # Educational institutions - highest authority for academic topics
    if any(domain.endswith(edu) for edu in ['.edu', '.ac.uk', '.edu.au']):
        score += 3
        category = "academic"
        reasons.append("Educational institution domain")

    # Government sources - highest authority for official information
    elif any(domain.endswith(gov) for gov in ['.gov', '.gov.uk', '.gc.ca']):
        score += 3
        category = "government"
        reasons.append("Government domain")

    # Medical authority sites
    elif any(med in domain for med in MEDICAL_AUTHORITY_SITES):
        score += 2.5
        category = "medical"
        reasons.append("Recognized medical authority")

    # Trusted news outlets
    elif any(news in domain for news in TRUSTED_NEWS_OUTLETS):
        score += 2
        category = "news"
        reasons.append("Established news organization")

    # Tech authority sites
    elif any(tech in domain for tech in TECH_AUTHORITY_SITES):
        score += 2
        category = "technical"
        reasons.append("Recognized technical authority")

    # Wikipedia - special case: good for general info but not primary source
    elif 'wikipedia.org' in domain:
        score += 1.5
        category = "encyclopedia"
        reasons.append("Collaborative encyclopedia (good for overviews)")

    # Check for unreliable indicators
    for unreliable in UNRELIABLE_INDICATORS:
        if unreliable in domain:
            score -= 2
            reasons.append(f"User-generated content platform ({unreliable})")
            category = "user_generated"
            break

    # Content quality indicators (if content provided)
    if content:
        # Check for citations/references
        if re.search(r'\[(\d+)\]|References|Bibliography|Citations', content, re.IGNORECASE):
            score += 0.5
            reasons.append("Contains citations/references")

        # Check for author information
        if re.search(r'By |Author:|Written by', content, re.IGNORECASE):
            score += 0.5
            reasons.append("Author information present")

        # Check for date/freshness
        if re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|Updated|Published', content, re.IGNORECASE):
            score += 0.5
            reasons.append("Date/timestamp present")

    # Ensure score is within bounds
    score = max(1, min(10, score))

    return {
        "score": round(score, 1),
        "category": category,
        "reasons": reasons
    }


def rank_sources_by_authority(sources: List[Dict]) -> List[Dict]:
    """
    Rank a list of sources by their authority scores.

    Args:
        sources: List of source dictionaries, each containing at least 'url'

    Returns:
        Sorted list of sources with authority scores added
    """
    # Calculate authority for each source
    for source in sources:
        url = source.get('url', '')
        title = source.get('title', '')
        content = source.get('content', '')

        authority_data = calculate_authority_score(url, title, content)
        source['authority_score'] = authority_data['score']
        source['authority_category'] = authority_data['category']
        source['authority_reasons'] = authority_data['reasons']

    # Sort by authority score (descending)
    ranked_sources = sorted(sources, key=lambda x: x.get('authority_score', 0), reverse=True)

    return ranked_sources


def select_top_authoritative_sources(sources: List[Dict], count: int = 5, min_score: float = 4.0) -> List[Dict]:
    """
    Select the top N most authoritative sources from a list.

    Args:
        sources: List of source dictionaries
        count: Maximum number of sources to select (default: 5)
        min_score: Minimum authority score to include (default: 4.0)

    Returns:
        List of top authoritative sources
    """
    # Rank all sources
    ranked = rank_sources_by_authority(sources)

    # Filter by minimum score and take top N
    filtered = [s for s in ranked if s.get('authority_score', 0) >= min_score]

    return filtered[:count]
