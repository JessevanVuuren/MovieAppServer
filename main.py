from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from networking import send_response 

import roomSystem

app = FastAPI()
RS = roomSystem.RoomSystem()



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.websocket("/ws")
async def websocket_endpoint(user: WebSocket):
    

    await user.accept()
    user_connected = True;
    room = None
    while user_connected:
        try:
            data = await user.receive_json()

            if (data["type"] == "room"):
                user_connected = await handle_room_request(data, user)
                if (user_connected):
                    room = RS.get_room(data["key"])
                else:
                    room = None

            elif (data["type"] == "movie" and room is not None):
                await handle_movie_request(data, user, room)

        except WebSocketDisconnect:
            RS.leave_room(user)
            break

        except Exception as e:
            print(e)
            await user.send_json(send_response(False, "failed", "Invalid json", {}))


async def handle_room_request(request, user):
    if (request["method"] == "create" and not RS.is_user_already_in_room(user)):
        key = RS.create_room(user)
        await user.send_json(send_response(True, "success", "", {"key": key}))

    elif(request["method"] == "join" and not RS.is_user_already_in_room(user)):
        joined = RS.join_room(user, request["key"])
        if (joined):
            await user.send_json(send_response(True, "success", "", {"joined": joined}))
        else:
            await user.send_json(send_response(False, "failed", "No room", {}))
    
    elif(request["method"] == "leave"):
        RS.leave_room(user)
        await user.close()
        return False

    return True


async def handle_movie_request(request, user, room):
    pass