import secrets
from typing import Dict, List
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn


app = FastAPI()

waiting_queue: List[WebSocket] = []
rooms: Dict[str, List[WebSocket]] = {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    if waiting_queue:
        opponent = waiting_queue.pop(0)
        room_id = str(uuid.uuid4())
        rooms[room_id] = [websocket, opponent]

        opponent_color = secrets.choice(["white", "black"])

        await opponent.send_json(
            {
                "type": "match_found",
                "room_id": room_id,
                "color": opponent_color,
            }
        )

        await websocket.send_json(
            {
                "type": "match_found",
                "room_id": room_id,
                "color": "white" if opponent_color == "black" else "black",
            }
        )
    else:
        waiting_queue.append(websocket)
        await websocket.send_json({"type": "waiting_for_opponent"})

    try:
        while True:
            data = await websocket.receive_json()

            for room_id, players in rooms.items():
                if websocket in players:
                    for player in players:
                        if player != websocket:
                            await player.send_json(data)

    except WebSocketDisconnect:
        if websocket in waiting_queue:
            waiting_queue.remove(websocket)
        else:
            for room_id, players in rooms.items():
                if websocket in players:
                    players.remove(websocket)

                    for player in players:
                        await player.send_json({"type": "opponent_left"})

                    del rooms[room_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
