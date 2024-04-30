from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from room_system import RoomSystem, User
# from dotenv import load_dotenv
from request_handle import *
from helper import *

import datetime
import asyncio
import time
import os

# load_dotenv()

BASE_URL = os.getenv("BASE_URL")
DASHBOARD_URL = os.getenv("DASHBOARD_URL")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD")

app = FastAPI()
RS = RoomSystem()

connection_users:dict[str, dict[int, int]] = {}

logger.warning("SERVER TYPE: " + os.getenv("SERVER_TYPE"))

app.mount(DASHBOARD_URL, StaticFiles(
    directory="static", html=True), name="static")


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
    host_ip = websocket.client.host
    await websocket.accept()
    is_auth = False

    if (host_ip not in connection_users.keys()):
        logger.warning("New user: " + host_ip)
        connection_ban(connection_users, host_ip, reset=True)

    pre_ban_time = connection_users[host_ip]["ban_time"]
    while (True):
        try:
            password = (await websocket.receive_json())["password"]

            if password == os.getenv("DASHBOARD_PASSWORD") and int(time.time()) > connection_users[host_ip]["new_time"]:
                connection_ban(connection_users, host_ip, reset=True)
                is_auth = True
                break

            if (int(time.time()) > connection_users[host_ip]["new_time"]):
                connection_ban(connection_users, host_ip)

            if (pre_ban_time != connection_users[host_ip]["ban_time"]):
                logger.warning("host: {}, banned for: {}".format(host_ip, connection_users[host_ip]["ban_time"]))

            pre_ban_time = connection_users[host_ip]["ban_time"]
            await websocket.send_json(send_response(False, "Failed", "wrong password", {"ban_time": connection_users[host_ip]["ban_time"]}))

        except WebSocketDisconnect:
            logger.warning("User disconnect: " + host_ip)
            break

        except RuntimeError:
            logger.warning("User disconnect: " + host_ip)
            break


    while is_auth:
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
