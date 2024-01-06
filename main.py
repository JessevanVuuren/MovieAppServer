from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from helper import send_response, logger
from roomSystem import RoomSystem, User

app = FastAPI()
RS = RoomSystem()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/is-online")
async def status():
    return {"status": True}
    

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user = User(websocket)

    while user.is_connected:
        try:
            data = await user.websocket.receive_json()

            if (data["type"] == "room"):
                await handle_room_request(data, user)

            elif (data["type"] == "movie" and user.room is not None):
                await handle_movie_request(data, user)

        except WebSocketDisconnect:
            RS.leave_room(user)
            if (user.is_connected):
                await user.disconnect()

        except Exception as e:
            logger.warning(e)
            await user.websocket.send_json(send_response(False, "failed", "Invalid json", {}))


async def handle_room_request(request, user:User):
    if (request["method"] == "create" and not RS.is_user_already_in_room(user)):
        user.room = RS.create_room(user)
        user.room.broadcast_info(user)


    elif(request["method"] == "join" and not RS.is_user_already_in_room(user)):
        user.room = RS.join_room(user, request["key"])
        if (user.room is not None):
            user.room.broadcast_info(user)
        else:
            user.websocket.send_json(send_response(False, "failed", "No room", {}))
            # user.room.broadcast_info(user, False, "failed", "No room")
    
    elif(request["method"] == "leave"):
        RS.leave_room(user)



async def handle_movie_request(request, user:User):
    # if (RS.user_is_not_in_room(user)):
    #     pass

    
    if (request["method"] == "wanted"):
        room = RS.get_room(request["key"])
        room.add_wanted(user, request["id"])
    
    if (request["method"] == "unwanted"):
        room = RS.get_room(request["key"])
        room.add_unwanted(user, request["id"])
    
    pass