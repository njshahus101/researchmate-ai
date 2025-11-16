"""
ResearchMate AI - Main Application

Multi-agent research assistant built with Google ADK.
Demonstrates A2A Protocol, MCP tools, Memory management, and Observability.
"""

import os
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import sys
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.adk.apps.app import App
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from google.genai import types

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import MVP agents
from agents.query_classifier_mvp import create_query_classifier_mvp, classify_query
from agents.information_gatherer import create_information_gatherer_agent

# Import services
from services.memory_service import MemoryService

# Import utilities
from utils.logging_config import setup_logging, AgentLogger
from utils.helpers import create_retry_config


def create_orchestrator_agent(
    retry_config: types.HttpRetryOptions,
    classifier_agent: LlmAgent,
    gatherer_agent: LlmAgent,
    memory_service: MemoryService
) -> LlmAgent:
    """
    Creates the Orchestrator Agent that manages the sequential workflow using A2A.

    This agent:
    - Receives user queries
    - Calls Query Classifier agent (A2A)
    - Calls Information Gatherer agent based on classification (A2A)
    - Provides formatted responses

    Args:
        retry_config: HTTP retry configuration
        classifier_agent: The Query Classifier agent
        gatherer_agent: The Information Gatherer agent
        memory_service: Memory service for user context

    Returns:
        LlmAgent configured as orchestrator with sub-agents as tools
    """

    # Create tool functions that wrap agent calls (A2A Protocol)
    def classify_user_query(query: str, user_id: str = "default") -> dict:
        """
        Classify a user query to determine research strategy.

        This function calls the Query Classifier agent using A2A protocol.

        Args:
            query: The user's research query
            user_id: User identifier for personalization

        Returns:
            Dictionary with classification results including query_type,
            research_strategy, complexity_score, and key_topics
        """
        # Get user context from memory
        user_memory = memory_service.get_user_memory(user_id)
        recent_research = memory_service.get_recent_research(user_id, limit=3)

        # Build context string
        context = f"\n\nUser ID: {user_id}"
        if user_memory.get("preferences"):
            context += f"\nUser Preferences: {json.dumps(user_memory['preferences'])}"
        if recent_research:
            context += f"\nRecent Research: {json.dumps(recent_research)}"

        # Call classifier agent via runner (A2A)
        runner = InMemoryRunner(agent=classifier_agent)
        import asyncio
        try:
            response = asyncio.run(runner.run_debug(query + context))

            # Extract response
            if isinstance(response, list) and len(response) > 0:
                last_event = response[-1]
                if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                    response_text = last_event.content.parts[0].text
                else:
                    response_text = str(last_event)
            else:
                response_text = str(response)

            # Parse JSON response
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()

            classification = json.loads(cleaned_text)

            # Store in memory
            memory_service.add_research_entry(
                user_id,
                query,
                classification.get('query_type', 'unknown'),
                classification.get('key_topics', [])
            )

            return classification

        except Exception as e:
            return {
                "error": str(e),
                "query_type": "unknown",
                "research_strategy": "quick-answer",
                "complexity_score": 5
            }

    def gather_information(query: str, classification: dict) -> dict:
        """
        Gather information from multiple sources based on research strategy.

        This function calls the Information Gatherer agent using A2A protocol.

        Args:
            query: The user's research query
            classification: Classification results from Query Classifier

        Returns:
            Dictionary with gathered information including sources and content
        """
        # Build context for information gatherer
        gatherer_prompt = f"""Research Query: {query}

Query Classification:
- Type: {classification.get('query_type', 'unknown')}
- Strategy: {classification.get('research_strategy', 'quick-answer')}
- Key Topics: {', '.join(classification.get('key_topics', []))}
- Estimated Sources: {classification.get('estimated_sources', 3)}

Please gather information according to the {classification.get('research_strategy', 'quick-answer')} strategy.
Provide sources with URLs, titles, and key findings."""

        # Call gatherer agent via runner (A2A)
        runner = InMemoryRunner(agent=gatherer_agent)
        import asyncio
        try:
            response = asyncio.run(runner.run_debug(gatherer_prompt))

            # Extract response
            if isinstance(response, list) and len(response) > 0:
                last_event = response[-1]
                if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                    response_text = last_event.content.parts[0].text
                else:
                    response_text = str(last_event)
            else:
                response_text = str(response)

            return {
                "status": "success",
                "content": response_text,
                "strategy": classification.get('research_strategy')
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    # Create function tools from these functions
    classify_tool = FunctionTool(func=classify_user_query)
    gather_tool = FunctionTool(func=gather_information)

    instruction = """You are the Orchestrator Agent for ResearchMate AI.

Your role is to coordinate the research pipeline using specialized agents:
1. Query Classifier Agent - analyzes queries and determines strategy
2. Information Gatherer Agent - searches and retrieves information

WORKFLOW:
When a user asks a research question:

1. Call classify_user_query with the query to get classification
2. Based on the research_strategy:
   - If "quick-answer": Skip information gathering, provide quick response
   - If "multi-source" or "deep-dive": Call gather_information to get detailed research
3. Synthesize results and provide a comprehensive response

OUTPUT FORMAT:
Provide clear, structured responses:
- Query Type and Complexity
- Research Strategy Used
- Key Topics Identified
- Information Gathered (if applicable)
- Summary of Findings
- Next Steps or Recommendations

Be conversational, helpful, and thorough. Always explain what you're doing.
"""

    agent = LlmAgent(
        name="research_orchestrator",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        description="Research pipeline orchestrator that coordinates query classification and information gathering via A2A",
        instruction=instruction,
        tools=[classify_tool, gather_tool],
    )

    return agent


class ResearchMateAI:
    """
    ResearchMate AI Application

    Orchestrates the multi-agent pipeline for intelligent research.
    """

    def __init__(self):
        """
        Initialize ResearchMate AI.
        """
        # Load environment variables
        load_dotenv()

        # Setup logging
        self.logger = setup_logging(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_to_file=True
        )
        self.agent_logger = AgentLogger(self.logger)

        self.logger.info("=" * 60)
        self.logger.info("ResearchMate AI Orchestrator Starting...")
        self.logger.info("=" * 60)

        # Configuration
        self.app_name = os.getenv("APP_NAME", "researchmate_ai")
        self.retry_config = create_retry_config()

        # Initialize services
        self.memory_service = MemoryService()

        # Pipeline metrics
        self.pipeline_metrics = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "average_duration": 0.0
        }

        # Create agents
        self._create_agents()

        # Create application
        self._create_app()

        self.logger.info("[SUCCESS] ResearchMate AI Orchestrator initialized successfully!")

    def _create_agents(self):
        """Create agents for the pipeline."""
        self.logger.info("Creating agents...")

        # 1. Query Classifier Agent (MVP version)
        self.query_classifier = create_query_classifier_mvp(
            self.retry_config,
            self.memory_service
        )
        self.logger.info(f"  [OK] {self.query_classifier.name}")

        # 2. Information Gatherer Agent
        self.information_gatherer = create_information_gatherer_agent(
            self.retry_config,
            web_fetcher_tool=None,  # Will add MCP tools later
            price_extractor_tool=None
        )
        self.logger.info(f"  [OK] {self.information_gatherer.name}")

        # 3. Orchestrator Agent - pass sub-agents
        self.orchestrator = create_orchestrator_agent(
            self.retry_config,
            self.query_classifier,
            self.information_gatherer,
            self.memory_service
        )
        self.logger.info(f"  [OK] {self.orchestrator.name}")

    def _create_app(self):
        """Create the main application with orchestrator as root."""
        self.app = App(
            name=self.app_name,
            root_agent=self.orchestrator
        )
        self.logger.info(f"Application created: {self.app_name}")

    async def research(self, query: str, user_id: str = "default") -> dict:
        """
        Execute the full research pipeline with sequential workflow.

        Pipeline: Query Classifier -> Information Gatherer

        Args:
            query: User's research query
            user_id: User identifier

        Returns:
            Dictionary with research results
        """
        pipeline_start = time.time()

        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"NEW RESEARCH REQUEST")
        self.logger.info(f"User: {user_id}")
        self.logger.info(f"Query: {query}")
        self.logger.info(f"{'='*60}\n")

        pipeline_data = {
            "query": query,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "stages": {}
        }

        try:
            # ========================================
            # STAGE 1: Query Classification
            # ========================================
            stage_start = time.time()
            self.agent_logger.log_agent_start("QueryClassifier", query)

            self.logger.info("[Stage 1/2] Running Query Classification...")

            # Call the classifier agent
            classification = await classify_query(
                query=query,
                user_id=user_id,
                memory_service=self.memory_service
            )

            stage_duration = (time.time() - stage_start) * 1000
            self.agent_logger.log_agent_complete("QueryClassifier", stage_duration)

            # Check for errors
            if "error" in classification:
                raise Exception(f"Query classification failed: {classification.get('message', 'Unknown error')}")

            # Store stage results
            pipeline_data["stages"]["classification"] = {
                "status": "success",
                "duration_ms": stage_duration,
                "output": classification
            }

            self.logger.info(f"[OK] Classification complete: {classification.get('query_type')} query")
            self.logger.info(f"  Strategy: {classification.get('research_strategy')}")
            self.logger.info(f"  Complexity: {classification.get('complexity_score')}/10")
            self.logger.info(f"  Duration: {stage_duration:.2f}ms\n")

            # ========================================
            # STAGE 2: Information Gathering
            # ========================================
            # Only run information gathering for certain query types
            research_strategy = classification.get("research_strategy", "quick-answer")

            if research_strategy in ["multi-source", "deep-dive"]:
                stage_start = time.time()
                self.agent_logger.log_agent_start("InformationGatherer", query)

                self.logger.info("[Stage 2/2] Running Information Gathering...")

                # Prepare context for information gatherer
                gatherer_context = {
                    "query": query,
                    "query_type": classification.get("query_type"),
                    "research_strategy": research_strategy,
                    "key_topics": classification.get("key_topics", []),
                    "estimated_sources": classification.get("estimated_sources", 3)
                }

                # Create runner for information gatherer
                runner = InMemoryRunner(agent=self.information_gatherer)

                # Build prompt for information gatherer
                gatherer_prompt = f"""Research Query: {query}

Query Classification:
- Type: {classification.get('query_type')}
- Strategy: {research_strategy}
- Key Topics: {', '.join(classification.get('key_topics', []))}
- Estimated Sources Needed: {classification.get('estimated_sources', 3)}

Please gather information according to the {research_strategy} strategy."""

                response = await runner.run_debug(gatherer_prompt)

                # Extract response
                if isinstance(response, list) and len(response) > 0:
                    last_event = response[-1]
                    if hasattr(last_event, 'content') and hasattr(last_event.content, 'parts'):
                        gatherer_response = last_event.content.parts[0].text
                    else:
                        gatherer_response = str(last_event)
                else:
                    gatherer_response = str(response)

                stage_duration = (time.time() - stage_start) * 1000
                self.agent_logger.log_agent_complete("InformationGatherer", stage_duration)

                # Store stage results
                pipeline_data["stages"]["information_gathering"] = {
                    "status": "success",
                    "duration_ms": stage_duration,
                    "output": gatherer_response
                }

                self.logger.info(f"[OK] Information gathering complete")
                self.logger.info(f"  Duration: {stage_duration:.2f}ms\n")
            else:
                self.logger.info("[Stage 2/2] Skipping information gathering (quick-answer strategy)\n")
                pipeline_data["stages"]["information_gathering"] = {
                    "status": "skipped",
                    "reason": "quick-answer strategy selected"
                }

            # ========================================
            # Pipeline Complete
            # ========================================
            total_duration = (time.time() - pipeline_start) * 1000

            # Update metrics
            self.pipeline_metrics["total_runs"] += 1
            self.pipeline_metrics["successful_runs"] += 1
            avg = self.pipeline_metrics["average_duration"]
            total = self.pipeline_metrics["total_runs"]
            self.pipeline_metrics["average_duration"] = (avg * (total - 1) + total_duration) / total

            pipeline_data["status"] = "success"
            pipeline_data["total_duration_ms"] = total_duration

            self.logger.info(f"{'='*60}")
            self.logger.info(f"PIPELINE COMPLETE")
            self.logger.info(f"Total Duration: {total_duration:.2f}ms")
            self.logger.info(f"Stages Completed: {len([s for s in pipeline_data['stages'].values() if s['status'] == 'success'])}")
            self.logger.info(f"{'='*60}\n")

            return pipeline_data

        except Exception as e:
            total_duration = (time.time() - pipeline_start) * 1000

            # Update metrics
            self.pipeline_metrics["total_runs"] += 1
            self.pipeline_metrics["failed_runs"] += 1

            self.logger.error(f"Pipeline error: {e}")

            pipeline_data["status"] = "error"
            pipeline_data["error_message"] = str(e)
            pipeline_data["total_duration_ms"] = total_duration

            return pipeline_data

    def run_interactive(self):
        """Run in interactive mode (console)."""
        print("\n" + "="*60)
        print("ResearchMate AI - Orchestrator Mode")
        print("="*60)
        print("\nPipeline: Query Classifier -> Information Gatherer")
        print("\nCommands:")
        print("  - Type your research query")
        print("  - Type 'metrics' to see pipeline metrics")
        print("  - Type 'exit' or 'quit' to stop")
        print("  - Type 'help' for more information")
        print("="*60 + "\n")

        while True:
            try:
                query = input("\n🔍 Enter your research query: ").strip()

                if not query:
                    continue

                if query.lower() in ['exit', 'quit', 'q']:
                    self._show_metrics()
                    print("\n👋 Thank you for using ResearchMate AI!")
                    break

                if query.lower() == 'help':
                    self._show_help()
                    continue

                if query.lower() == 'metrics':
                    self._show_metrics()
                    continue

                # Run research pipeline
                result = asyncio.run(self.research(query))

                # Display results
                print(f"\n{'='*60}")
                print("PIPELINE RESULTS")
                print(f"{'='*60}")
                print(f"Status: {result['status']}")

                if result['status'] == 'success':
                    # Show classification
                    if 'classification' in result['stages']:
                        classification = result['stages']['classification']['output']
                        print(f"\nQuery Classification:")
                        print(f"  Type: {classification.get('query_type', 'N/A')}")
                        print(f"  Complexity: {classification.get('complexity_score', 'N/A')}/10")
                        print(f"  Strategy: {classification.get('research_strategy', 'N/A')}")
                        print(f"  Topics: {', '.join(classification.get('key_topics', []))}")

                    # Show information gathering status
                    if 'information_gathering' in result['stages']:
                        ig_stage = result['stages']['information_gathering']
                        print(f"\nInformation Gathering:")
                        print(f"  Status: {ig_stage['status']}")
                        if ig_stage['status'] == 'success':
                            print(f"  Duration: {ig_stage['duration_ms']:.2f}ms")
                        elif ig_stage['status'] == 'skipped':
                            print(f"  Reason: {ig_stage['reason']}")

                    print(f"\nTotal Duration: {result['total_duration_ms']:.2f}ms")
                else:
                    print(f"\nError: {result.get('error_message', 'Unknown error')}")

                print(f"{'='*60}")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Thank you for using ResearchMate AI!")
                self._show_metrics()
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

    def _show_metrics(self):
        """Display pipeline metrics."""
        print(f"\n{'='*60}")
        print("PIPELINE METRICS")
        print(f"{'='*60}")
        print(f"Total Runs: {self.pipeline_metrics['total_runs']}")
        print(f"Successful: {self.pipeline_metrics['successful_runs']}")
        print(f"Failed: {self.pipeline_metrics['failed_runs']}")
        if self.pipeline_metrics['total_runs'] > 0:
            success_rate = (self.pipeline_metrics['successful_runs'] / self.pipeline_metrics['total_runs']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            print(f"Average Duration: {self.pipeline_metrics['average_duration']:.2f}ms")
        print(f"{'='*60}")

    def _show_help(self):
        """Show help information."""
        help_text = """
        ResearchMate AI - Orchestrator Help
        ====================================

        ResearchMate AI uses a sequential pipeline of specialized agents:

        Pipeline Stages:
        1. Query Classifier - Analyzes query type and determines strategy
        2. Information Gatherer - Searches and retrieves information (conditional)

        Query Types:
        - FACTUAL: Simple fact-based questions
        - COMPARATIVE: Product/service comparisons
        - EXPLORATORY: Learning about topics
        - MONITORING: Tracking developments

        Research Strategies:
        - quick-answer: Single search, immediate response
        - multi-source: 3-5 sources, structured analysis
        - deep-dive: 5-10+ sources, comprehensive research

        Example Queries:
        - "What is the capital of Japan?" (Factual, quick-answer)
        - "Best wireless headphones under $200" (Comparative, multi-source)
        - "Explain quantum computing for beginners" (Exploratory, deep-dive)
        - "Latest developments in AI agents" (Monitoring, multi-source)

        Commands:
        - Type your query to run the pipeline
        - 'metrics' - View pipeline performance metrics
        - 'help' - Show this help
        - 'exit' or 'quit' - Exit the application
        """
        print(help_text)


def main():
    """Main entry point for interactive mode."""
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("  GOOGLE_API_KEY=your_key_here")
        return

    # Create application
    app = ResearchMateAI()

    # Run in interactive mode
    app.run_interactive()


async def test_pipeline():
    """Test the pipeline with sample queries."""
    print("\n" + "="*60)
    print("TESTING RESEARCHMATE AI PIPELINE")
    print("="*60)

    # Create app
    app = ResearchMateAI()

    test_queries = [
        "What is the capital of Japan?",  # Quick answer
        "Best wireless headphones under $200",  # Multi-source
        "Explain quantum computing for beginners",  # Deep dive
    ]

    results = []

    for query in test_queries:
        print(f"\n\nTesting: {query}")
        result = await app.research(query, user_id="test_user")
        results.append(result)

        # Small delay between requests
        await asyncio.sleep(2)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['query']}")
        print(f"   Status: {result['status']}")
        if result['status'] == 'success':
            classification = result['stages']['classification']['output']
            print(f"   Type: {classification.get('query_type')}")
            print(f"   Strategy: {classification.get('research_strategy')}")
            print(f"   Duration: {result['total_duration_ms']:.2f}ms")

    app._show_metrics()
    print("\n✅ Testing Complete!\n")


if __name__ == "__main__":
    import sys

    # Check for test flag
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(test_pipeline())
    else:
        main()
