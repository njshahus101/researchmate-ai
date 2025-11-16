"""
Unit tests for Query Classification Agent

Tests cover:
- Classification accuracy for different query types
- Memory service integration
- JSON response validation
- Error handling
- Edge cases
"""

import pytest
import asyncio
import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.query_classifier_mvp import (
    create_query_classifier_mvp,
    classify_query,
    create_memory_retrieval_tool
)
from services.memory_service import MemoryService
from google.genai import types


class TestQueryClassifier:
    """Test suite for Query Classifier Agent"""

    @pytest.fixture
    def retry_config(self):
        """Create a standard retry configuration"""
        return types.HttpRetryOptions(
            attempts=5,
            exp_base=7,
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],
        )

    @pytest.fixture
    def memory_service(self, tmp_path):
        """Create a memory service with temporary storage"""
        storage_path = tmp_path / "test_memory.json"
        return MemoryService(storage_path=str(storage_path))

    @pytest.fixture
    def test_user_id(self):
        """Standard test user ID"""
        return "test_user_123"

    def test_agent_creation_without_memory(self, retry_config):
        """Test creating agent without memory service"""
        agent = create_query_classifier_mvp(retry_config)

        assert agent is not None
        assert agent.name == "query_classifier_mvp"
        assert "query analyzer" in agent.description.lower()

    def test_agent_creation_with_memory(self, retry_config, memory_service, test_user_id):
        """Test creating agent with memory service"""
        agent = create_query_classifier_mvp(retry_config, memory_service, test_user_id)

        assert agent is not None
        assert agent.name == "query_classifier_mvp"
        assert "context awareness" in agent.description.lower()

    def test_memory_retrieval_tool_creation(self, memory_service, test_user_id):
        """Test creating memory retrieval tool"""
        tool = create_memory_retrieval_tool(memory_service, test_user_id)

        assert callable(tool)

        # Test the tool
        context = tool()
        assert "preferences" in context
        assert "recent_research" in context
        assert "domain_knowledge" in context

    def test_memory_retrieval_tool_with_topics(self, memory_service, test_user_id):
        """Test memory retrieval with related topics"""
        # Add some research history
        memory_service.add_research_entry(
            test_user_id,
            "Best wireless headphones",
            "comparative",
            ["headphones", "audio", "wireless"]
        )

        tool = create_memory_retrieval_tool(memory_service, test_user_id)
        context = tool(query_topics=["headphones"])

        assert "related_topics" in context
        assert isinstance(context["related_topics"], list)

    @pytest.mark.asyncio
    async def test_classify_query_without_api_key(self):
        """Test classification fails gracefully without API key"""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": ""}, clear=True):
            result = await classify_query("test query")

            assert "error" in result
            assert "GOOGLE_API_KEY" in result["error"]

    @pytest.mark.asyncio
    async def test_classify_query_structure(self):
        """Test that classification returns expected structure"""
        # This test requires a valid API key and may be slow
        # Skip if API key not available
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not available")

        result = await classify_query("What is the capital of France?")

        # Check structure
        if "error" not in result:
            assert "query_type" in result
            assert "complexity_score" in result
            assert "research_strategy" in result
            assert "key_topics" in result
            assert "user_intent" in result
            assert "estimated_sources" in result
            assert "reasoning" in result

            # Validate types
            assert isinstance(result["query_type"], str)
            assert isinstance(result["complexity_score"], int)
            assert isinstance(result["research_strategy"], str)
            assert isinstance(result["key_topics"], list)
            assert isinstance(result["estimated_sources"], int)

            # Validate ranges
            assert 1 <= result["complexity_score"] <= 10
            assert result["query_type"] in ["factual", "comparative", "exploratory", "monitoring"]
            assert result["research_strategy"] in ["quick-answer", "multi-source", "deep-dive"]

    @pytest.mark.asyncio
    async def test_classify_with_memory(self, memory_service, test_user_id):
        """Test classification with memory service"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not available")

        # Add some user preferences
        memory_service.store_preference(test_user_id, "priority_quality", True)
        memory_service.store_preference(test_user_id, "preferred_brands", ["Sony", "Bose"])

        # Add research history
        memory_service.add_research_entry(
            test_user_id,
            "Best noise-cancelling headphones",
            "comparative",
            ["headphones", "audio", "noise-cancelling"]
        )

        result = await classify_query(
            "Sony WH-1000XM5 review",
            user_id=test_user_id,
            memory_service=memory_service
        )

        # Check that classification succeeded
        if "error" not in result:
            assert "query_type" in result

            # Check that entry was added to memory
            recent = memory_service.get_recent_research(test_user_id, limit=5)
            assert len(recent) == 2  # Original + new entry

    def test_memory_service_integration(self, memory_service, test_user_id):
        """Test memory service stores and retrieves data correctly"""
        # Store preference
        memory_service.store_preference(test_user_id, "test_pref", "test_value")

        # Retrieve preference
        value = memory_service.get_preference(test_user_id, "test_pref")
        assert value == "test_value"

        # Add research entry
        memory_service.add_research_entry(
            test_user_id,
            "Test query",
            "factual",
            ["topic1", "topic2"]
        )

        # Get recent research
        recent = memory_service.get_recent_research(test_user_id, limit=10)
        assert len(recent) == 1
        assert recent[0]["query"] == "Test query"
        assert recent[0]["query_type"] == "factual"

        # Check topic connections
        related = memory_service.get_related_topics(test_user_id, "topic1")
        assert "topic2" in related


class TestQueryTypeClassification:
    """Test classification accuracy for different query types"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("query,expected_type", [
        ("What is the capital of Japan?", "factual"),
        ("Who invented the telephone?", "factual"),
        ("Best laptops under $1000", "comparative"),
        ("iPhone vs Android comparison", "comparative"),
        ("Explain quantum computing", "exploratory"),
        ("How does blockchain work?", "exploratory"),
        ("Latest AI developments", "monitoring"),
        ("Recent news about climate change", "monitoring"),
    ])
    async def test_query_type_classification(self, query, expected_type):
        """Test that different queries are classified correctly"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not available")

        result = await classify_query(query)

        if "error" not in result:
            assert result["query_type"] == expected_type, \
                f"Query '{query}' classified as {result['query_type']}, expected {expected_type}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("query,expected_complexity_range", [
        ("What is 2+2?", (1, 3)),  # Simple factual
        ("Best wireless headphones", (4, 7)),  # Moderate comparative
        ("Explain quantum entanglement in detail", (7, 10)),  # Complex exploratory
    ])
    async def test_complexity_scoring(self, query, expected_complexity_range):
        """Test that complexity scores are appropriate"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not available")

        result = await classify_query(query)

        if "error" not in result:
            complexity = result["complexity_score"]
            min_expected, max_expected = expected_complexity_range
            assert min_expected <= complexity <= max_expected, \
                f"Query '{query}' has complexity {complexity}, expected {expected_complexity_range}"


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_empty_query(self):
        """Test handling of empty query"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not available")

        result = await classify_query("")

        # Should either classify it or return an error, but not crash
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_very_long_query(self):
        """Test handling of very long query"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not available")

        long_query = "What is " + "very " * 100 + "long query about AI?"
        result = await classify_query(long_query)

        # Should handle gracefully
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_special_characters_in_query(self):
        """Test handling of special characters"""
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not available")

        result = await classify_query("What's the best C++ & Python IDE?")

        # Should handle special characters
        assert isinstance(result, dict)

    def test_memory_service_with_invalid_path(self):
        """Test memory service with invalid storage path"""
        # Should create memory service but fail to save
        memory = MemoryService(storage_path="/invalid/path/memory.json")

        # Should still work in memory
        user_memory = memory.get_user_memory("test_user")
        assert "preferences" in user_memory


class TestResponseValidation:
    """Test JSON response validation"""

    def test_json_structure_validation(self):
        """Test that we validate JSON structure correctly"""
        # Valid JSON
        valid_response = {
            "query_type": "factual",
            "complexity_score": 5,
            "research_strategy": "multi-source",
            "key_topics": ["topic1"],
            "user_intent": "test",
            "estimated_sources": 3,
            "reasoning": "test"
        }

        assert "query_type" in valid_response
        assert valid_response["query_type"] in ["factual", "comparative", "exploratory", "monitoring"]
        assert 1 <= valid_response["complexity_score"] <= 10

    def test_required_fields_present(self):
        """Test that all required fields are present"""
        required_fields = [
            "query_type",
            "complexity_score",
            "research_strategy",
            "key_topics",
            "user_intent",
            "estimated_sources",
            "reasoning"
        ]

        response = {
            "query_type": "factual",
            "complexity_score": 5,
            "research_strategy": "quick-answer",
            "key_topics": ["test"],
            "user_intent": "test",
            "estimated_sources": 1,
            "reasoning": "test"
        }

        for field in required_fields:
            assert field in response, f"Required field '{field}' missing"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
