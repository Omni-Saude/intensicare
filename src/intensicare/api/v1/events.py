"""SSE (Server-Sent Events) endpoint — fallback quando WebSocket não está disponível.

Endpoint: ``/api/v1/events/stream?token=<JWT>``

Compartilha o mesmo mecanismo de broadcasting do WebSocket.
Cada conexão SSE recebe uma ``asyncio.Queue`` registrada num registry global;
quando o ``WSConnectionManager.publish()`` dispara um evento, ele é enfileirado
para todos os listeners SSE ativos.

Event types publicados (mesmos canais do WS):
  - alert.raised
  - alert.updated
  - bed_grid.updated
  - presence.updated
  - vitals.updated

Formato SSE (por evento):
  event: <channel>
  data: {"type":"<channel>","payload":{...},"timestamp":"<iso8601>"}
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
import logging

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse

from intensicare.auth.jwt import decode_token

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Shared SSE listener registry
# ---------------------------------------------------------------------------

_sse_listeners: list[asyncio.Queue] = []


def get_sse_registry() -> list[asyncio.Queue]:
    """Retorna a lista global de filas dos listeners SSE ativos.

    É chamada pelo ``WSConnectionManager.publish()`` (via lazy import)
    para replicar cada evento publicado para os clientes SSE.
    """
    return _sse_listeners


# ---------------------------------------------------------------------------
# SSE endpoint
# ---------------------------------------------------------------------------


@router.get("/api/v1/events/stream")
async def events_stream(
    request: Request,
    token: str = Query(..., description="JWT access token"),
):
    """SSE fallback — mantém conexão HTTP aberta e transmite eventos em tempo real.

    Autentica via JWT no query parameter, depois entra em loop lendo de uma
    ``asyncio.Queue`` registrada no registry global. Envia heartbeat (comentário
    SSE) a cada 30 s para evitar que proxies fechem a conexão.
    """
    # 1. Autenticar token JWT
    payload = decode_token(token)
    if payload is None:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or expired token"},
        )

    username: str = payload.get("sub", "unknown")
    logger.info("SSE connected: user=%s", username)

    # 2. Criar fila por conexão
    queue: asyncio.Queue = asyncio.Queue()

    # 3. Registrar no registry global
    _sse_listeners.append(queue)

    async def event_generator():
        """Generator assíncrono que produz frames SSE."""
        try:
            # Enviar evento inicial de conexão bem-sucedida
            connected_event = {
                "type": "connected",
                "payload": {"user": username},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            yield f"event: connected\ndata: {json.dumps(connected_event)}\n\n"

            while True:
                # Aguarda eventos com timeout para keepalive (heartbeat)
                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=30.0)
                except asyncio.TimeoutError:
                    # Heartbeat: comentário SSE mantém a conexão viva
                    yield ": heartbeat\n\n"
                    continue

                # Sentinel de desconexão (None)
                if event_data is None:
                    break

                channel: str = event_data.get("channel", "unknown")
                data: dict = event_data.get("data", {})

                # Formato esperado pelo frontend (RealtimeEvent em websocket.ts)
                sse_event = {
                    "type": channel,
                    "payload": data,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

                json_data = json.dumps(sse_event)
                yield f"event: {channel}\ndata: {json_data}\n\n"

        except asyncio.CancelledError:
            logger.info("SSE connection cancelled for user=%s", username)
        except Exception:
            logger.exception("SSE stream error for user=%s", username)
        finally:
            # 5. Remover do registry ao desconectar
            if queue in _sse_listeners:
                _sse_listeners.remove(queue)
            logger.info("SSE disconnected: user=%s", username)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Desabilita buffering do nginx
        },
    )
