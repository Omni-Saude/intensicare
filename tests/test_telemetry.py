"""
Tests for OpenTelemetry instrumentation (telemetry.py).

Covers:
  - init_telemetry does not double-initialise
  - get_tracer returns a tracer (or NoOp when OTEL not installed)
  - get_current_trace_id returns None when no span is active
  - format_trace_id formatting
  - _NoOpTracer and _NoOpSpan behaviour
  - trace_stage context manager creates spans
  - is_telemetry_available reports initialisation state
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

from intensicare.core.telemetry import (
    _NoOpSpan,
    _NoOpTracer,
    _telemetry_state,
    format_trace_id,
    get_current_trace_id,
    get_tracer,
    init_telemetry,
    is_telemetry_available,
    trace_stage,
)

# ─── Helpers to fake the OTEL SDK being importable ───────────────────────────
#
# telemetry.py imports `opentelemetry.*` lazily *inside* functions (never at
# module scope), so `trace`, `TracerProvider`, etc. are not attributes of
# `intensicare.core.telemetry` and cannot be patched with
# `patch("intensicare.core.telemetry.<name>", ...)`. To simulate the "OTEL
# SDK is installed" path, inject fake modules directly into `sys.modules`
# (via `patch.dict`) for every dotted path telemetry.py imports from — this
# is the "OTEL is available" counterpart to the "OTEL is not installed"
# tests below (which patch `builtins.__import__` to raise `ImportError`).


def _fake_otel_modules(*, trace_module: MagicMock | None = None) -> dict[str, MagicMock]:
    """Build a sys.modules mapping that satisfies telemetry.py's lazy imports."""
    top_level = trace_module if trace_module is not None else MagicMock()

    resources_module = MagicMock()
    resources_module.SERVICE_NAME = "service.name"
    resources_module.Resource = MagicMock()

    sdk_trace_module = MagicMock()
    sdk_trace_module.TracerProvider = MagicMock()

    return {
        "opentelemetry": MagicMock(trace=top_level),
        "opentelemetry.exporter": MagicMock(),
        "opentelemetry.exporter.otlp": MagicMock(),
        "opentelemetry.exporter.otlp.proto": MagicMock(),
        "opentelemetry.exporter.otlp.proto.http": MagicMock(),
        "opentelemetry.exporter.otlp.proto.http.trace_exporter": MagicMock(
            OTLPSpanExporter=MagicMock()
        ),
        "opentelemetry.sdk": MagicMock(),
        "opentelemetry.sdk.resources": resources_module,
        "opentelemetry.sdk.trace": sdk_trace_module,
        "opentelemetry.sdk.trace.export": MagicMock(BatchSpanProcessor=MagicMock()),
        "opentelemetry.sdk.trace.sampling": MagicMock(ALWAYS_ON=MagicMock()),
    }

# ─── Fixture to guard global state ───────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_telemetry_state():
    """Reset the global _telemetry_state before and after each test."""
    original = _telemetry_state.initialized
    _telemetry_state.initialized = False
    _telemetry_state.tracer_provider = None
    _telemetry_state.meter_provider = None
    _telemetry_state.tracer = None
    yield
    _telemetry_state.initialized = original


# ─── get_tracer tests ───────────────────────────────────────────────────────


class TestGetTracer:
    """Tests for get_tracer()."""

    def test_returns_noop_when_otel_not_installed(self):
        """When opentelemetry is not importable, get_tracer returns NoOpTracer."""
        # get_tracer() imports `opentelemetry.trace` lazily inside the
        # function body, so simulate "SDK not installed" by making the
        # import itself fail rather than patching a module attribute that
        # doesn't exist.
        with patch(
            "builtins.__import__",
            side_effect=ImportError("No OTEL"),
        ):
            tracer = get_tracer()
            assert isinstance(tracer, _NoOpTracer)


# ─── NoOp helpers ───────────────────────────────────────────────────────────


class TestNoOpSpan:
    """Tests for the _NoOpSpan fallback."""

    def test_span_context_manager(self):
        span = _NoOpSpan()
        with span:
            span.set_attribute("key", "value")
        # Should not raise

    def test_set_status_noop(self):
        span = _NoOpSpan()
        span.set_status(1, "OK")  # Should not raise

    def test_record_exception_noop(self):
        span = _NoOpSpan()
        span.record_exception()  # Should not raise


class TestNoOpTracer:
    """Tests for the _NoOpTracer fallback."""

    def test_start_as_current_span_returns_noop(self):
        tracer = _NoOpTracer()
        span = tracer.start_as_current_span("test-op")
        assert isinstance(span, _NoOpSpan)


# ─── get_current_trace_id tests ──────────────────────────────────────────────


class TestGetCurrentTraceID:
    """Tests for get_current_trace_id()."""

    def test_returns_none_when_no_span(self):
        """When no span is active, return None."""
        # Without OTEL initialised, tracer returns NoOp, so get_current_trace_id
        # should return None (since OTEL is not importable).
        with patch(
            "builtins.__import__",
            side_effect=ImportError("No OTEL"),
        ):
            trace_id = get_current_trace_id()
            assert trace_id is None

    def test_returns_formatted_trace_id_when_active(self):
        """When a span is active, return a 32-char hex string."""
        mock_span = MagicMock()
        mock_span_context = MagicMock()
        mock_span_context.is_valid = True
        mock_span_context.trace_id = 12345678901234567890
        mock_span.get_span_context.return_value = mock_span_context

        mock_trace = MagicMock()
        mock_trace.get_current_span.return_value = mock_span

        # get_current_trace_id() does `from opentelemetry import trace`
        # lazily inside the function, so inject a fake `opentelemetry`
        # module into sys.modules rather than patching a (nonexistent)
        # module-level attribute.
        with patch.dict(sys.modules, {"opentelemetry": MagicMock(trace=mock_trace)}):
            trace_id = get_current_trace_id()
            assert trace_id is not None
            assert len(trace_id) == 32
            assert int(trace_id, 16) == 12345678901234567890


# ─── format_trace_id tests ────────────────────────────────────────────────────


class TestFormatTraceID:
    """Tests for format_trace_id()."""

    def test_formats_as_32_char_hex(self):
        result = format_trace_id(42)
        assert result == "0000000000000000000000000000002a"
        assert len(result) == 32

    def test_formats_large_id(self):
        result = format_trace_id(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
        assert len(result) == 32
        assert result == "ffffffffffffffffffffffffffffffff"


# ─── init_telemetry tests ────────────────────────────────────────────────────


class TestInitTelemetry:
    """Tests for init_telemetry()."""

    def test_double_init_is_idempotent(self):
        """Calling init_telemetry twice should log and return early."""
        _telemetry_state.initialized = True

        with patch("intensicare.core.telemetry.logger") as mock_logger:
            init_telemetry()
            mock_logger.info.assert_called_once()
            assert "já inicializada" in mock_logger.info.call_args[0][0].lower()

    def test_init_sets_initialized_flag(self):
        """After init_telemetry, _telemetry_state.initialized should be True."""
        _telemetry_state.initialized = False

        # Simulate success path. All of init_telemetry's OTEL imports
        # (trace, TracerProvider, OTLPSpanExporter, ...) are local imports
        # inside the function body, so they must be faked via sys.modules
        # rather than via `patch("intensicare.core.telemetry.<name>", ...)`
        # (those names are not module-level attributes). `_auto_instrument`
        # *is* a real module-level attribute, so it's still patched directly.
        with (
            patch.dict(sys.modules, _fake_otel_modules()),
            patch(
                "intensicare.core.telemetry._auto_instrument",
            ),
        ):
            init_telemetry(traces_enabled=True, metrics_enabled=False)
            assert _telemetry_state.initialized is True

    def test_init_handles_import_error_gracefully(self):
        """When OTEL SDK is not installed, init_telemetry logs a warning."""
        _telemetry_state.initialized = False

        # Simulate ImportError at the top of init_telemetry try block
        with (
            patch("intensicare.core.telemetry.logger") as mock_logger,
            patch("builtins.__import__", side_effect=ImportError("No OTEL SDK")),
        ):
            init_telemetry()
            # Even on failure, initialized is set to True to avoid retry
            assert _telemetry_state.initialized is True
            # Should have logged a warning
            mock_logger.warning.assert_called()


# ─── trace_stage context manager ─────────────────────────────────────────────


class TestTraceStage:
    """Tests for the trace_stage context manager."""

    def test_successful_stage(self):
        """A successful stage should yield the span without errors."""
        with (
            patch(
                "intensicare.core.telemetry.get_tracer",
                return_value=_NoOpTracer(),
            ),
            trace_stage("poll_nrt", unit_id="ICU-1", tenant_id="t01"),
        ):
            # Just verify it doesn't crash
            pass

    def test_exception_in_stage_is_re_raised(self):
        """An exception inside the stage should be re-raised."""
        with (
            patch(
                "intensicare.core.telemetry.get_tracer",
                return_value=_NoOpTracer(),
            ),
            pytest.raises(ValueError, match="test error"),
            trace_stage("evaluate"),
        ):
            raise ValueError("test error")

    def test_stage_with_all_attributes(self):
        """All optional attributes should be handled."""
        with (
            patch(
                "intensicare.core.telemetry.get_tracer",
                return_value=_NoOpTracer(),
            ),
            trace_stage(
                "deliver",
                attributes={"custom": "value"},
                evaluation_mode="micro_batch",
                tenant_id="t02",
                unit_id="ICU-2",
                alert_definition_id="alert-001",
            ),
        ):
            pass


# ─── is_telemetry_available tests ────────────────────────────────────────────


class TestIsTelemetryAvailable:
    """Tests for is_telemetry_available()."""

    def test_returns_false_when_not_initialized(self):
        _telemetry_state.initialized = False
        assert is_telemetry_available() is False

    def test_returns_true_when_initialized(self):
        _telemetry_state.initialized = True
        assert is_telemetry_available() is True
