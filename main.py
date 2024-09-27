from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from room_system import RoomSystem, User

from request_handle import *
from helper import *
import requests
import os


BASE_URL = os.getenv("BASE_URL")
SERVER_TYPE = os.getenv("SERVER_TYPE")

app = FastAPI()
html = FastAPI()
roomSystem = RoomSystem()

logger.warning("SERVER TYPE: " + SERVER_TYPE)

templates = Jinja2Templates(directory="templates")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return RedirectResponse("/")


@app.get('/robots.txt', response_class=PlainTextResponse)
def robots():
    return """User-agent: *\nDisallow: /"""


@app.get(BASE_URL + "/is-online")
async def status():
    return {"status": True}


@app.get(BASE_URL + "/movie")
async def movie(id: int, request: Request):
    err, data = check_show_response("movie", id)

    if (err):
        logger.error(f"id: {id} does not exist")
        return RedirectResponse("/")

    logger.info(f"Shared movie: {id}, name: {data['title']}")
    return templates.TemplateResponse("show.html", {"request": request, "data": data, "title": data['title']})


@app.get(BASE_URL + "/tv")
async def tvShow(id: int, request: Request):
    err, data = check_show_response("tv", id)

    if (err):
        logger.error(f"id: {id} does not exist")
        return RedirectResponse("/")

    logger.info(f"Shared tv-show: {id}, name: {data['name']}")
    return templates.TemplateResponse("show.html", {"request": request, "data": data, "title": data['title']})


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


app.mount(BASE_URL, StaticFiles(directory="static", html=True), name="static")
