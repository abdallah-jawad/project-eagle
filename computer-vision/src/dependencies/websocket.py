import asyncio
import websockets
import json
import base64
import cv2
import numpy as np
from typing import Set, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        """Initialize WebSocket server
        
        Args:
            host: Host address to bind to
            port: Port number to listen on
        """
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.camera_streams: Dict[str, asyncio.Queue] = {}
        
    async def start(self):
        """Start the WebSocket server"""
        async with websockets.serve(self._handle_client, self.host, self.port):
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever
            
    async def _handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle new client connections
        
        Args:
            websocket: WebSocket connection
            path: Request path
        """
        self.clients.add(websocket)
        try:
            async for message in websocket:
                # Handle client messages (e.g., subscribe to specific camera)
                data = json.loads(message)
                if data.get("type") == "subscribe":
                    camera_id = data.get("camera_id")
                    if camera_id not in self.camera_streams:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "Camera ID does not exist"
                        }))
                        return
                    # Send acknowledgment
                    await websocket.send(json.dumps({
                        "type": "subscribed",
                        "camera_id": camera_id
                    }))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            
    async def broadcast_frame(self, camera_id: str, frame):
        """Broadcast frame to all subscribed clients
        
        Args:
            camera_id: ID of the camera
            frame: OpenCV frame to broadcast
        """
        current_time = datetime.now().timestamp()
        
        # Convert frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = base64.b64encode(buffer).decode('utf-8')
        
        # Create message
        message = json.dumps({
            "type": "frame",
            "camera_id": camera_id,
            "frame": frame_bytes,
            "timestamp": current_time
        })
        
        # Broadcast to all clients
        websockets_to_remove = set()
        for websocket in self.clients:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                websockets_to_remove.add(websocket)
                
        # Remove disconnected clients
        self.clients -= websockets_to_remove
