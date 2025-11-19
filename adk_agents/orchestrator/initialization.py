"""
Initialization logic for sub-agents, services, and observability.
"""

import sys
from pathlib import Path

from utils.observability import (
    get_logger,
    get_tracer,
    get_metrics,
    get_error_tracker,
)
from services.persistent_session_service import create_persistent_session_service
from services.quality_assurance import QualityAssuranceService

from .config import project_root, orchestrator_sessions_dir

# Initialize observability
logger = get_logger("orchestrator")
tracer = get_tracer()
metrics = get_metrics()
error_tracker = get_error_tracker()

logger.info("Initializing orchestrator agent with A2A integration")

# Load sub-agents
logger.info("Loading sub-agents")

# Add sub-agent paths to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / 'query_classifier'))
from adk_agents.query_classifier.agent import agent as classifier_agent

sys.path.insert(0, str(Path(__file__).parent.parent / 'information_gatherer'))
from adk_agents.information_gatherer.agent import agent as gatherer_agent

sys.path.insert(0, str(Path(__file__).parent.parent / 'content_analyzer'))
from adk_agents.content_analyzer.agent import agent as analyzer_agent

sys.path.insert(0, str(Path(__file__).parent.parent / 'report_generator'))
from adk_agents.report_generator.agent import agent as report_generator_agent

logger.info("All sub-agents loaded successfully")

# Initialize persistent session service for conversation history and user memory
session_service = create_persistent_session_service(orchestrator_sessions_dir)
logger.info("Persistent session service initialized for conversation history")

# Initialize Quality Assurance service
qa_service = QualityAssuranceService()
logger.info("Quality Assurance service initialized for output validation")

# Export all initialized components
__all__ = [
    'logger',
    'tracer',
    'metrics',
    'error_tracker',
    'classifier_agent',
    'gatherer_agent',
    'analyzer_agent',
    'report_generator_agent',
    'session_service',
    'qa_service',
]
