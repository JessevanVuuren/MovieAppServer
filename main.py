from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from helper import send_response, logger
from room_system import RoomSystem, User
from request_handle import *

import asyncio
import time
import os

BASE_URL = os.getenv("BASE_URL")
DASHBOARD_URL = os.getenv("DASHBOARD_URL")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD")

app = FastAPI()
RS = RoomSystem()

logger.warning("SERVER TYPE: " + os.getenv("SERVER_TYPE"))

app.mount(DASHBOARD_URL, StaticFiles(directory="static", html=True), name="static")


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/robots.txt', response_class=PlainTextResponse)
def robots():
    return """User-agent: *\nDisallow: /"""


@app.get(BASE_URL + "/is-online")
async def status():
    return {"status": True}


@app.websocket(BASE_URL + "/wss")
async def websocket_tinder(websocket: WebSocket):
    await websocket.accept()
    user = User(websocket)

    while user.is_connected:
        try:
            data = await user.websocket.receive_json()

            if (data["type"] == "room"):
                await handle_room_request(data, user, RS)

            elif (data["type"] == "movie" and user.room is not None):
                await handle_movie_request(data, user)

        except WebSocketDisconnect:
            RS.leave_room(user)
            if (user.is_connected):
                await user.disconnect()

        except Exception as e:
            logger.warning(e)
            await user.websocket.send_json(send_response(False, "Server error", "Fault", {}))



@app.websocket(DASHBOARD_URL + "-wss")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    is_connected = True
    while is_connected:
        try:
            
            payload = handle_payload_response(RS)
            await websocket.send_json(send_response(True, "success", "", payload))
            await asyncio.sleep(1)

        except WebSocketDisconnect:
            await websocket.close()
            is_connected = False
            break

        except Exception as e:
            await websocket.close()
            logger.warning(e)
            is_connected = False
            break