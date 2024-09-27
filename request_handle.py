from room_system import RoomSystem, User
from helper import send_response, logger

import requests
import os 

API_KEY = os.getenv("API_KEY")

def check_show_response(type:str, id:int):
    response = requests.get(f"https://api.themoviedb.org/3/{type}/{id}?api_key={API_KEY}&language=en-US")
    data = response.json()

    if (response.status_code != 200 or ("success" in data.keys() and data["success"] == False)):
        return True, data

    return False, data

async def handle_room_request(request, user: User, RS: RoomSystem):
    if (request["method"] == "create" and not RS.is_user_in_room(user)):
        user.room = RS.create_room(user)
        user.room.broadcast_info()

    elif (request["method"] == "join" and not RS.is_user_in_room(user)):
        user.room = RS.join_room(user, request["key"])
        if (user.room is not None):
            user.room.broadcast_info()
        else:
            await user.websocket.send_json(send_response(False, "failed", "No room", {}))

    elif (request["method"] == "leave"):
        RS.leave_room(user)



async def handle_movie_request(request, user: User):

    if (request["method"] == "wanted"):
        user.room.add_wanted(user, request["id"])
        user.room.broadcast_info()

    if (request["method"] == "unwanted"):
        user.room.add_unwanted(user, request["id"])
        user.room.broadcast_info()

    if (request["method"] == "cancel_final_movie"):
        user.room.cancel_final_movie()


def handle_payload_response(RS: RoomSystem):
    rooms = []
    for room in RS.rooms:
        rooms.append({
            "key": room.key,
            "users": len(room.users),
            "wanted": room.full_wanted_list,
            "unwanted": room.full_unwanted_list
        })

    payload = {
        "amount_users": RS.get_amount_of_users(),
        "amount_rooms": RS.get_amount_of_rooms(),
        "rooms": rooms
    }

    return payload
