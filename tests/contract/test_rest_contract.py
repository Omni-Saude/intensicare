"""Contract tests for IntensiCare REST API."""

import yaml


def test_openapi_yaml_is_valid():
    """OpenAPI spec must be valid YAML and parse successfully."""
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)

    assert spec["openapi"] == "3.1.0", f"Expected OpenAPI 3.1.0, got {spec.get('openapi')}"
    assert "info" in spec, "Missing 'info' section"
    assert spec["info"]["title"] == "IntensiCare v2 API"
    assert "paths" in spec, "Missing 'paths' section"


def test_openapi_has_alerts_path():
    """The /alerts endpoint must be defined."""
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)

    assert "/alerts" in spec["paths"], "Missing /alerts path"
    alerts_get = spec["paths"]["/alerts"]["get"]
    assert alerts_get["operationId"] == "listAlerts"

    # Response schema must be {data: [...], meta: {...}} per spec
    resp200 = alerts_get["responses"]["200"]
    schema = resp200["content"]["application/json"]["schema"]
    assert schema["type"] == "object", "GET /alerts response must be an object"
    assert "data" in schema.get("properties", {}), "Response must have 'data' property"
    assert "meta" in schema.get("properties", {}), "Response must have 'meta' property"


def test_openapi_has_lifecycle_endpoints():
    """All alert lifecycle endpoints must be defined."""
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)

    lifecycle_endpoints = [
        "/alerts/{alertId}/acknowledge",
        "/alerts/{alertId}/act",
        "/alerts/{alertId}/resolve",
        "/alerts/{alertId}/escalate",
    ]

    for endpoint in lifecycle_endpoints:
        assert endpoint in spec["paths"], f"Missing lifecycle endpoint: {endpoint}"
        assert "post" in spec["paths"][endpoint], f"{endpoint} must be POST"
        assert "200" in spec["paths"][endpoint]["post"]["responses"], (
            f"{endpoint} must have 200 response"
        )


def test_alert_response_contract():
    """Alert response schema must match the OpenAPI Alert schema."""
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)

    alert_schema = spec["components"]["schemas"]["Alert"]

    # The spec's "required" uses inline comma-separated strings (e.g.
    # "- id, mpi_id, alert_definition_id, ..."), which YAML treats as
    # single strings. Expand them to a flat set.
    raw_required = alert_schema.get("required", [])
    required_fields: set[str] = set()
    for item in raw_required:
        for raw_field in item.split(","):
            field = raw_field.strip()
            if field:
                required_fields.add(field)

    # Ensure the spec defines the properties our API serves
    # Note: the API uses "title" while the spec Alert schema uses "name";
    # both represent the same semantic field. The spec is richer than our
    # current DB model — we validate what we do serve.
    props = set(alert_schema.get("properties", {}).keys())
    api_fields = {
        "id",
        "mpi_id",
        "score_id",
        "severity",
        "status",
        "body",
        "created_at",
        "acknowledged_at",
        "acknowledged_by",
        "resolved_at",
        "resolution",
    }
    missing_from_props = api_fields - props
    assert not missing_from_props, f"API fields missing from spec properties: {missing_from_props}"

    # title/name is present (spec calls it "name")
    assert "name" in props, "Spec Alert must have 'name' field (API uses 'title')"

    # Core fields must be in the required list
    core_required = {"id", "mpi_id", "severity", "status", "created_at"}
    missing_core = core_required - required_fields
    assert not missing_core, f"Core Alert fields missing from spec required: {missing_core}"


def test_severity_enum():
    """Severity must use the canonical clinical.* four-band scale."""
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)

    severity = spec["components"]["schemas"]["Severity"]
    assert severity["type"] == "string"
    assert set(severity["enum"]) == {"normal", "watch", "urgent", "critical"}, (
        f"Severity enum mismatch: {severity['enum']}"
    )


def test_alert_status_enum():
    """AlertStatus must cover the full lifecycle."""
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)

    alert_status = spec["components"]["schemas"]["AlertStatus"]
    assert set(alert_status["enum"]) == {
        "raised",
        "acknowledged",
        "acting",
        "resolved",
        "escalated",
        "expired",
    }, f"AlertStatus enum mismatch: {alert_status['enum']}"


def test_resolution_enum():
    """Resolution must support the three clinical outcomes."""
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)

    resolution = spec["components"]["schemas"]["Resolution"]
    assert set(resolution["enum"]) == {"true_positive", "false_positive", "intervention_done"}, (
        f"Resolution enum mismatch: {resolution['enum']}"
    )


def test_error_envelope_schema():
    """Error envelope must include trace_id for observability."""
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)

    envelope = spec["components"]["schemas"]["ErrorEnvelope"]
    error_obj = envelope["properties"]["error"]
    required = set(error_obj["required"])
    assert "trace_id" in required, "Error must include trace_id"
    assert "timestamp" in required, "Error must include timestamp"
    assert "code" in required, "Error must include code"


def test_cursor_page_meta():
    """CursorPageMeta must have all fields for pagination."""
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)

    meta = spec["components"]["schemas"]["CursorPageMeta"]
    props = set(meta["properties"].keys())
    assert props >= {"limit", "has_more"}, "CursorPageMeta missing core fields"


def test_auth_flow():
    """Auth endpoints must be defined for login, refresh, logout, and me."""
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)

    auth_paths = ["/auth/login", "/auth/refresh", "/auth/logout", "/auth/me"]
    for path in auth_paths:
        assert path in spec["paths"], f"Missing auth path: {path}"


def test_security_scheme():
    """bearerAuth must be the defined security scheme."""
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        spec = yaml.safe_load(f)

    schemes = spec.get("components", {}).get("securitySchemes", {})
    assert "bearerAuth" in schemes, "Missing bearerAuth security scheme"
    assert schemes["bearerAuth"]["type"] == "http"
    assert schemes["bearerAuth"]["scheme"] == "bearer"
    assert schemes["bearerAuth"]["bearerFormat"] == "JWT"
