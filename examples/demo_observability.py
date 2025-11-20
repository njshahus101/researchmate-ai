"""
Quick Demo: Observability System in Action

This script demonstrates the observability system by:
1. Running some tracked operations
2. Displaying the metrics dashboard
3. Showing how to view logs
"""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.observability import (
    get_logger, get_tracer, get_metrics, get_error_tracker,
    track_operation
)
from utils.observability_dashboard import display_metrics

def demo_operations():
    """Run some example operations to generate observability data"""
    print("\n" + "="*80)
    print("RUNNING DEMO OPERATIONS...")
    print("="*80 + "\n")

    logger = get_logger("demo_agent")
    tracer = get_tracer()
    metrics = get_metrics()

    # Simulate pipeline start
    metrics.increment_counter("pipeline_start_total", labels={"user_id": "demo_user"})
    logger.info("Demo pipeline started", user_id="demo_user", query="test query")

    # Operation 1: Successful operation
    with track_operation("demo_agent", "fetch_data", {"source": "api"}):
        logger.info("Fetching data from API")
        time.sleep(0.1)  # Simulate work
        logger.info("Data fetched successfully", record_count=42)

    # Operation 2: Another successful operation
    with track_operation("demo_agent", "process_data", {"records": 42}):
        logger.info("Processing records")
        time.sleep(0.05)  # Simulate work
        logger.info("Processing complete")

    # Operation 3: Simulated error
    try:
        with track_operation("demo_agent", "risky_operation", {"attempt": 1}):
            logger.warning("Attempting risky operation")
            raise ValueError("Demo error - this is intentional for testing")
    except ValueError:
        logger.error("Operation failed as expected")

    # Add some metrics
    metrics.record_histogram("query_processing_time_seconds", 2.3,
                            labels={"status": "success"})
    metrics.record_histogram("query_processing_time_seconds", 1.8,
                            labels={"status": "success"})
    metrics.record_histogram("query_processing_time_seconds", 4.2,
                            labels={"status": "success"})

    metrics.set_gauge("active_queries", 3)
    metrics.increment_counter("total_queries", labels={"source": "web_ui"})

    print("\n" + "="*80)
    print("DEMO OPERATIONS COMPLETE - Generated logs, traces, and metrics")
    print("="*80 + "\n")

def show_log_files():
    """Display information about log files"""
    print("\n" + "="*80)
    print("LOG FILES LOCATION")
    print("="*80 + "\n")

    log_file = Path("logs/researchmate.log")
    error_file = Path("logs/errors.json")

    if log_file.exists():
        line_count = len(log_file.read_text(encoding='utf-8').strip().split('\n'))
        print(f"[OK] Application logs: logs/researchmate.log ({line_count} entries)")
        print(f"     View with: type logs\\researchmate.log")

    if error_file.exists():
        error_count = len([l for l in error_file.read_text(encoding='utf-8').strip().split('\n') if l.strip()])
        print(f"[OK] Error logs: logs/errors.json ({error_count} errors)")
        print(f"     View with: type logs\\errors.json")

    print()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("OBSERVABILITY SYSTEM DEMONSTRATION")
    print("="*80)

    # Run demo operations to generate data
    demo_operations()

    # Show where logs are stored
    show_log_files()

    # Display the dashboard with metrics from operations we just ran
    print("="*80)
    print("METRICS DASHBOARD (from operations above)")
    print("="*80 + "\n")
    display_metrics()

    print("\n" + "="*80)
    print("DEMO COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("1. View logs: type logs\\researchmate.log")
    print("2. View errors: type logs\\errors.json")
    print("3. Run full test: python test_observability_end_to_end.py")
    print("4. Check the testing guide: OBSERVABILITY_TESTING_GUIDE.md")
    print()
