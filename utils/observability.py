"""
Observability Module for ResearchMate AI

Provides comprehensive observability infrastructure:
- Structured logging with context
- Distributed tracing with OpenTelemetry
- Metrics collection and aggregation
- Error tracking and analysis

This module enables full visibility into the multi-agent research pipeline.
"""

import logging
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import contextmanager
from collections import defaultdict
import threading

# Try to import OpenTelemetry (optional dependency)
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    print("[WARN] OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk")


class StructuredLogger:
    """
    Structured logger that outputs JSON logs with context.

    Replaces print() statements with structured logging that includes:
    - Timestamp
    - Log level
    - Agent name
    - Query/session IDs
    - Contextual data
    - Trace ID
    """

    def __init__(self, name: str, log_file: Optional[str] = "logs/researchmate.log"):
        """
        Initialize structured logger.

        Args:
            name: Logger name (typically agent name)
            log_file: Path to log file (None for console only)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if not self.logger.handlers:
            # Console handler with JSON format
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(console_handler)

            # File handler if specified
            if log_file:
                import os
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(JSONFormatter())
                self.logger.addHandler(file_handler)

    def _log(self, level: str, message: str, **context):
        """Internal logging method with context."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "agent": self.name,
            "message": message,
        }

        # Add context
        if context:
            log_data["context"] = context

        # Add trace ID if available
        if OTEL_AVAILABLE:
            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                log_data["trace_id"] = format(span.get_span_context().trace_id, '032x')
                log_data["span_id"] = format(span.get_span_context().span_id, '016x')

        # Log at appropriate level
        getattr(self.logger, level.lower())(json.dumps(log_data))

    def debug(self, message: str, **context):
        """Log debug message with context."""
        self._log("DEBUG", message, **context)

    def info(self, message: str, **context):
        """Log info message with context."""
        self._log("INFO", message, **context)

    def warning(self, message: str, **context):
        """Log warning message with context."""
        self._log("WARNING", message, **context)

    def error(self, message: str, **context):
        """Log error message with context."""
        self._log("ERROR", message, **context)

    def critical(self, message: str, **context):
        """Log critical message with context."""
        self._log("CRITICAL", message, **context)


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON."""

    def format(self, record):
        # The message is already JSON from StructuredLogger
        return record.getMessage()


class DistributedTracer:
    """
    Distributed tracing for multi-agent pipeline using OpenTelemetry.

    Tracks request flow through agents with parent-child span relationships.
    Measures latency at each step and captures contextual attributes.
    """

    def __init__(self, service_name: str = "researchmate-ai"):
        """
        Initialize distributed tracer.

        Args:
            service_name: Name of the service for tracing
        """
        self.service_name = service_name
        self.tracer = None

        if OTEL_AVAILABLE:
            # Create a tracer provider with resource
            resource = Resource.create({"service.name": service_name})
            provider = TracerProvider(resource=resource)

            # Add console exporter (can be replaced with OTLP exporter for production)
            processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)

            # Set as global default
            trace.set_tracer_provider(provider)

            # Get tracer instance
            self.tracer = trace.get_tracer(__name__)

            print(f"[OK] Distributed tracing initialized for {service_name}")
        else:
            print(f"[WARN] OpenTelemetry not available - tracing disabled")

    @contextmanager
    def trace_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Create a traced span as context manager.

        Usage:
            with tracer.trace_span("fetch_content", {"url_count": 5}):
                # ... do work ...
                pass

        Args:
            name: Span name
            attributes: Optional attributes to attach to span
        """
        if self.tracer and OTEL_AVAILABLE:
            with self.tracer.start_as_current_span(name) as span:
                # Add attributes
                if attributes:
                    for key, value in attributes.items():
                        # Convert value to string for OpenTelemetry
                        span.set_attribute(key, str(value))

                try:
                    yield span
                except Exception as e:
                    # Record exception in span
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise
        else:
            # No-op context manager if tracing disabled
            yield None

    def get_trace_id(self) -> Optional[str]:
        """Get current trace ID."""
        if OTEL_AVAILABLE:
            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                return format(span.get_span_context().trace_id, '032x')
        return None


class MetricsCollector:
    """
    Metrics collection and aggregation.

    Collects performance metrics, success rates, and business metrics.
    Provides methods to record, query, and export metrics.
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.lock = threading.Lock()

        print("[OK] Metrics collector initialized")

    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Record a histogram metric (for distributions like latency).

        Args:
            name: Metric name
            value: Metric value
            labels: Optional labels (e.g., {"agent": "orchestrator"})
        """
        with self.lock:
            key = self._make_key(name, labels)
            self.metrics[key].append({
                "timestamp": time.time(),
                "value": value
            })

    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric.

        Args:
            name: Metric name
            value: Increment value (default 1)
            labels: Optional labels
        """
        with self.lock:
            key = self._make_key(name, labels)
            self.counters[key] += value

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric (for current values).

        Args:
            name: Metric name
            value: Current value
            labels: Optional labels
        """
        with self.lock:
            key = self._make_key(name, labels)
            self.gauges[key] = value

    def get_histogram_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """
        Get statistics for a histogram metric.

        Returns:
            Dictionary with min, max, avg, p50, p95, p99
        """
        with self.lock:
            key = self._make_key(name, labels)
            values = [m["value"] for m in self.metrics.get(key, [])]

            if not values:
                return {}

            sorted_values = sorted(values)
            n = len(sorted_values)

            return {
                "count": n,
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / n,
                "p50": sorted_values[int(n * 0.5)],
                "p95": sorted_values[int(n * 0.95)] if n > 20 else sorted_values[-1],
                "p99": sorted_values[int(n * 0.99)] if n > 100 else sorted_values[-1],
            }

    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> int:
        """Get counter value."""
        with self.lock:
            key = self._make_key(name, labels)
            return self.counters.get(key, 0)

    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value."""
        with self.lock:
            key = self._make_key(name, labels)
            return self.gauges.get(key, 0.0)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as a dictionary."""
        with self.lock:
            return {
                "histograms": {k: self.get_histogram_stats(*self._parse_key(k)) for k in self.metrics.keys()},
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

    def export_json(self, filepath: str):
        """Export metrics to JSON file."""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(self.get_all_metrics(), f, indent=2)

        print(f"[OK] Metrics exported to {filepath}")

    @staticmethod
    def _make_key(name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create metric key from name and labels."""
        if labels:
            label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}{{{label_str}}}"
        return name

    @staticmethod
    def _parse_key(key: str) -> tuple:
        """Parse metric key back to name and labels."""
        if "{" in key:
            name, label_str = key.split("{", 1)
            label_str = label_str.rstrip("}")
            labels = dict(pair.split("=") for pair in label_str.split(","))
            return name, labels
        return key, None


class ErrorTracker:
    """
    Error tracking and failure analysis.

    Captures exceptions with full context for debugging and analysis.
    """

    def __init__(self, log_file: str = "logs/errors.json"):
        """Initialize error tracker."""
        self.log_file = log_file
        self.errors = []
        self.lock = threading.Lock()

        import os
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        print(f"[OK] Error tracker initialized (log: {log_file})")

    def track_error(
        self,
        agent: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Track an error with context.

        Args:
            agent: Agent name where error occurred
            error: The exception
            context: Additional context (query, step, etc.)
        """
        error_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent": agent,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }

        # Add trace ID if available
        if OTEL_AVAILABLE:
            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                error_data["trace_id"] = format(span.get_span_context().trace_id, '032x')

        with self.lock:
            self.errors.append(error_data)

            # Write to file
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(error_data) + "\n")

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics."""
        with self.lock:
            if not self.errors:
                return {"total_errors": 0}

            # Count by agent
            by_agent = defaultdict(int)
            by_type = defaultdict(int)

            for error in self.errors:
                by_agent[error["agent"]] += 1
                by_type[error["error_type"]] += 1

            return {
                "total_errors": len(self.errors),
                "by_agent": dict(by_agent),
                "by_type": dict(by_type),
                "recent_errors": self.errors[-10:]  # Last 10 errors
            }


# Global singleton instances
_logger_instances = {}
_tracer_instance = None
_metrics_instance = None
_error_tracker_instance = None


def get_logger(name: str) -> StructuredLogger:
    """Get or create a structured logger instance."""
    global _logger_instances
    if name not in _logger_instances:
        _logger_instances[name] = StructuredLogger(name)
    return _logger_instances[name]


def get_tracer() -> DistributedTracer:
    """Get or create the global tracer instance."""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = DistributedTracer()
    return _tracer_instance


def get_metrics() -> MetricsCollector:
    """Get or create the global metrics collector instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
    return _metrics_instance


def get_error_tracker() -> ErrorTracker:
    """Get or create the global error tracker instance."""
    global _error_tracker_instance
    if _error_tracker_instance is None:
        _error_tracker_instance = ErrorTracker()
    return _error_tracker_instance


# Convenience context manager for tracking agent operations
@contextmanager
def track_operation(
    agent_name: str,
    operation_name: str,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Context manager for tracking a complete operation with logging, tracing, and metrics.

    Usage:
        with track_operation("orchestrator", "fetch_content", {"url_count": 5}):
            # ... do work ...
            pass

    Args:
        agent_name: Name of the agent
        operation_name: Name of the operation
        attributes: Optional attributes for context
    """
    logger = get_logger(agent_name)
    tracer = get_tracer()
    metrics = get_metrics()
    error_tracker = get_error_tracker()

    # Log start
    logger.info(f"Starting {operation_name}", **(attributes or {}))

    # Start timing
    start_time = time.time()

    # Start trace span
    with tracer.trace_span(f"{agent_name}.{operation_name}", attributes):
        try:
            yield

            # Log success
            duration = time.time() - start_time
            logger.info(
                f"Completed {operation_name}",
                duration_seconds=duration,
                **(attributes or {})
            )

            # Record metrics
            metrics.record_histogram(
                "operation_duration_seconds",
                duration,
                labels={"agent": agent_name, "operation": operation_name}
            )
            metrics.increment_counter(
                "operation_success_total",
                labels={"agent": agent_name, "operation": operation_name}
            )

        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                f"Failed {operation_name}",
                error=str(e),
                error_type=type(e).__name__,
                duration_seconds=duration,
                **(attributes or {})
            )

            # Track error
            error_tracker.track_error(agent_name, e, {
                "operation": operation_name,
                **(attributes or {})
            })

            # Record failure metric
            metrics.increment_counter(
                "operation_error_total",
                labels={"agent": agent_name, "operation": operation_name, "error_type": type(e).__name__}
            )

            raise


if __name__ == "__main__":
    # Test the observability system
    print("Testing Observability System\n")

    # Test structured logging
    logger = get_logger("test_agent")
    logger.info("Starting test", query="test query", user_id="test123")
    logger.warning("This is a warning", retry_count=3)
    logger.error("This is an error", error_type="TestError")

    # Test tracing
    tracer = get_tracer()
    with tracer.trace_span("test_operation", {"test": "value"}):
        time.sleep(0.1)
        logger.info("Inside trace span")

    # Test metrics
    metrics = get_metrics()
    metrics.record_histogram("test_duration", 0.5, {"agent": "test"})
    metrics.increment_counter("test_requests", labels={"agent": "test"})
    metrics.set_gauge("test_queue_size", 10.0)

    print("\n[METRICS] Summary:")
    print(json.dumps(metrics.get_all_metrics(), indent=2))

    # Test error tracking
    error_tracker = get_error_tracker()
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_tracker.track_error("test_agent", e, {"query": "test"})

    print("\n[ERRORS] Summary:")
    print(json.dumps(error_tracker.get_error_summary(), indent=2))

    # Test track_operation convenience function
    print("\n[TEST] Testing track_operation:")
    with track_operation("test_agent", "complete_test", {"param": "value"}):
        time.sleep(0.05)

    print("\n[OK] Observability system test complete!")
