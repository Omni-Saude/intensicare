"""WebSocket endpoint — real-time event streaming with JWT auth.

Endpoint: ``/api/v1/ws?token=<JWT>``

Event types published:
  - alert.raised       — when new alert created
  - alert.updated      — when alert status changes (acknowledged/resolved/escalated)
  - bed_grid.updated   — when bed status changes
  - presence.updated   — when user presence changes
  - vitals.updated     — when new vital signs ingested

Features:
  - JWT token authentication via query parameter
  - Room/channel-based subscription (clients subscribe to event types)
  - Heartbeat ping/pong every 30s
  - Auto-disconnect stale connections after 60s of inactivity
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from starlette.websockets import WebSocketState

from intensicare.auth.jwt import decode_token
from intensicare.core.websocket import get_websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Connection manager with channel/room support, heartbeat, and staleness
# ---------------------------------------------------------------------------


class ChannelConnection:
    """Wraps a single WebSocket with per-connection state."""

    __slots__ = ("ws", "user", "channels", "last_pong", "last_activity")

    def __init__(self, ws: WebSocket, user: str) -> None:
        self.ws: WebSocket = ws
        self.user: str = user
        self.channels: set[str] = set()  # which event types this client listens to
        self.last_pong: float = time.monotonic()
        self.last_activity: float = time.monotonic()


class WSConnectionManager:
    """Manages WebSocket connections with channel/room support.

    Clients subscribe to named channels (event types). When an event is
    published on a channel, only subscribed clients receive it.

    Implements:
      - Heartbeat ping every 30s; expects pong within 10s.
      - Stale connection cleanup: disconnects clients silent for > 60s.
    """

    HEARTBEAT_INTERVAL = 30  # seconds between server pings
    PONG_TIMEOUT = 10        # seconds to wait for pong after ping
    STALE_TIMEOUT = 60       # seconds without any activity before disconnect

    def __init__(self) -> None:
        self._connections: dict[WebSocket, ChannelConnection] = {}
        self._heartbeat_task: asyncio.Task[None] | None = None

    # ---- connection lifecycle ------------------------------------------------

    async def connect(self, ws: WebSocket, user: str) -> None:
        """Accept and register a new connection."""
        await ws.accept()
        conn = ChannelConnection(ws, user)
        self._connections[ws] = conn
        logger.info(
            "WS connected: user=%s total=%d", user, len(self._connections)
        )
        # Start heartbeat loop if this is the first connection.
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    def disconnect(self, ws: WebSocket) -> None:
        """Remove a connection."""
        if ws in self._connections:
            conn = self._connections.pop(ws)
            logger.info(
                "WS disconnected: user=%s total=%d",
                conn.user,
                len(self._connections),
            )
        # Cancel heartbeat loop if no connections remain.
        if not self._connections and self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None

    # ---- channel subscription -----------------------------------------------

    def subscribe(self, ws: WebSocket, channel: str) -> None:
        """Subscribe a connection to a named channel."""
        conn = self._connections.get(ws)
        if conn is not None:
            conn.channels.add(channel)
            conn.last_activity = time.monotonic()
            logger.debug("WS subscribed to channel '%s'", channel)

    def unsubscribe(self, ws: WebSocket, channel: str) -> None:
        """Unsubscribe a connection from a named channel."""
        conn = self._connections.get(ws)
        if conn is not None:
            conn.channels.discard(channel)
            conn.last_activity = time.monotonic()
            logger.debug("WS unsubscribed from channel '%s'", channel)

    # ---- publishing ---------------------------------------------------------

    async def publish(self, channel: str, data: dict[str, Any]) -> None:
        """Publish an event to all connections subscribed to *channel*."""
        disconnected: list[WebSocket] = []
        payload = {"type": channel, "data": data}

        for ws, conn in list(self._connections.items()):
            # Broadcast to clients listening to this channel, or to clients
            # with no channel filter (empty set = firehose / all channels).
            if channel in conn.channels or not conn.channels:
                try:
                    await ws.send_json(payload)
                    conn.last_activity = time.monotonic()
                except Exception:
                    disconnected.append(ws)

        for ws in disconnected:
            self.disconnect(ws)

        # ---- Broadcast to SSE listeners (shared event bus) ----
        self._broadcast_to_sse(channel, data)

    @staticmethod
    def _broadcast_to_sse(channel: str, data: dict[str, Any]) -> None:
        """Push event to all registered SSE listener queues.

        Uses a lazy import to avoid circular dependency at module-load time.
        The ``asyncio.Queue`` default maxsize is 0 (unbounded), so
        ``put_nowait`` never raises ``QueueFull``.
        """
        try:
            from intensicare.api.v1.events import get_sse_registry  # lazy
        except ImportError:
            return

        listeners = get_sse_registry()
        if not listeners:
            return

        event = {"channel": channel, "data": data}
        for q in listeners[:]:  # iterate over a shallow copy
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass  # defensive — shouldn't happen with unbounded queues

    async def send_to_connection(self, ws: WebSocket, payload: dict[str, Any]) -> None:
        """Send a message to a single connection."""
        try:
            await ws.send_json(payload)
            if ws in self._connections:
                self._connections[ws].last_activity = time.monotonic()
        except Exception:
            self.disconnect(ws)

    # ---- heartbeat loop -----------------------------------------------------

    async def _heartbeat_loop(self) -> None:
        """Background task that pings every HEARTBEAT_INTERVAL seconds."""
        while self._connections:
            await asyncio.sleep(self.HEARTBEAT_INTERVAL)

            now = time.monotonic()
            disconnected: list[WebSocket] = []

            for ws, conn in list(self._connections.items()):
                # Check staleness: auto-disconnect if no activity for STALE_TIMEOUT.
                if now - conn.last_activity > self.STALE_TIMEOUT:
                    disconnected.append(ws)
                    continue

                # Send ping and check pong response.
                # If last_pong is older than HEARTBEAT_INTERVAL + PONG_TIMEOUT,
                # the client missed a heartbeat — disconnect.
                if now - conn.last_pong > self.HEARTBEAT_INTERVAL + self.PONG_TIMEOUT:
                    disconnected.append(ws)
                    continue

                try:
                    if ws.application_state == WebSocketState.CONNECTED:
                        await ws.send_json({"type": "ping"})
                except Exception:
                    disconnected.append(ws)

            for ws in disconnected:
                self.disconnect(ws)


# ---------------------------------------------------------------------------
# Singleton holder
# ---------------------------------------------------------------------------


class _WSManagerState:
    """Container for the process-wide channel-aware WS manager singleton."""

    instance: WSConnectionManager | None = None


_ws_manager_state = _WSManagerState()


def get_ws_manager() -> WSConnectionManager:
    """Get or create the global channel-aware WebSocket manager."""
    manager = _ws_manager_state.instance
    if manager is None:
        manager = WSConnectionManager()
        _ws_manager_state.instance = manager
    return manager


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------


@router.websocket("/api/v1/ws")
async def websocket_endpoint(
    ws: WebSocket,
    token: str = Query(..., description="JWT access token"),
) -> None:
    """Real-time event stream for the Intensicare frontend.

    Authenticates via JWT token in the query string, then enters a persistent
    event loop that handles:
      - Client → server: subscribe/unsubscribe messages, pong responses.
      - Server → client: heartbeat pings, event broadcasts.

    Client message protocol (JSON):
      {"action": "subscribe",   "channel": "<event_type>"}
      {"action": "unsubscribe", "channel": "<event_type>"}
      {"action": "pong"}

    Server message protocol (JSON):
      {"type": "ping"}
      {"type": "alert.raised",       "data": {...}}
      {"type": "alert.updated",      "data": {...}}
      {"type": "bed_grid.updated",   "data": {...}}
      {"type": "presence.updated",   "data": {...}}
      {"type": "vitals.updated",     "data": {...}}
      {"type": "error",              "message": "..."}
    """
    # ---- Authenticate -------------------------------------------------------
    payload = decode_token(token)
    if payload is None:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    username: str | None = payload.get("sub")
    if username is None:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # ---- Register connection ------------------------------------------------
    manager = get_ws_manager()
    await manager.connect(ws, user=username)

    # ---- Also register with the legacy broadcast manager
    # (so vitals ingestion, etc. can reach WS clients).
    legacy = get_websocket_manager()
    await legacy.connect(ws)

    try:
        while True:
            # Receive client messages (subscribe, unsubscribe, pong).
            try:
                raw = await asyncio.wait_for(ws.receive_text(), timeout=5.0)
            except asyncio.TimeoutError:
                # No message received — loop again (heartbeat handles staleness).
                continue

            data: dict[str, Any]
            try:
                data = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                await manager.send_to_connection(
                    ws, {"type": "error", "message": "Invalid JSON"}
                )
                continue

            action = data.get("action", "").strip().lower()
            channel = data.get("channel", "").strip().lower()

            if action == "subscribe" and channel:
                manager.subscribe(ws, channel)
            elif action == "unsubscribe" and channel:
                manager.unsubscribe(ws, channel)
            elif action == "pong":
                # Update the last_pong timestamp.
                conn = manager._connections.get(ws)
                if conn is not None:
                    conn.last_pong = time.monotonic()
            else:
                await manager.send_to_connection(
                    ws,
                    {
                        "type": "error",
                        "message": "Unknown action. Use: subscribe, unsubscribe, pong.",
                    },
                )

    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket error for user=%s", username)
    finally:
        legacy.disconnect(ws)
        manager.disconnect(ws)
        try:
            await ws.close()
        except Exception:
            pass
