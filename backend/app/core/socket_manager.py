import socketio
from typing import Any
import logging

logger = logging.getLogger(__name__)

class SocketManager:
    def __init__(self):
        # Configure Redis Manager for external emission support (e.g. from Celery)
        # Using redis://localhost:6379/0 as default
        mgr = socketio.AsyncRedisManager('redis://localhost:6379/0')
        
        self.sio = socketio.AsyncServer(
            client_manager=mgr,
            async_mode='asgi',
            cors_allowed_origins='*',
            # Performance & stability settings
            max_http_buffer_size=1e6,  # 1MB max message size
            ping_interval=25,  # Ping every 25 seconds
            ping_timeout=60,  # Disconnect if no pong after 60s
            logger=False,  # Disable Socket.IO debug logging (use our logger)
            engineio_logger=False
        )
        self.app = socketio.ASGIApp(self.sio)
        
        # Connection tracking
        self.active_connections = 0
        self.max_connections = 10000  # Prevent DoS

    async def emit(self, event: str, data: Any, room: str = None):
        """
        Emit an event to all clients or a specific room.
        """
        try:
            await self.sio.emit(event, data, room=room)
        except Exception as e:
            logger.error(f"Socket emit error: {e}")

    async def connect(self, sid, environ):
        self.active_connections += 1
        if self.active_connections > self.max_connections:
            logger.warning(f"Max connections ({self.max_connections}) reached. Rejecting {sid}")
            return False  # Reject connection
        logger.info(f"Client connected: {sid} (Total: {self.active_connections})")
        return True

    async def disconnect(self, sid):
        self.active_connections = max(0, self.active_connections - 1)
        logger.info(f"Client disconnected: {sid} (Total: {self.active_connections})")

socket_manager = SocketManager()

@socket_manager.sio.on('connect')
async def handle_connect(sid, environ):
    return await socket_manager.connect(sid, environ)

@socket_manager.sio.on('disconnect')
async def handle_disconnect(sid):
    await socket_manager.disconnect(sid)

@socket_manager.sio.event
async def join_job_room(sid, job_id):
    """
    Client joins a specific job room to listen for updates.
    """
    logger.info(f"Client {sid} joined room {job_id}")
    await socket_manager.sio.enter_room(sid, job_id)
