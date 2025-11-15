"""
Logging Configuration

Sets up comprehensive logging and observability infrastructure for ResearchMate AI.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file in addition to console
        log_dir: Directory for log files

    Returns:
        Configured logger instance
    """

    # Create logger
    logger = logging.getLogger("researchmate_ai")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_to_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"researchmate_{timestamp}.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info(f"Logging to file: {log_file}")

    logger.info(f"Logging initialized at {log_level} level")

    return logger


class AgentLogger:
    """
    Specialized logger for tracking agent actions and decisions.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initialize agent logger.

        Args:
            logger: Base logger instance
        """
        self.logger = logger

    def log_agent_start(self, agent_name: str, query: str):
        """Log when an agent starts processing."""
        self.logger.info(f"[{agent_name}] Starting - Query: {query}")

    def log_agent_complete(self, agent_name: str, duration_ms: float):
        """Log when an agent completes."""
        self.logger.info(f"[{agent_name}] Completed in {duration_ms:.2f}ms")

    def log_tool_call(self, agent_name: str, tool_name: str, args: dict):
        """Log when an agent calls a tool."""
        self.logger.debug(f"[{agent_name}] Calling tool: {tool_name} with args: {args}")

    def log_tool_result(self, agent_name: str, tool_name: str, success: bool):
        """Log tool execution result."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"[{agent_name}] Tool {tool_name}: {status}")

    def log_decision(self, agent_name: str, decision: str, reasoning: str):
        """Log an agent's decision and reasoning."""
        self.logger.info(f"[{agent_name}] Decision: {decision}")
        self.logger.debug(f"[{agent_name}] Reasoning: {reasoning}")

    def log_error(self, agent_name: str, error: str):
        """Log an agent error."""
        self.logger.error(f"[{agent_name}] Error: {error}")


if __name__ == "__main__":
    # Test logging setup
    logger = setup_logging(log_level="DEBUG", log_to_file=False)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    # Test agent logger
    agent_logger = AgentLogger(logger)

    agent_logger.log_agent_start("QueryClassifier", "Best wireless headphones")
    agent_logger.log_tool_call("QueryClassifier", "get_user_preferences", {"user_id": "123"})
    agent_logger.log_tool_result("QueryClassifier", "get_user_preferences", True)
    agent_logger.log_decision("QueryClassifier", "Route to multi-source", "Comparative query detected")
    agent_logger.log_agent_complete("QueryClassifier", 125.5)

    print("\n✅ Logging test completed!")
