from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from models.user import UserRecord
from services import auth_service
from services.websocket_manager import websocket_manager

ws_router = APIRouter()

@ws_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user: UserRecord = Depends(auth_service.get_websocket_user)):
    username = user.username
    
    # Connect user through the manager
    await websocket_manager.connect(websocket, username)
    
    # Send welcome message
    await websocket.send_text(f"Hello, {username}! You are connected.")
    print(f"Client {username} connected")
    
    try:
        while True:
            # Wait for a message from the client
            data = await websocket.receive_text()
            print(f"Received from {username}: {data}")
            
            # Echo the message back to the client
            await websocket.send_text(f"Message received: {data}")
            
    except WebSocketDisconnect:
        print(f"Client {username} disconnected")
    except Exception as e:
        print(f"An error occurred for {username}: {e}")
    finally:
        # Always disconnect through the manager
        websocket_manager.disconnect(websocket, username)