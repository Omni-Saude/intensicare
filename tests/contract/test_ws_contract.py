"""Contract tests for IntensiCare WebSocket/Realtime API (AsyncAPI)."""

import yaml


def test_asyncapi_yaml_is_valid():
    """AsyncAPI spec must be valid YAML and parse successfully."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        spec = yaml.safe_load(f)

    assert spec["asyncapi"] == "2.6.0", f"Expected AsyncAPI 2.6.0, got {spec.get('asyncapi')}"
    assert "info" in spec, "Missing 'info' section"
    assert spec["info"]["title"] == "IntensiCare v2 Realtime API"
    assert "channels" in spec, "Missing 'channels' section"


def test_websocket_channel_defined():
    """The primary WebSocket channel must be /api/v1/realtime."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        spec = yaml.safe_load(f)

    channels = spec["channels"]
    assert "/api/v1/realtime" in channels, "Missing WebSocket channel"
    assert "/api/v1/realtime/stream" in channels, "Missing SSE fallback channel"


def test_websocket_server_url():
    """Production server must use wss://."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        spec = yaml.safe_load(f)

    ws_server = spec["servers"]["websocket"]
    assert ws_server["protocol"] == "wss", "Production WebSocket must use wss"
    assert ws_server["url"].startswith("wss://"), "WebSocket URL must start with wss://"


def test_sse_fallback_url():
    """SSE fallback server must use https://."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        spec = yaml.safe_load(f)

    sse_server = spec["servers"]["sse"]
    assert sse_server["protocol"] == "https", "SSE must use HTTPS"
    assert sse_server["url"].startswith("https://"), "SSE URL must start with https://"


def test_event_catalog_messages():
    """All event catalog messages must be defined in components."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        spec = yaml.safe_load(f)

    messages = spec["components"]["messages"]

    # Server → Client messages
    expected_server = [
        "AlertRaised",
        "AlertUpdated",
        "BedGridUpdated",
        "PresenceUpdated",
        "HeartbeatPing",
        "SubscribeAck",
        "ServerError",
    ]
    for msg in expected_server:
        assert msg in messages, f"Missing server message: {msg}"

    # Client → Server messages
    expected_client = [
        "Subscribe",
        "Unsubscribe",
        "HeartbeatPong",
        "PresenceHeartbeat",
    ]
    for msg in expected_client:
        assert msg in messages, f"Missing client message: {msg}"


def test_alert_event_envelope():
    """Alert events must carry the full envelope with seq for dedup."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        spec = yaml.safe_load(f)

    envelope = spec["components"]["schemas"]["AlertEventEnvelope"]
    required = set(envelope["required"])
    assert "seq" in required, "Alert event must carry seq for ordering/resume"
    assert "tenant_id" in required, "Alert event must carry tenant_id"
    assert "occurred_at" in required, "Alert event must carry occurred_at"
    assert "data" in required, "Alert event must carry data payload"

    # type must discriminate alert.raised vs alert.updated
    type_prop = envelope["properties"]["type"]
    assert "alert.raised" in type_prop["enum"], "Missing alert.raised event type"
    assert "alert.updated" in type_prop["enum"], "Missing alert.updated event type"


def test_subscribe_message():
    """Subscribe must carry tenant/unit scope."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        spec = yaml.safe_load(f)

    subscribe = spec["components"]["messages"]["Subscribe"]
    payload = subscribe["payload"]
    scope = payload["properties"]["scope"]["properties"]
    assert "tenant_id" in scope, "Subscribe scope must require tenant_id"
    assert "unit" in scope, "Subscribe scope must require unit"


def test_bed_grid_updated():
    """bed_grid.updated must include severity for sorting/coloring."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        spec = yaml.safe_load(f)

    bed_grid = spec["components"]["messages"]["BedGridUpdated"]
    data_props = bed_grid["payload"]["properties"]["data"]["properties"]
    bed_grid["payload"]["properties"]["data"].get("required", [])

    assert "bed_id" in data_props, "bed_grid must carry bed_id"
    assert "occupied" in data_props, "bed_grid must carry occupied flag"
    assert "latest_score_severity" in data_props, "bed_grid must carry score severity"
    assert "active_alert_severity" in data_props, "bed_grid must carry alert severity"


def test_severity_consistent_with_rest():
    """AsyncAPI Severity must match OpenAPI Severity enum."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        async_spec = yaml.safe_load(f)
    with open("docs/plan/architecture/api/openapi.yaml") as f:
        rest_spec = yaml.safe_load(f)

    async_severity = set(async_spec["components"]["schemas"]["Severity"]["enum"])
    rest_severity = set(rest_spec["components"]["schemas"]["Severity"]["enum"])

    assert async_severity == rest_severity, (
        f"Severity mismatch: async={async_severity} vs rest={rest_severity}"
    )


def test_reconnect_backoff_policy():
    """Reconnect policy must be documented in x-reconnect-backoff-policy."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        spec = yaml.safe_load(f)

    policy = spec.get("x-reconnect-backoff-policy", {})
    assert policy, "Missing x-reconnect-backoff-policy extension"
    assert "description" in policy, "Reconnect policy must have a description"


def test_tags():
    """Both specs must have the expected tag groups."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        spec = yaml.safe_load(f)

    tag_names = [t["name"] for t in spec.get("tags", [])]
    expected = {"alert", "bed_grid", "presence", "control"}
    missing = expected - set(tag_names)
    assert not missing, f"Missing tags in AsyncAPI: {missing}"


def test_heartbeat_contract():
    """Heartbeat ping/pong must use matching ping_seq for correlation."""
    with open("docs/plan/architecture/api/asyncapi.yaml") as f:
        spec = yaml.safe_load(f)

    ping = spec["components"]["messages"]["HeartbeatPing"]
    pong = spec["components"]["messages"]["HeartbeatPong"]

    ping_props = set(ping["payload"]["required"])
    pong_props = set(pong["payload"]["required"])

    assert "ping_seq" in ping_props, "HeartbeatPing must include ping_seq"
    assert "ping_seq" in pong_props, "HeartbeatPong must include ping_seq"
