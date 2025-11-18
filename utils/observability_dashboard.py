"""
Observability Dashboard - Terminal-based metrics viewer

Displays real-time observability metrics for ResearchMate AI:
- Pipeline execution metrics
- Agent performance stats
- Error summary
- Recent activity

Usage:
    python utils/observability_dashboard.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def format_duration(seconds):
    """Format duration in human-readable form."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        mins = int(seconds / 60)
        secs = seconds % 60
        return f"{mins}m {secs:.0f}s"

def format_number(num):
    """Format large numbers with commas."""
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"

def print_header(title):
    """Print a formatted section header."""
    width = 80
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)

def print_metric_row(label, value, unit=""):
    """Print a formatted metric row."""
    print(f"  {label:.<50} {value}{unit}")

def display_metrics():
    """Display all observability metrics."""
    try:
        # Try to load metrics from the global instance
        from utils.observability import get_metrics, get_error_tracker

        metrics = get_metrics()
        error_tracker = get_error_tracker()

        # Get all metrics
        all_metrics = metrics.get_all_metrics()

        print_header("RESEARCHMATE AI - OBSERVABILITY DASHBOARD")
        print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Pipeline Overview
        print_header("Pipeline Metrics")

        pipeline_starts = metrics.get_counter("pipeline_start_total")
        if pipeline_starts > 0:
            print_metric_row("Total Pipeline Executions", pipeline_starts)
        else:
            print_metric_row("Total Pipeline Executions", 0)
            print("  (No pipeline executions yet)")

        # Operation Metrics
        print_header("Operation Performance")

        histograms = all_metrics.get("histograms", {})
        if histograms:
            for metric_name, stats in histograms.items():
                if stats and "count" in stats:
                    print(f"\n  {metric_name}:")
                    print_metric_row("  Count", stats["count"])
                    print_metric_row("  Average", format_duration(stats["avg"]))
                    print_metric_row("  Min", format_duration(stats["min"]))
                    print_metric_row("  Max", format_duration(stats["max"]))
                    print_metric_row("  P50 (median)", format_duration(stats["p50"]))
                    print_metric_row("  P95", format_duration(stats["p95"]))
                    if stats["count"] > 100:
                        print_metric_row("  P99", format_duration(stats["p99"]))
        else:
            print("  (No operation metrics yet)")

        # Success/Error Rates
        print_header("Success & Error Rates")

        counters = all_metrics.get("counters", {})

        # Calculate success rate
        total_success = 0
        total_errors = 0

        for key, value in counters.items():
            if "success" in key:
                total_success += value
            elif "error" in key:
                total_errors += value

        if total_success > 0 or total_errors > 0:
            total_ops = total_success + total_errors
            success_rate = (total_success / total_ops * 100) if total_ops > 0 else 0

            print_metric_row("Successful Operations", total_success)
            print_metric_row("Failed Operations", total_errors)
            print_metric_row("Success Rate", f"{success_rate:.1f}%")
        else:
            print("  (No operations completed yet)")

        # Detailed Error Breakdown
        if total_errors > 0:
            print("\n  Error Breakdown:")
            for key, value in counters.items():
                if "error" in key and value > 0:
                    print_metric_row(f"    {key}", value)

        # Error Tracker Summary
        print_header("Error Tracking")

        error_summary = error_tracker.get_error_summary()
        total_errors_tracked = error_summary.get("total_errors", 0)

        if total_errors_tracked > 0:
            print_metric_row("Total Errors Tracked", total_errors_tracked)

            # Errors by agent
            by_agent = error_summary.get("by_agent", {})
            if by_agent:
                print("\n  Errors by Agent:")
                for agent, count in sorted(by_agent.items(), key=lambda x: x[1], reverse=True):
                    print_metric_row(f"    {agent}", count)

            # Errors by type
            by_type = error_summary.get("by_type", {})
            if by_type:
                print("\n  Errors by Type:")
                for error_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                    print_metric_row(f"    {error_type}", count)

            # Recent errors
            recent = error_summary.get("recent_errors", [])
            if recent:
                print("\n  Recent Errors (last 5):")
                for i, error in enumerate(recent[-5:], 1):
                    print(f"\n    [{i}] {error.get('error_type')}: {error.get('error_message', '')[:60]}")
                    print(f"        Agent: {error.get('agent')}")
                    print(f"        Time: {error.get('timestamp')}")
        else:
            print("  (No errors tracked - system healthy!)")

        # Gauges
        print_header("Current State")

        gauges = all_metrics.get("gauges", {})
        if gauges:
            for key, value in gauges.items():
                print_metric_row(key, format_number(value))
        else:
            print("  (No gauge metrics yet)")

        # Footer
        print_header("Dashboard Summary")
        print("  Observability System Status: ACTIVE")
        print("  Components:")
        print("    - Structured Logging: ENABLED")
        print("    - Distributed Tracing: ENABLED")
        print("    - Metrics Collection: ENABLED")
        print("    - Error Tracking: ENABLED")
        print("\n  Log Files:")
        print("    - Application logs: logs/researchmate.log")
        print("    - Error logs: logs/errors.json")
        print("\n" + "=" * 80 + "\n")

    except Exception as e:
        print(f"[ERROR] Failed to display metrics: {e}")
        print("Make sure the observability system is initialized.")
        import traceback
        traceback.print_exc()

def export_metrics_report(output_file="observability_report.json"):
    """Export metrics to JSON file for analysis."""
    try:
        from utils.observability import get_metrics, get_error_tracker

        metrics = get_metrics()
        error_tracker = get_error_tracker()

        report = {
            "generated_at": datetime.now().isoformat(),
            "metrics": metrics.get_all_metrics(),
            "errors": error_tracker.get_error_summary()
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"[OK] Metrics report exported to {output_file}")
        return output_file

    except Exception as e:
        print(f"[ERROR] Failed to export metrics: {e}")
        return None

if __name__ == "__main__":
    import sys

    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--export":
        output_file = sys.argv[2] if len(sys.argv) > 2 else "observability_report.json"
        export_metrics_report(output_file)
    else:
        display_metrics()

        # Offer to export
        print("\nTo export metrics to JSON: python utils/observability_dashboard.py --export [filename]")
