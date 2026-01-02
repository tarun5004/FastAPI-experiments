# 19 — WebSockets & Real-Time Communication (Complete In-Depth Guide)

> 🎯 **Goal**: Real-time features add karo - Chat, Notifications, Live Updates!

---

## 📚 Table of Contents
1. [HTTP vs WebSocket](#http-vs-websocket)
2. [WebSocket Basics](#websocket-basics)
3. [FastAPI WebSockets](#fastapi-websockets)
4. [Connection Management](#connection-management)
5. [Chat Application](#chat-application)
6. [Broadcast & Rooms](#broadcast--rooms)
7. [Authentication](#authentication)
8. [Scaling WebSockets](#scaling-websockets)
9. [Server-Sent Events (SSE)](#server-sent-events-sse)
10. [Best Practices](#best-practices)

---

## HTTP vs WebSocket

### The Problem with HTTP

```
HTTP = Request-Response Model

Client: "Koi naya message hai?"
Server: "Nahi"

(1 second later)
Client: "Koi naya message hai?"
Server: "Nahi"

(1 second later)
Client: "Koi naya message hai?"
Server: "Haan, ek message hai!"

This is POLLING - wasteful and slow!
```

### HTTP Polling vs WebSocket

```
HTTP Polling (Bad):
─────────────────────────────────────────────────────────
Client ──► "Any updates?" ──► Server
Client ◄── "No" ◄── Server

Client ──► "Any updates?" ──► Server
Client ◄── "No" ◄── Server

Client ──► "Any updates?" ──► Server
Client ◄── "Yes! Here's data" ◄── Server

❌ Many requests even when no data
❌ Delay between data arrival and client getting it
❌ Server overhead for each request


WebSocket (Good):
─────────────────────────────────────────────────────────
Client ────── Handshake ──────► Server
       ◄──── Connection Open ────

       ◄──── "New message!" ────  (instant!)
       ◄──── "User joined" ────   (instant!)
Client ────── "Send message" ──►
       ◄──── "Message sent" ────

✅ Persistent connection
✅ Real-time, instant updates
✅ Bi-directional communication
✅ Less overhead
```

### Visual: WebSocket Connection

```
    Client                                Server
      │                                      │
      │ ──── HTTP Upgrade Request ────►      │
      │      GET /ws HTTP/1.1                │
      │      Upgrade: websocket              │
      │      Connection: Upgrade             │
      │                                      │
      │ ◄─── HTTP 101 Switching Protocols ── │
      │                                      │
      │ ════════════════════════════════════ │
      │        WebSocket Connection          │
      │ ════════════════════════════════════ │
      │                                      │
      │ ◄──── Message ────                   │
      │ ────► Message ────                   │
      │ ◄──── Message ────                   │
      │                                      │
```

---

## WebSocket Basics

### How WebSocket Works

```
1. HANDSHAKE (HTTP Upgrade)
   - Client requests upgrade to WebSocket
   - Server accepts with 101 response
   
2. CONNECTION OPEN
   - Persistent TCP connection
   - Both can send messages anytime
   
3. MESSAGE EXCHANGE
   - Text messages (JSON usually)
   - Binary messages (images, files)
   
4. CONNECTION CLOSE
   - Either side can close
   - Close frame with code and reason
```

### WebSocket Message Types

```python
# Text Message (most common)
await websocket.send_text("Hello!")
message = await websocket.receive_text()

# JSON Message
await websocket.send_json({"type": "message", "data": "Hello"})
data = await websocket.receive_json()

# Binary Message
await websocket.send_bytes(image_bytes)
data = await websocket.receive_bytes()
```

---

## FastAPI WebSockets

### Basic WebSocket Endpoint

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Basic WebSocket endpoint
    
    Steps:
    1. Accept connection
    2. Receive messages in loop
    3. Send response back
    4. Handle disconnection
    """
    # Step 1: Accept connection
    await websocket.accept()
    
    try:
        # Step 2: Message loop
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            # Echo back
            await websocket.send_text(f"You said: {data}")
            
    except WebSocketDisconnect:
        print("Client disconnected")
```

### Testing WebSocket

```python
# test_client.py (manual testing)
import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send("Hello, Server!")
        
        # Receive response
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(test_websocket())


# pytest testing
from fastapi.testclient import TestClient

def test_websocket():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("Hello")
        data = websocket.receive_text()
        assert data == "You said: Hello"
```

### WebSocket with Path Parameters

```python
@app.websocket("/ws/{room_id}")
async def room_websocket(websocket: WebSocket, room_id: str):
    """
    WebSocket with path parameter
    
    Connect to: ws://localhost:8000/ws/room-123
    """
    await websocket.accept()
    
    print(f"Client connected to room: {room_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"[{room_id}] {data}")
    except WebSocketDisconnect:
        print(f"Client left room: {room_id}")
```

### WebSocket with Query Parameters

```python
@app.websocket("/ws")
async def websocket_with_query(
    websocket: WebSocket,
    token: str = None,
    client_id: str = None
):
    """
    WebSocket with query parameters
    
    Connect to: ws://localhost:8000/ws?token=abc&client_id=123
    """
    if not token:
        await websocket.close(code=4001, reason="Token required")
        return
    
    await websocket.accept()
    print(f"Client {client_id} connected with token {token}")
    
    # ... rest of logic
```

---

## Connection Management

### Connection Manager Class

```python
from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    """
    Manage all WebSocket connections
    
    Responsibilities:
    - Track active connections
    - Send to specific client
    - Broadcast to all
    - Handle disconnection
    """
    
    def __init__(self):
        # All active connections
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store new connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove disconnected client"""
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific client"""
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        """Send message to ALL connected clients"""
        for connection in self.active_connections:
            await connection.send_text(message)
    
    async def broadcast_except(self, message: str, exclude: WebSocket):
        """Send to all except sender"""
        for connection in self.active_connections:
            if connection != exclude:
                await connection.send_text(message)


# Create global instance
manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all clients
            await manager.broadcast(f"Someone said: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A user left the chat")
```

### User-Based Connection Manager

```python
from typing import Dict

class UserConnectionManager:
    """
    Track connections by user ID
    
    Use when you need to:
    - Send to specific user
    - Handle multiple devices per user
    """
    
    def __init__(self):
        # user_id -> list of connections (for multiple devices)
        self.connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.connections:
            self.connections[user_id] = []
        self.connections[user_id].append(websocket)
    
    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.connections:
            self.connections[user_id].remove(websocket)
            if not self.connections[user_id]:
                del self.connections[user_id]
    
    async def send_to_user(self, user_id: str, message: str):
        """Send to all devices of a user"""
        if user_id in self.connections:
            for websocket in self.connections[user_id]:
                await websocket.send_text(message)
    
    def is_online(self, user_id: str) -> bool:
        return user_id in self.connections
    
    def online_users(self) -> List[str]:
        return list(self.connections.keys())


user_manager = UserConnectionManager()


@app.websocket("/ws/{user_id}")
async def user_websocket(websocket: WebSocket, user_id: str):
    await user_manager.connect(user_id, websocket)
    
    # Notify others
    for other_user in user_manager.online_users():
        if other_user != user_id:
            await user_manager.send_to_user(other_user, f"{user_id} joined!")
    
    try:
        while True:
            data = await websocket.receive_json()
            # Send to specific user
            if data["type"] == "private_message":
                await user_manager.send_to_user(
                    data["to"],
                    f"From {user_id}: {data['message']}"
                )
    except WebSocketDisconnect:
        user_manager.disconnect(user_id, websocket)
```

---

## Chat Application

### Complete Chat Server

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List
import json

app = FastAPI()

class Message(BaseModel):
    type: str  # "message", "join", "leave"
    username: str
    content: str = ""
    timestamp: str = ""


class ChatRoom:
    """Single chat room manager"""
    
    def __init__(self, name: str):
        self.name = name
        self.connections: Dict[str, WebSocket] = {}  # username -> websocket
        self.message_history: List[dict] = []
    
    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[username] = websocket
        
        # Send history to new user
        for msg in self.message_history[-50:]:  # Last 50 messages
            await websocket.send_json(msg)
        
        # Notify room
        await self.broadcast({
            "type": "join",
            "username": username,
            "content": f"{username} joined the room",
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, username: str):
        if username in self.connections:
            del self.connections[username]
    
    async def broadcast(self, message: dict):
        """Send to all in room"""
        self.message_history.append(message)
        
        for websocket in self.connections.values():
            await websocket.send_json(message)
    
    def get_users(self) -> List[str]:
        return list(self.connections.keys())


# Store all rooms
rooms: Dict[str, ChatRoom] = {}


def get_or_create_room(room_name: str) -> ChatRoom:
    if room_name not in rooms:
        rooms[room_name] = ChatRoom(room_name)
    return rooms[room_name]


@app.websocket("/chat/{room_name}/{username}")
async def chat_endpoint(
    websocket: WebSocket,
    room_name: str,
    username: str
):
    room = get_or_create_room(room_name)
    
    # Check if username taken
    if username in room.connections:
        await websocket.close(code=4000, reason="Username taken")
        return
    
    await room.connect(username, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "message":
                await room.broadcast({
                    "type": "message",
                    "username": username,
                    "content": data["content"],
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        room.disconnect(username)
        await room.broadcast({
            "type": "leave",
            "username": username,
            "content": f"{username} left the room",
            "timestamp": datetime.now().isoformat()
        })


@app.get("/rooms/{room_name}/users")
async def get_room_users(room_name: str):
    """Get list of users in room"""
    if room_name in rooms:
        return {"users": rooms[room_name].get_users()}
    return {"users": []}
```

### JavaScript Client

```html
<!DOCTYPE html>
<html>
<head>
    <title>Chat Room</title>
</head>
<body>
    <div id="messages"></div>
    <input type="text" id="messageInput" placeholder="Type a message...">
    <button onclick="sendMessage()">Send</button>

    <script>
        const roomName = "general";
        const username = "user" + Math.floor(Math.random() * 1000);
        
        // Connect to WebSocket
        const ws = new WebSocket(`ws://localhost:8000/chat/${roomName}/${username}`);
        
        ws.onopen = () => {
            console.log("Connected!");
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const messages = document.getElementById("messages");
            
            if (data.type === "message") {
                messages.innerHTML += `<p><b>${data.username}:</b> ${data.content}</p>`;
            } else if (data.type === "join") {
                messages.innerHTML += `<p style="color:green">${data.content}</p>`;
            } else if (data.type === "leave") {
                messages.innerHTML += `<p style="color:red">${data.content}</p>`;
            }
        };
        
        ws.onclose = () => {
            console.log("Disconnected");
        };
        
        function sendMessage() {
            const input = document.getElementById("messageInput");
            ws.send(JSON.stringify({
                type: "message",
                content: input.value
            }));
            input.value = "";
        }
    </script>
</body>
</html>
```

---

## Broadcast & Rooms

### Room-Based Broadcasting

```python
class RoomManager:
    """
    Manage multiple chat rooms
    
    Features:
    - Create/delete rooms
    - Join/leave rooms
    - Broadcast to room
    """
    
    def __init__(self):
        self.rooms: Dict[str, set] = {}  # room_name -> set of websockets
        self.user_rooms: Dict[WebSocket, str] = {}  # websocket -> current room
    
    async def join_room(self, room: str, websocket: WebSocket):
        """User joins a room"""
        # Leave previous room
        if websocket in self.user_rooms:
            await self.leave_room(websocket)
        
        # Join new room
        if room not in self.rooms:
            self.rooms[room] = set()
        
        self.rooms[room].add(websocket)
        self.user_rooms[websocket] = room
        
        await self.broadcast_to_room(room, {
            "type": "system",
            "message": "A user joined the room"
        }, exclude=websocket)
    
    async def leave_room(self, websocket: WebSocket):
        """User leaves current room"""
        if websocket in self.user_rooms:
            room = self.user_rooms[websocket]
            self.rooms[room].discard(websocket)
            del self.user_rooms[websocket]
            
            await self.broadcast_to_room(room, {
                "type": "system",
                "message": "A user left the room"
            })
    
    async def broadcast_to_room(self, room: str, message: dict, exclude: WebSocket = None):
        """Broadcast to all users in a room"""
        if room in self.rooms:
            for ws in self.rooms[room]:
                if ws != exclude:
                    await ws.send_json(message)
    
    async def broadcast_all(self, message: dict):
        """Broadcast to ALL users in ALL rooms"""
        for room_sockets in self.rooms.values():
            for ws in room_sockets:
                await ws.send_json(message)


room_manager = RoomManager()


@app.websocket("/ws")
async def websocket_with_rooms(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "join":
                await room_manager.join_room(data["room"], websocket)
                
            elif data["type"] == "message":
                room = room_manager.user_rooms.get(websocket)
                if room:
                    await room_manager.broadcast_to_room(room, {
                        "type": "message",
                        "content": data["content"]
                    })
    
    except WebSocketDisconnect:
        await room_manager.leave_room(websocket)
```

---

## Authentication

### Token-Based WebSocket Auth

```python
from fastapi import WebSocket, Depends, HTTPException, status
from jose import JWTError, jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


async def get_user_from_token(token: str):
    """Verify token and return user"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return await get_user(user_id)
    except JWTError:
        return None


@app.websocket("/ws")
async def authenticated_websocket(websocket: WebSocket):
    """
    WebSocket with token authentication
    
    Options to pass token:
    1. Query parameter: ws://localhost:8000/ws?token=xxx
    2. First message after connect
    """
    
    # Option 1: Token in query parameter
    token = websocket.query_params.get("token")
    
    if not token:
        await websocket.close(code=4001, reason="Token required")
        return
    
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=4003, reason="Invalid token")
        return
    
    # Token valid, accept connection
    await websocket.accept()
    print(f"User {user.id} connected via WebSocket")
    
    try:
        while True:
            data = await websocket.receive_json()
            # Process messages...
    except WebSocketDisconnect:
        print(f"User {user.id} disconnected")


# Alternative: Token in first message
@app.websocket("/ws/v2")
async def websocket_token_in_message(websocket: WebSocket):
    """Accept first, then verify token in first message"""
    await websocket.accept()
    
    # Wait for auth message
    try:
        auth_data = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=5.0  # 5 second timeout for auth
        )
    except asyncio.TimeoutError:
        await websocket.close(code=4002, reason="Auth timeout")
        return
    
    if auth_data.get("type") != "auth":
        await websocket.close(code=4001, reason="First message must be auth")
        return
    
    user = await get_user_from_token(auth_data.get("token"))
    if not user:
        await websocket.close(code=4003, reason="Invalid token")
        return
    
    # Send auth success
    await websocket.send_json({"type": "auth_success", "user_id": user.id})
    
    # Now handle regular messages...
```

---

## Scaling WebSockets

### The Problem

```
Single Server:
─────────────────────────────────────────────────────────
All users connect to one server → Works fine


Multiple Servers (Load Balancing):
─────────────────────────────────────────────────────────
User A ──► Server 1
User B ──► Server 2

User A sends message to User B...
Server 1 doesn't know about User B! ❌
```

### Solution: Redis Pub/Sub

```python
# Use Redis as message broker between servers

import aioredis
import json

class ScalableConnectionManager:
    """
    Connection manager that works across multiple servers
    using Redis pub/sub
    """
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.redis = None
        self.pubsub = None
    
    async def connect_redis(self):
        self.redis = await aioredis.from_url("redis://localhost:6379")
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe("chat_messages")
        
        # Start listening for messages from other servers
        asyncio.create_task(self._listen_redis())
    
    async def _listen_redis(self):
        """Listen for messages from Redis (other servers)"""
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                # Send to local connections
                for ws in self.connections.values():
                    await ws.send_json(data)
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[user_id] = websocket
    
    async def broadcast(self, message: dict):
        """
        Broadcast to ALL users across ALL servers
        by publishing to Redis
        """
        await self.redis.publish("chat_messages", json.dumps(message))


manager = ScalableConnectionManager()


@app.on_event("startup")
async def startup():
    await manager.connect_redis()
```

### Docker Compose for Scaling

```yaml
version: "3.8"
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  app:
    build: .
    ports:
      - "8000-8002:8000"
    deploy:
      replicas: 3
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379
```

---

## Server-Sent Events (SSE)

### SSE vs WebSocket

```
WebSocket:
─────────────────────────────────────────────────────────
✅ Bi-directional (client ↔ server)
✅ Real-time
❌ More complex
❌ Needs special handling for proxies


Server-Sent Events (SSE):
─────────────────────────────────────────────────────────
✅ Simple (just HTTP)
✅ Auto-reconnect
✅ Works through proxies
❌ One-way only (server → client)
❌ No binary data

Use SSE when: Only server needs to push (notifications, live updates)
Use WebSocket when: Both sides need to send (chat, games)
```

### SSE in FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()


async def event_generator():
    """
    Generator that yields SSE events
    
    SSE Format:
    data: message content\n\n
    """
    counter = 0
    while True:
        counter += 1
        yield f"data: Event {counter} at {datetime.now()}\n\n"
        await asyncio.sleep(1)  # Send every second


@app.get("/events")
async def sse_endpoint():
    """
    Server-Sent Events endpoint
    
    Client connects with:
    const eventSource = new EventSource('/events');
    eventSource.onmessage = (event) => console.log(event.data);
    """
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


# SSE with event types
async def typed_event_generator():
    while True:
        # Named event
        yield f"event: notification\ndata: You have a new message\n\n"
        await asyncio.sleep(5)
        
        # Different event type
        yield f"event: update\ndata: {json.dumps({'count': 42})}\n\n"
        await asyncio.sleep(5)


# JavaScript client
"""
const es = new EventSource('/events');

// Default message event
es.onmessage = (e) => console.log(e.data);

// Named events
es.addEventListener('notification', (e) => {
    showNotification(e.data);
});

es.addEventListener('update', (e) => {
    const data = JSON.parse(e.data);
    updateUI(data);
});
"""
```

---

## Best Practices

### 1. Handle Connection Errors

```python
@app.websocket("/ws")
async def robust_websocket(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0  # Ping/pong timeout
                )
                await websocket.send_text(f"Received: {data}")
                
            except asyncio.TimeoutError:
                # Send ping to check if alive
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        print("Clean disconnect")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close(code=1011, reason="Internal error")
```

### 2. Heartbeat/Keep-Alive

```python
async def heartbeat(websocket: WebSocket):
    """Send periodic heartbeat to detect dead connections"""
    while True:
        try:
            await asyncio.sleep(30)  # Every 30 seconds
            await websocket.send_json({"type": "heartbeat"})
        except:
            break


@app.websocket("/ws")
async def websocket_with_heartbeat(websocket: WebSocket):
    await websocket.accept()
    
    # Start heartbeat task
    heartbeat_task = asyncio.create_task(heartbeat(websocket))
    
    try:
        while True:
            data = await websocket.receive_text()
            # Process...
    finally:
        heartbeat_task.cancel()
```

### 3. Message Validation

```python
from pydantic import BaseModel, ValidationError

class ChatMessage(BaseModel):
    type: str
    content: str = ""
    target_user: str = None


@app.websocket("/ws")
async def validated_websocket(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            raw_data = await websocket.receive_json()
            
            try:
                message = ChatMessage(**raw_data)
            except ValidationError as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                continue
            
            # Process validated message...
    except WebSocketDisconnect:
        pass
```

### 4. Rate Limiting

```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_messages: int, window_seconds: int):
        self.max_messages = max_messages
        self.window = window_seconds
        self.message_counts: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        # Remove old timestamps
        self.message_counts[user_id] = [
            t for t in self.message_counts[user_id]
            if now - t < self.window
        ]
        
        if len(self.message_counts[user_id]) >= self.max_messages:
            return False
        
        self.message_counts[user_id].append(now)
        return True


rate_limiter = RateLimiter(max_messages=10, window_seconds=60)


@app.websocket("/ws")
async def rate_limited_websocket(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    while True:
        data = await websocket.receive_text()
        
        if not rate_limiter.is_allowed(user_id):
            await websocket.send_json({
                "type": "error",
                "message": "Rate limit exceeded. Please slow down."
            })
            continue
        
        # Process message...
```

---

## Quick Reference

```python
# Basic WebSocket
@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")

# JSON messages
data = await websocket.receive_json()
await websocket.send_json({"type": "response", "data": data})

# Close codes:
# 1000 - Normal closure
# 1001 - Going away
# 4000+ - Application specific

# SSE
from fastapi.responses import StreamingResponse

async def generator():
    yield f"data: message\n\n"

@app.get("/events")
async def sse():
    return StreamingResponse(generator(), media_type="text/event-stream")
```

---

> **Pro Tip**: "Chat, notifications, live scores - jab bhi real-time chahiye, WebSocket use karo!" ⚡
