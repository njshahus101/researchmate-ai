"""
End-to-End Observability Test

Tests the complete observability system:
1. Initializes all components
2. Simulates agent operations
3. Records metrics, traces, and errors
4. Displays dashboard
5. Exports metrics report
"""

import asyncio
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.observability import (
    get_logger,
    get_tracer,
    get_metrics,
    get_error_tracker,
    track_operation
)

def test_logging():
    """Test structured logging."""
    print("\n[TEST 1/5] Testing Structured Logging...")

    logger = get_logger("test_orchestrator")

    logger.info("Test pipeline started", query="test query", user_id="test_user")
    logger.debug("Processing step 1", step="classification")
    logger.warning("Simulated warning", retry_count=1)

    print("[OK] Structured logging test complete")

def test_tracing():
    """Test distributed tracing."""
    print("\n[TEST 2/5] Testing Distributed Tracing...")

    tracer = get_tracer()

    with tracer.trace_span("test_pipeline", {"test": "value"}):
        time.sleep(0.1)

        with tracer.trace_span("test_step_1", {"step": "classify"}):
            time.sleep(0.05)

        with tracer.trace_span("test_step_2", {"step": "fetch"}):
            time.sleep(0.05)

    print("[OK] Distributed tracing test complete")

def test_metrics():
    """Test metrics collection."""
    print("\n[TEST 3/5] Testing Metrics Collection...")

    metrics = get_metrics()

    # Record some test metrics
    metrics.increment_counter("pipeline_start_total", labels={"user_id": "test"})
    metrics.record_histogram("operation_duration_seconds", 0.5, labels={"agent": "orchestrator", "operation": "test"})
    metrics.record_histogram("operation_duration_seconds", 0.3, labels={"agent": "orchestrator", "operation": "test"})
    metrics.record_histogram("operation_duration_seconds", 0.7, labels={"agent": "orchestrator", "operation": "test"})

    metrics.increment_counter("operation_success_total", labels={"agent": "classifier", "operation": "classify"})
    metrics.increment_counter("operation_success_total", labels={"agent": "classifier", "operation": "classify"})

    metrics.set_gauge("active_queries", 5.0)

    print("[OK] Metrics collection test complete")

def test_error_tracking():
    """Test error tracking."""
    print("\n[TEST 4/5] Testing Error Tracking...")

    error_tracker = get_error_tracker()

    # Simulate some errors
    try:
        raise ValueError("Test error 1")
    except Exception as e:
        error_tracker.track_error("test_agent", e, {"query": "test query 1"})

    try:
        raise ConnectionError("Test error 2")
    except Exception as e:
        error_tracker.track_error("test_agent", e, {"query": "test query 2"})

    print("[OK] Error tracking test complete")

def test_track_operation():
    """Test the track_operation convenience function."""
    print("\n[TEST 5/5] Testing track_operation Convenience Function...")

    # Test successful operation
    with track_operation("test_agent", "successful_operation", {"param": "value1"}):
        time.sleep(0.1)

    # Test failed operation
    try:
        with track_operation("test_agent", "failed_operation", {"param": "value2"}):
            time.sleep(0.05)
            raise RuntimeError("Intentional test error")
    except RuntimeError:
        pass  # Expected

    print("[OK] track_operation test complete")

def display_test_dashboard():
    """Display observability dashboard with test data."""
    print("\n" + "="*80)
    print("  DISPLAYING OBSERVABILITY DASHBOARD")
    print("="*80)

    # Import and run dashboard
    from utils.observability_dashboard import display_metrics
    display_metrics()

def export_test_report():
    """Export metrics report."""
    print("\n[EXPORT] Generating observability report...")

    from utils.observability_dashboard import export_metrics_report
    export_metrics_report("test_observability_report.json")

def main():
    """Run all observability tests."""
    print("="*80)
    print("  RESEARCHMATE AI - END-TO-END OBSERVABILITY TEST")
    print("="*80)

    try:
        # Run tests in sequence
        test_logging()
        test_tracing()
        test_metrics()
        test_error_tracking()
        test_track_operation()

        # Display dashboard
        display_test_dashboard()

        # Export report
        export_test_report()

        print("\n" + "="*80)
        print("  ALL OBSERVABILITY TESTS PASSED!")
        print("="*80)

        print("\nObservability System Summary:")
        print("  - Structured Logging: WORKING")
        print("  - Distributed Tracing: WORKING")
        print("  - Metrics Collection: WORKING")
        print("  - Error Tracking: WORKING")
        print("  - Dashboard: WORKING")
        print("  - Export: WORKING")

        print("\nNext Steps:")
        print("  1. Check logs at: logs/researchmate.log")
        print("  2. Check errors at: logs/errors.json")
        print("  3. Check report at: test_observability_report.json")
        print("  4. Run actual research query to see full pipeline observability")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Observability test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
