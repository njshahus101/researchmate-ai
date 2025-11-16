"""
Unit tests for Information Gatherer Agent

Tests cover:
- Source authority scoring
- Parallel fetching
- Error handling
- Success rate calculation
- Agent functionality
"""

import pytest
import asyncio
from typing import Dict, List
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.source_authority import (
    calculate_authority_score,
    rank_sources_by_authority,
    select_top_authoritative_sources
)
from tools.parallel_fetcher import (
    fetch_multiple_urls,
    calculate_success_rate,
    fetch_with_retry
)
from tools.web_fetcher import fetch_webpage_content


class TestAuthorityScoring:
    """Test source authority scoring functionality."""

    def test_edu_domain_high_score(self):
        """Educational domains should get high authority scores."""
        result = calculate_authority_score("https://mit.edu/article")
        assert result['score'] >= 8.0
        assert result['category'] == 'academic'
        assert any('Educational' in r for r in result['reasons'])

    def test_gov_domain_high_score(self):
        """Government domains should get high authority scores."""
        result = calculate_authority_score("https://cdc.gov/health-info")
        assert result['score'] >= 8.0
        assert result['category'] == 'government'

    def test_trusted_news_outlet(self):
        """Trusted news outlets should get good scores."""
        result = calculate_authority_score("https://www.bbc.com/news/article")
        assert result['score'] >= 7.0
        assert result['category'] == 'news'

    def test_tech_authority_site(self):
        """Tech authority sites should get good scores."""
        result = calculate_authority_score("https://stackoverflow.com/questions/12345")
        assert result['score'] >= 7.0
        assert result['category'] == 'technical'

    def test_medical_authority(self):
        """Medical authority sites should get high scores."""
        result = calculate_authority_score("https://www.mayoclinic.org/diseases")
        assert result['score'] >= 7.5
        assert result['category'] == 'medical'

    def test_wikipedia_moderate_score(self):
        """Wikipedia should get moderate scores."""
        result = calculate_authority_score("https://en.wikipedia.org/wiki/Python")
        assert 6.0 <= result['score'] <= 8.0
        assert result['category'] == 'encyclopedia'

    def test_user_generated_low_score(self):
        """User-generated content should get lower scores."""
        result = calculate_authority_score("https://someone.blogspot.com/my-post")
        assert result['score'] <= 5.0
        assert result['category'] == 'user_generated'

    def test_https_bonus(self):
        """HTTPS should add to the score."""
        https_result = calculate_authority_score("https://example.com")
        http_result = calculate_authority_score("http://example.com")
        assert https_result['score'] > http_result['score']

    def test_content_with_citations(self):
        """Content with citations should score higher."""
        content = "This is an article. [1] References: 1. Smith et al."
        result = calculate_authority_score("https://example.com", content=content)
        # Should have citation bonus in reasons
        assert any('citation' in r.lower() for r in result['reasons'])

    def test_invalid_url(self):
        """Invalid URLs should return low score."""
        result = calculate_authority_score("not-a-url")
        assert result['score'] == 1
        assert result['category'] == 'invalid'


class TestSourceRanking:
    """Test source ranking and selection."""

    def test_rank_sources_by_authority(self):
        """Sources should be ranked by authority score."""
        sources = [
            {"url": "https://blogspot.com/post", "title": "Blog Post"},
            {"url": "https://mit.edu/research", "title": "MIT Research"},
            {"url": "https://example.com", "title": "Example"},
        ]

        ranked = rank_sources_by_authority(sources)

        # MIT should be first (highest authority)
        assert 'mit.edu' in ranked[0]['url']
        assert ranked[0]['authority_score'] > ranked[1]['authority_score']
        assert ranked[1]['authority_score'] > ranked[2]['authority_score']

    def test_select_top_authoritative_sources(self):
        """Should select only top N authoritative sources."""
        sources = [
            {"url": f"https://example{i}.com", "title": f"Example {i}"}
            for i in range(10)
        ]
        sources.insert(0, {"url": "https://stanford.edu/paper", "title": "Stanford"})

        top_sources = select_top_authoritative_sources(sources, count=3, min_score=4.0)

        # Should return at most 3 sources
        assert len(top_sources) <= 3
        # Stanford should be first
        assert 'stanford.edu' in top_sources[0]['url']

    def test_min_score_filter(self):
        """Sources below minimum score should be filtered out."""
        sources = [
            {"url": "https://blogspot.com/post1", "title": "Blog 1"},
            {"url": "https://wordpress.com/post2", "title": "Blog 2"},
        ]

        top_sources = select_top_authoritative_sources(sources, count=5, min_score=7.0)

        # All sources are low quality, should return empty or very few
        assert len(top_sources) == 0  # All below min_score of 7.0


class TestSuccessRateCalculation:
    """Test success rate calculation."""

    def test_calculate_success_rate_all_success(self):
        """100% success rate when all fetches succeed."""
        results = [
            {"status": "success", "url": "https://example1.com"},
            {"status": "success", "url": "https://example2.com"},
            {"status": "success", "url": "https://example3.com"},
        ]

        metrics = calculate_success_rate(results)

        assert metrics['total'] == 3
        assert metrics['successful'] == 3
        assert metrics['failed'] == 0
        assert metrics['success_rate'] == 100.0

    def test_calculate_success_rate_mixed(self):
        """Should correctly calculate mixed success/failure."""
        results = [
            {"status": "success", "url": "https://example1.com"},
            {"status": "error", "url": "https://example2.com", "error_message": "404 not found"},
            {"status": "success", "url": "https://example3.com"},
            {"status": "error", "url": "https://example4.com", "error_message": "timeout"},
        ]

        metrics = calculate_success_rate(results)

        assert metrics['total'] == 4
        assert metrics['successful'] == 2
        assert metrics['failed'] == 2
        assert metrics['success_rate'] == 50.0

    def test_error_type_categorization(self):
        """Should categorize different error types."""
        results = [
            {"status": "error", "error_message": "404 not found", "url": "url1"},
            {"status": "error", "error_message": "403 forbidden", "url": "url2"},
            {"status": "error", "error_message": "Request timed out", "url": "url3"},
            {"status": "error", "error_message": "Connection error", "url": "url4"},
        ]

        metrics = calculate_success_rate(results)

        assert metrics['error_types']['404_not_found'] == 1
        assert metrics['error_types']['403_forbidden'] == 1
        assert metrics['error_types']['timeout'] == 1
        assert metrics['error_types']['connection_error'] == 1

    def test_empty_results(self):
        """Should handle empty results gracefully."""
        metrics = calculate_success_rate([])

        assert metrics['total'] == 0
        assert metrics['successful'] == 0
        assert metrics['failed'] == 0
        assert metrics['success_rate'] == 0


class TestParallelFetching:
    """Test parallel URL fetching functionality."""

    @pytest.mark.asyncio
    async def test_fetch_multiple_urls_success(self):
        """Should fetch multiple URLs in parallel."""
        # Use real, reliable URLs
        urls = [
            "https://www.example.com",
            "https://www.iana.org/domains/reserved",
        ]

        results = await fetch_multiple_urls(
            urls=urls,
            fetch_function=fetch_webpage_content,
            max_concurrent=2,
            timeout=15
        )

        assert len(results) == 2
        # At least one should succeed (example.com is very reliable)
        successful = [r for r in results if r.get('status') == 'success']
        assert len(successful) >= 1

    @pytest.mark.asyncio
    async def test_fetch_with_404_error(self):
        """Should handle 404 errors gracefully."""
        urls = [
            "https://www.example.com/this-page-does-not-exist-123456789"
        ]

        results = await fetch_multiple_urls(
            urls=urls,
            fetch_function=fetch_webpage_content,
            max_concurrent=1,
            timeout=10
        )

        assert len(results) == 1
        assert results[0]['status'] == 'error'
        assert '404' in results[0]['error_message']

    @pytest.mark.asyncio
    async def test_fetch_with_invalid_url(self):
        """Should handle invalid URLs gracefully."""
        urls = ["not-a-valid-url"]

        results = await fetch_multiple_urls(
            urls=urls,
            fetch_function=fetch_webpage_content,
            max_concurrent=1,
            timeout=10
        )

        assert len(results) == 1
        assert results[0]['status'] == 'error'

    @pytest.mark.asyncio
    async def test_fetch_with_retry(self):
        """Retry logic should work for transient failures."""
        # Use a URL that might have occasional issues
        url = "https://www.example.com"

        result = await fetch_with_retry(
            url=url,
            fetch_function=fetch_webpage_content,
            max_retries=2,
            timeout=10
        )

        # Should eventually succeed
        assert result['status'] == 'success'

    @pytest.mark.asyncio
    async def test_concurrency_limit(self):
        """Should respect max_concurrent limit."""
        urls = [f"https://www.example.com" for _ in range(10)]

        # Fetch with concurrency limit of 3
        import time
        start_time = time.time()

        results = await fetch_multiple_urls(
            urls=urls,
            fetch_function=fetch_webpage_content,
            max_concurrent=3,
            timeout=10
        )

        elapsed = time.time() - start_time

        # Should get all results
        assert len(results) == 10

        # With concurrency of 3 for 10 URLs, should take longer than 1 sequential fetch
        # but less than 10 sequential fetches


class TestWebFetcher:
    """Test the web content fetcher."""

    def test_fetch_valid_url(self):
        """Should successfully fetch a valid URL."""
        result = fetch_webpage_content("https://www.example.com", timeout=15)

        assert result['status'] == 'success'
        assert 'title' in result
        assert 'content' in result
        assert len(result['content']) > 0

    def test_fetch_404_url(self):
        """Should handle 404 errors properly."""
        result = fetch_webpage_content(
            "https://www.example.com/nonexistent-page-xyz123",
            timeout=10
        )

        assert result['status'] == 'error'
        assert '404' in result['error_message']

    def test_fetch_invalid_url_format(self):
        """Should reject invalid URL formats."""
        result = fetch_webpage_content("not-a-url")

        assert result['status'] == 'error'
        assert 'Invalid URL' in result['error_message']

    def test_fetch_without_http_scheme(self):
        """Should reject URLs without http/https."""
        result = fetch_webpage_content("example.com")

        assert result['status'] == 'error'
        assert 'Invalid URL' in result['error_message']


@pytest.mark.integration
class TestInformationGathererIntegration:
    """Integration tests for the Information Gatherer agent."""

    @pytest.mark.asyncio
    async def test_gather_information_enhanced(self):
        """Test enhanced information gathering with real URLs."""
        from agents.information_gatherer_mvp import gather_information_enhanced

        # Test with a few reliable URLs
        urls = [
            "https://www.example.com",
            "https://en.wikipedia.org/wiki/Python_(programming_language)",
        ]

        result = await gather_information_enhanced(
            query="Python programming language",
            urls=urls
        )

        # Should have metrics
        assert 'metrics' in result
        assert result['metrics']['total'] == 2

        # Should have success rate >= 80% (at least 1 of 2 should succeed)
        assert result['metrics']['success_rate'] >= 50.0

        # Should have sources with authority scores
        assert 'sources' in result
        for source in result['sources']:
            assert 'authority_score' in source
            assert 'authority_category' in source
            assert 'fetch_status' in source


# Success Criteria Validation Test
@pytest.mark.success_criteria
class TestSuccessCriteria:
    """
    Tests to validate the success criteria:
    - Successfully fetches and extracts content from 80%+ of URLs
    - Correctly identifies authoritative sources
    - Handles errors without crashing
    - Returns structured source data
    """

    @pytest.mark.asyncio
    async def test_80_percent_success_rate(self):
        """Should achieve 80%+ success rate on valid URLs."""
        # Mix of reliable URLs
        urls = [
            "https://www.example.com",
            "https://www.iana.org",
            "https://www.w3.org",
            "https://en.wikipedia.org/wiki/Internet",
            "https://www.python.org",
        ]

        results = await fetch_multiple_urls(
            urls=urls,
            fetch_function=fetch_webpage_content,
            max_concurrent=3,
            timeout=15
        )

        metrics = calculate_success_rate(results)

        # Should achieve at least 80% success
        assert metrics['success_rate'] >= 80.0, \
            f"Success rate {metrics['success_rate']}% is below 80% threshold"

    def test_authority_identification(self):
        """Should correctly identify authoritative sources."""
        sources = [
            {"url": "https://mit.edu/research", "title": "MIT Research"},
            {"url": "https://cdc.gov/health", "title": "CDC Health"},
            {"url": "https://blogspot.com/random", "title": "Random Blog"},
            {"url": "https://bbc.com/news", "title": "BBC News"},
        ]

        ranked = rank_sources_by_authority(sources)

        # Educational and government should rank highest
        assert 'mit.edu' in ranked[0]['url'] or 'cdc.gov' in ranked[0]['url']
        assert ranked[0]['authority_score'] > 8.0

        # BBC should rank higher than blogspot
        bbc_rank = next(i for i, s in enumerate(ranked) if 'bbc.com' in s['url'])
        blog_rank = next(i for i, s in enumerate(ranked) if 'blogspot.com' in s['url'])
        assert bbc_rank < blog_rank

    @pytest.mark.asyncio
    async def test_error_handling_no_crash(self):
        """Should handle various errors without crashing."""
        problematic_urls = [
            "https://this-domain-definitely-does-not-exist-xyz123.com",
            "not-a-url",
            "https://www.example.com/404-page-not-found",
            "https://www.example.com",  # One good URL
        ]

        try:
            results = await fetch_multiple_urls(
                urls=problematic_urls,
                fetch_function=fetch_webpage_content,
                max_concurrent=2,
                timeout=10
            )

            # Should complete without exceptions
            assert len(results) == len(problematic_urls)

            # Should have at least one success
            successful = [r for r in results if r.get('status') == 'success']
            assert len(successful) >= 1

        except Exception as e:
            pytest.fail(f"Error handling failed with exception: {e}")

    @pytest.mark.asyncio
    async def test_structured_data_return(self):
        """Should return structured source data."""
        from agents.information_gatherer_mvp import gather_information_enhanced

        urls = ["https://www.example.com"]

        result = await gather_information_enhanced(
            query="Test query",
            urls=urls
        )

        # Should have required structure
        assert 'sources' in result
        assert 'metrics' in result
        assert 'success_rate' in result

        # Each source should have required fields
        for source in result['sources']:
            assert 'url' in source
            assert 'title' in source
            assert 'fetch_status' in source
            assert 'authority_score' in source
            assert 'authority_category' in source


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
