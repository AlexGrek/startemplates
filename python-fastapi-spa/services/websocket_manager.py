from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        # Dictionary to store active connections per user
        # Key: username, Value: List of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, username: str):
        """Connect a user's websocket session"""
        await websocket.accept()

        if username not in self.active_connections:
            self.active_connections[username] = []

        self.active_connections[username].append(websocket)
        logger.info(
            f"User {username} connected. Total sessions: {len(self.active_connections[username])}"
        )

    def disconnect(self, websocket: WebSocket, username: str):
        """Disconnect a user's websocket session"""
        if username in self.active_connections:
            if websocket in self.active_connections[username]:
                self.active_connections[username].remove(websocket)
                logger.info(
                    f"User {username} disconnected. Remaining sessions: {len(self.active_connections[username])}"
                )

                # Remove username from dict if no active connections
                if not self.active_connections[username]:
                    del self.active_connections[username]
                    logger.info(f"User {username} has no more active sessions")

    def get_online_users(self) -> Set[str]:
        """Get set of all online users"""
        return set(self.active_connections.keys())

    def get_user_session_count(self, username: str) -> int:
        """Get number of active sessions for a specific user"""
        return len(self.active_connections.get(username, []))

    def is_user_online(self, username: str) -> bool:
        """Check if a user has any active sessions"""
        return (
            username in self.active_connections
            and len(self.active_connections[username]) > 0
        )

    async def send_to_user(self, username: str, data: Any) -> bool:
        """
        Send data to all active sessions of a specific user

        Args:
            username: Target username
            data: Data to send (will be JSON serialized if not a string)

        Returns:
            bool: True if message was sent to at least one session, False if user is not online
        """
        if username not in self.active_connections:
            return False

        connections = self.active_connections[
            username
        ].copy()  # Copy to avoid modification during iteration
        successful_sends = 0
        dead_connections = []

        # Prepare message
        if isinstance(data, str):
            message = data
        else:
            message = json.dumps(data)

        for websocket in connections:
            try:
                await websocket.send_text(message)
                successful_sends += 1
            except Exception as e:
                logger.warning(f"Failed to send message to {username}: {e}")
                dead_connections.append(websocket)

        # Clean up dead connections
        for dead_ws in dead_connections:
            self.disconnect(dead_ws, username)

        return successful_sends > 0

    async def send_to_user_json(self, username: str, data: Dict) -> bool:
        """
        Send JSON data to all active sessions of a specific user

        Args:
            username: Target username
            data: Dictionary to send as JSON

        Returns:
            bool: True if message was sent to at least one session, False if user is not online
        """
        return await self.send_to_user(username, json.dumps(data))

    async def broadcast_to_all(self, data: Any):
        """Broadcast data to all connected users"""
        if isinstance(data, str):
            message = data
        else:
            message = json.dumps(data)

        dead_connections = []

        for username, connections in self.active_connections.items():
            for websocket in connections.copy():
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.warning(f"Failed to broadcast to {username}: {e}")
                    dead_connections.append((websocket, username))

        # Clean up dead connections
        for dead_ws, username in dead_connections:
            self.disconnect(dead_ws, username)

    async def broadcast_to_users(
        self, usernames: List[str], data: Any
    ) -> Dict[str, bool]:
        """
        Broadcast data to specific list of users

        Args:
            usernames: List of target usernames
            data: Data to send

        Returns:
            Dict mapping username to success status
        """
        results = {}
        for username in usernames:
            results[username] = await self.send_to_user(username, data)
        return results

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections"""
        total_connections = sum(
            len(connections) for connections in self.active_connections.values()
        )
        return {
            "total_users_online": len(self.active_connections),
            "total_connections": total_connections,
            "users_with_multiple_sessions": sum(
                1 for conns in self.active_connections.values() if len(conns) > 1
            ),
            "user_session_counts": {
                username: len(connections)
                for username, connections in self.active_connections.items()
            },
        }


# Global instance
websocket_manager = WebSocketManager()
