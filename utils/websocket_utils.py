from fastapi import WebSocket
from typing import Dict, List
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage multiple WebSocket connections per session.

    active_connections: Dict[session_id, List[WebSocket]]
    """

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections.setdefault(session_id, []).append(websocket)

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            try:
                del self.active_connections[session_id]
            except KeyError:
                pass

    def disconnect_websocket(self, websocket: WebSocket, session_id: str):
        conns = self.active_connections.get(session_id)
        if not conns:
            return
        try:
            conns.remove(websocket)
            if not conns:
                del self.active_connections[session_id]
        except ValueError:
            pass

    async def send_personal_message(self, message: str, session_id: str):
        """Send a message to all websockets associated with a session.
        Removes dead connections automatically.
        """
        conns = self.active_connections.get(session_id, [])[:]
        for ws in conns:
            try:
                await ws.send_text(message)
            except Exception:
                logger.exception("Failed to send to websocket, removing it")
                try:
                    self.disconnect_websocket(ws, session_id)
                except Exception:
                    pass

    async def send_message_to_all(self, message: str):
        all_conns = []
        for conns in self.active_connections.values():
            all_conns.extend(conns)

        for ws in all_conns:
            try:
                await ws.send_text(message)
            except Exception:
                logger.exception("Failed to broadcast to a websocket")


connection_manager = ConnectionManager()
