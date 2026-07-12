"""WebSocket manager for real-time alert broadcasting.

Provides:
- Connection lifecycle management (connect/disconnect)
- Patient-specific subscription filtering
- Broadcast alerts to connected clients
"""

from __future__ import annotations

import logging
from typing import Any

from starlette.websockets import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts alerts in real time.

    Supports per-connection patient_id subscription filtering so that
    clients only receive alerts for the patients they care about.
    """

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []
        # None  → client has never subscribed: firehose (receives every alert).
        # set() → client curated subscriptions: receives only matching patients
        #         (an emptied set therefore receives nothing).
        self._subscriptions: dict[WebSocket, set[str] | None] = {}

    @property
    def active_connections(self) -> int:
        """Number of currently active WebSocket connections."""
        return len(self._connections)

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection and register it.

        .. deprecated::
            This method is deprecated for client-facing connections.
            Use ``WSConnectionManager.connect()`` from ``intensicare.api.v1.ws``
            instead. The legacy ``WebSocketManager`` is now internal-only and
            should only be used via ``broadcast_alert()`` for server-side
            broadcasting (e.g. from vitals ingestion and notification workers).
        """
        import warnings

        warnings.warn(
            "WebSocketManager.connect() is deprecated for client connections. "
            "Use WSConnectionManager (api.v1.ws) instead. "
            "This legacy manager is now internal-only for broadcast_alert().",
            DeprecationWarning,
            stacklevel=2,
        )
        await websocket.accept()
        self._connections.append(websocket)
        self._subscriptions[websocket] = None
        logger.info("WebSocket client connected (total: %d)", len(self._connections))

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection and its subscriptions."""
        if websocket in self._connections:
            self._connections.remove(websocket)
        self._subscriptions.pop(websocket, None)
        logger.info("WebSocket client disconnected (total: %d)", len(self._connections))

    async def subscribe(self, websocket: WebSocket, patient_id: str) -> None:
        """Subscribe a connection to alerts for a specific patient.

        The first subscription switches the client from firehose (None) to a
        curated set, so it thereafter receives only its subscribed patients.
        """
        if websocket in self._subscriptions:
            current = self._subscriptions[websocket]
            if current is None:
                self._subscriptions[websocket] = {patient_id}
            else:
                current.add(patient_id)
            logger.debug("WebSocket subscribed to patient %s", patient_id)

    async def unsubscribe(self, websocket: WebSocket, patient_id: str) -> None:
        """Unsubscribe a connection from alerts for a specific patient."""
        if websocket in self._subscriptions:
            current = self._subscriptions[websocket]
            if current is not None:
                current.discard(patient_id)
            logger.debug("WebSocket unsubscribed from patient %s", patient_id)

    async def broadcast_alert(self, alert_data: dict[str, Any]) -> None:
        """Broadcast an alert to relevant connected clients.

        A client that has never subscribed (None) receives all alerts. Once a
        client has subscribed to any patient, it receives only alerts matching
        its current subscription set (which may be empty → receives nothing).
        """
        disconnected: list[WebSocket] = []

        for ws in self._connections:
            try:
                subscribed_ids = self._subscriptions.get(ws)
                mpi_id = alert_data.get("mpi_id")

                # None → firehose (never subscribed). Otherwise, filter by set.
                if subscribed_ids is None or mpi_id in subscribed_ids:
                    await ws.send_json(alert_data)
            except Exception:
                disconnected.append(ws)

        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws)

    async def send_error(self, websocket: WebSocket, message: str) -> None:
        """Send an error message to a specific WebSocket client."""
        try:
            await websocket.send_json({"type": "error", "message": message})
        except Exception:
            self.disconnect(websocket)


# Module-level singleton holder — matches the Redis/engine pattern.
# Storing the instance as an attribute avoids the `global` statement while
# preserving the exact singleton semantics.
class _ManagerState:
    """Container for the process-wide WebSocket manager singleton."""

    instance: WebSocketManager | None = None


_manager_state = _ManagerState()


def get_websocket_manager() -> WebSocketManager:
    """Get or create the global WebSocket manager singleton."""
    manager = _manager_state.instance
    if manager is None:
        manager = WebSocketManager()
        _manager_state.instance = manager
    return manager


def set_websocket_manager(manager: WebSocketManager) -> None:
    """Set a specific WebSocket manager instance (useful for testing)."""
    _manager_state.instance = manager


def reset_websocket_manager() -> None:
    """Reset the WebSocket manager (useful for testing)."""
    _manager_state.instance = None
