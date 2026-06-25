import socketio
from app.core.config import settings

# Configure Socket.IO Server with Redis message queue
mgr = socketio.AsyncRedisManager(settings.REDIS_URL)
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*", # Adjust in production
    client_manager=mgr
)

# Create an ASGI app to wrap the Socket.IO server
sio_app = socketio.ASGIApp(
    socketio_server=sio,
    socketio_path='/socket.io'
)

@sio.on('connect')
async def connect(sid, environ, auth):
    """
    Handle client connection.
    In production, validate JWT from auth dict here.
    """
    print(f"Client connected: {sid}")
    # Example auth check
    # if not auth or 'token' not in auth:
    #     raise ConnectionRefusedError('Authentication failed')
    return True

@sio.on('disconnect')
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

# Register all namespaces
from app.websockets.interview_namespace import register_namespaces
register_namespaces(sio)
