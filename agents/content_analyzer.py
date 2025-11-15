"""
Content Analysis Agent

This agent evaluates source credibility, extracts key facts, and identifies
conflicting information across multiple sources.
"""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
from typing import Dict, Any, List


def create_content_analyzer_agent(retry_config: types.HttpRetryOptions) -> LlmAgent:
    """
    Creates the Content Analysis Agent.

    This agent:
    - Assesses source reliability and credibility
    - Extracts key facts, quotes, and statistics
    - Identifies conflicting information
    - Normalizes data for comparisons

    Args:
        retry_config: HTTP retry configuration

    Returns:
        LlmAgent configured for content analysis
    """

    agent = LlmAgent(
        name="content_analyzer",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        description="Critical evaluator that analyzes source credibility and extracts insights",
        instruction="""
        You are the Content Analysis Agent for ResearchMate AI.

        Your role is to critically evaluate sources and extract actionable insights:

        1. SOURCE CREDIBILITY ASSESSMENT:

        Evaluate each source on these dimensions (1-10 scale):
        - Domain Authority: Quality of the publication/website
        - Author Credentials: Expertise and reputation
        - Publication Recency: How current is the information
        - Citation Quality: Are claims backed by evidence?
        - Bias Detection: Is there commercial or political bias?

        Credibility Levels:
        - HIGH (8-10): Academic journals, government sources, established news
        - MEDIUM (5-7): Industry blogs, reputable reviews, verified experts
        - LOW (1-4): Unknown sources, commercial sites, unverified claims

        2. KEY FACT EXTRACTION:

        For each source, extract:
        - Main Claims: Primary assertions or findings
        - Supporting Evidence: Statistics, quotes, data points
        - Specifications: For products (price, features, specs)
        - Expert Opinions: Quotes from credible authorities
        - Confidence Level: How certain is this information?

        3. CONFLICT IDENTIFICATION:

        When sources disagree:
        - Note the specific points of disagreement
        - Identify which sources are more credible
        - Indicate level of consensus (unanimous, majority, split)
        - Flag areas needing further research

        4. DATA NORMALIZATION (for comparisons):

        For product comparisons:
        - Identify common evaluation dimensions
        - Normalize units (e.g., convert all prices to same currency)
        - Create structured comparison data
        - Weight factors by importance

        Output Format:
        {
            "analyzed_sources": [
                {
                    "url": "https://...",
                    "credibility_score": 8,
                    "credibility_factors": {
                        "domain_authority": 9,
                        "author_credentials": 8,
                        "recency": 10,
                        "citation_quality": 7,
                        "bias_detection": 8
                    },
                    "key_facts": [
                        {
                            "claim": "...",
                            "evidence": "...",
                            "confidence": "high|medium|low"
                        }
                    ],
                    "extracted_data": {...},
                    "notable_quotes": ["..."]
                }
            ],
            "conflicts_identified": [
                {
                    "topic": "...",
                    "conflicting_claims": [...],
                    "consensus_level": "unanimous|majority|split",
                    "recommendation": "..."
                }
            ],
            "comparison_matrix": {
                "dimensions": ["price", "quality", "features"],
                "normalized_data": {...}
            },
            "overall_reliability": "high|medium|low",
            "analysis_notes": "..."
        }

        Be thorough, objective, and transparent about limitations.
        """,
        tools=[],  # Pure analysis agent, no external tools needed
    )

    return agent


# Example credibility scoring function
def calculate_credibility_score(source_data: Dict[str, Any]) -> int:
    """
    Calculate overall credibility score for a source.

    Args:
        source_data: Dictionary containing source information

    Returns:
        Credibility score (1-10)
    """
    # Weighted average of credibility factors
    weights = {
        "domain_authority": 0.3,
        "author_credentials": 0.25,
        "recency": 0.15,
        "citation_quality": 0.2,
        "bias_detection": 0.1,
    }

    factors = source_data.get("credibility_factors", {})

    if not factors:
        return 5  # Default medium credibility

    weighted_sum = sum(
        factors.get(factor, 5) * weight
        for factor, weight in weights.items()
    )

    return round(weighted_sum)


if __name__ == "__main__":
    # Test the agent creation
    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )

    analyzer = create_content_analyzer_agent(retry_config)
    print(f"✅ Content Analyzer Agent created: {analyzer.name}")
    print(f"📊 Analysis dimensions: Credibility, Facts, Conflicts, Comparisons")
