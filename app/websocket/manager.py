from typing import List, Dict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        if username not in self.active_connections:
            self.active_connections[username] = [websocket]
        else:
            self.active_connections[username].append(websocket)

    def disconnect(self, websocket: WebSocket, username: str):
        self.active_connections[username].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_order_data(self, order_data: dict, websocket: WebSocket):
        await websocket.send_json(order_data)

    async def broadcast(self, message: str, username: str):
        if username in self.active_connections:
            for connection in self.active_connections[username]:
                await self.send_personal_message(message, connection)

    async def broadcast_order(self, order_data: dict, username: str):
        if username in self.active_connections:
            for connection in self.active_connections[username]:
                await self.send_order_data(order_data, connection)
            return True
        else:
            return False
