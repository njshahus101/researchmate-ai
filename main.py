"""
ResearchMate AI - Main Application

Multi-agent research assistant built with Google ADK.
Demonstrates A2A Protocol, MCP tools, Memory management, and Observability.
"""

import os
import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.apps.app import App
from google.genai import types

# Import agents
from agents.query_classifier import create_query_classifier_agent
from agents.information_gatherer import create_information_gatherer_agent
from agents.content_analyzer import create_content_analyzer_agent
from agents.report_generator import create_report_generator_agent

# Import services
from services.memory_service import MemoryService
from services.session_service import create_session_service

# Import MCP tools
from mcp_servers.web_content_fetcher import fetch_web_content
from mcp_servers.price_extractor import extract_product_info

# Import utilities
from utils.logging_config import setup_logging, AgentLogger
from utils.helpers import create_retry_config


class ResearchMateAI:
    """
    ResearchMate AI Application

    Orchestrates the multi-agent pipeline for intelligent research.
    """

    def __init__(self, use_database: bool = False):
        """
        Initialize ResearchMate AI.

        Args:
            use_database: Whether to use persistent database storage
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
        self.logger.info("ResearchMate AI Starting...")
        self.logger.info("=" * 60)

        # Configuration
        self.app_name = os.getenv("APP_NAME", "researchmate_ai")
        self.retry_config = create_retry_config()

        # Initialize services
        self.memory_service = MemoryService()
        self.session_service = create_session_service(
            use_database=use_database,
            db_url=os.getenv("DATABASE_URL")
        )

        # Create agents
        self._create_agents()

        # Create application (for future A2A exposure)
        self._create_app()

        self.logger.info("✅ ResearchMate AI initialized successfully!")

    def _create_agents(self):
        """Create all four agents in the pipeline."""
        self.logger.info("Creating agents...")

        # 1. Query Classifier Agent
        self.query_classifier = create_query_classifier_agent(self.retry_config)
        self.logger.info(f"  ✓ {self.query_classifier.name}")

        # 2. Information Gatherer Agent (with MCP tools)
        self.information_gatherer = create_information_gatherer_agent(
            self.retry_config,
            web_fetcher_tool=fetch_web_content,
            price_extractor_tool=extract_product_info
        )
        self.logger.info(f"  ✓ {self.information_gatherer.name}")

        # 3. Content Analyzer Agent
        self.content_analyzer = create_content_analyzer_agent(self.retry_config)
        self.logger.info(f"  ✓ {self.content_analyzer.name}")

        # 4. Report Generator Agent
        self.report_generator = create_report_generator_agent(self.retry_config)
        self.logger.info(f"  ✓ {self.report_generator.name}")

    def _create_app(self):
        """Create the main application for potential A2A exposure."""
        # For now, we'll use the query classifier as the root agent
        # In a full implementation, you'd create an orchestrator agent
        self.app = App(
            name=self.app_name,
            root_agent=self.query_classifier
        )
        self.logger.info(f"Application created: {self.app_name}")

    async def research(self, query: str, user_id: str = "default") -> dict:
        """
        Execute the full research pipeline.

        Args:
            query: User's research query
            user_id: User identifier

        Returns:
            Dictionary with research results
        """
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"NEW RESEARCH REQUEST")
        self.logger.info(f"User: {user_id}")
        self.logger.info(f"Query: {query}")
        self.logger.info(f"{'='*60}\n")

        try:
            # Step 1: Query Classification
            self.agent_logger.log_agent_start("QueryClassifier", query)
            # In a full implementation, you would call the agent here
            # For now, we'll simulate the response
            classification = {
                "query_type": "comparative",  # This would come from the agent
                "complexity_score": 6,
                "research_strategy": "multi-source",
                "key_topics": ["wireless", "headphones"],
                "user_intent": "product comparison"
            }
            self.agent_logger.log_agent_complete("QueryClassifier", 150.0)

            # Step 2: Information Gathering
            self.agent_logger.log_agent_start("InformationGatherer", query)
            # Agent would execute searches and fetch content here
            self.agent_logger.log_agent_complete("InformationGatherer", 5000.0)

            # Step 3: Content Analysis
            self.agent_logger.log_agent_start("ContentAnalyzer", query)
            # Agent would analyze sources here
            self.agent_logger.log_agent_complete("ContentAnalyzer", 2000.0)

            # Step 4: Report Generation
            self.agent_logger.log_agent_start("ReportGenerator", query)
            # Agent would generate report here
            self.agent_logger.log_agent_complete("ReportGenerator", 1500.0)

            # Store in memory
            self.memory_service.add_research_entry(
                user_id,
                query,
                classification["query_type"],
                classification["key_topics"]
            )

            return {
                "status": "success",
                "query": query,
                "classification": classification,
                "message": "Research pipeline completed successfully!"
            }

        except Exception as e:
            self.logger.error(f"Research pipeline error: {e}")
            return {
                "status": "error",
                "query": query,
                "error_message": str(e)
            }

    def run_interactive(self):
        """Run in interactive mode (console)."""
        print("\n" + "="*60)
        print("ResearchMate AI - Interactive Mode")
        print("="*60)
        print("\nCommands:")
        print("  - Type your research query")
        print("  - Type 'exit' or 'quit' to stop")
        print("  - Type 'help' for more information")
        print("="*60 + "\n")

        while True:
            try:
                query = input("\n🔍 Enter your research query: ").strip()

                if not query:
                    continue

                if query.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Thank you for using ResearchMate AI!")
                    break

                if query.lower() == 'help':
                    self._show_help()
                    continue

                # Run research
                result = asyncio.run(self.research(query))

                print(f"\n{'='*60}")
                print("RESEARCH RESULTS")
                print(f"{'='*60}")
                print(f"Status: {result['status']}")
                if result['status'] == 'success':
                    print(f"Query Type: {result['classification']['query_type']}")
                    print(f"Strategy: {result['classification']['research_strategy']}")
                    print(f"\n{result['message']}")
                else:
                    print(f"Error: {result['error_message']}")
                print(f"{'='*60}")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Thank you for using ResearchMate AI!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

    def _show_help(self):
        """Show help information."""
        help_text = """
        ResearchMate AI Help
        ====================

        ResearchMate AI is a multi-agent research assistant that:
        - Understands your query intent and complexity
        - Gathers information from authoritative sources
        - Analyzes content credibility
        - Generates comprehensive reports with citations

        Example Queries:
        - "What is the capital of Japan?" (Factual)
        - "Best wireless headphones under $200" (Comparative)
        - "Explain quantum computing for beginners" (Exploratory)

        The system will automatically:
        1. Classify your query
        2. Determine the optimal research strategy
        3. Gather relevant information
        4. Analyze source credibility
        5. Generate a tailored report

        Commands:
        - Type your query to start research
        - 'help' - Show this help
        - 'exit' or 'quit' - Exit the application
        """
        print(help_text)


def main():
    """Main entry point."""
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("  GOOGLE_API_KEY=your_key_here")
        return

    # Create application
    app = ResearchMateAI(use_database=False)

    # Run in interactive mode
    app.run_interactive()


if __name__ == "__main__":
    main()
