from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from room_system import RoomSystem, User
from request_handle import *
from helper import *
import os


BASE_URL = os.getenv("BASE_URL")
SERVER_TYPE = os.getenv("SERVER_TYPE")

app = FastAPI()
roomSystem = RoomSystem()

logger.warning("SERVER TYPE: " + SERVER_TYPE)
app.mount(BASE_URL, StaticFiles(directory="static", html=True), name="static")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/robots.txt', response_class=PlainTextResponse)
def robots():
    return """User-agent: *\nDisallow: /"""


@app.get(BASE_URL + "/is-online")
async def status():
    return {"status": True}


@app.websocket(BASE_URL + "/ws")
async def websocket_tinder(websocket: WebSocket):
    await websocket.accept()
    user = User(websocket)

    while user.is_connected:
        try:
            data = await user.websocket.receive_json()

            if (data["type"] == "room"):
                await handle_room_request(data, user, roomSystem)

            elif (data["type"] == "movie" and user.room is not None):
                await handle_movie_request(data, user)

        except WebSocketDisconnect:
            roomSystem.leave_room(user)
            if (user.is_connected):
                await user.disconnect()

        except Exception as e:
            logger.warning(e)
            await user.websocket.send_json(send_response(False, "Server error", "Fault", {}))
