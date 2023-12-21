from networking import send_response
from fastapi import WebSocket

import asyncio
import random


class User:
    def __init__(self, websocket: WebSocket) -> None:
        self.room: Room = None
        self.websocket: WebSocket = websocket
        self.is_connected: bool = True
        self.list_of_wanted: list[str] = []
        self.list_of_unwanted: list[str] = []

    async def disconnect(self):
        self.room = None
        self.is_connected = False
        await self.websocket.close()


class Room:
    def __init__(self, key: str) -> None:
        self.key: str = key  # -> 04232
        self.users: list[User] = []
        self.final_movie = None

    def add_unwanted(self, user:User, id: str):
        user.list_of_unwanted.append(id)
        self.match_compare()
        self.broadcast_info(user)

    def add_wanted(self, user:User, id: str):
        user.list_of_wanted.append(id)
        self.broadcast_info(user)

    def broadcast_info(self, user: User):
        list_wanted: list[str] = []
        list_unwanted: list[str] = []

        for userI in self.users:
            if (user != userI):
                list_wanted += userI.list_of_wanted
                list_unwanted += userI.list_of_unwanted

        payload = {
            "amount_of_users": len(self.users),
            "wanted_list": list_wanted,
            "unwanted_list": list_unwanted,
            "final_movie": self.final_movie
        }

        self.broadcast(payload)

    def broadcast(self, payload):
        for user in self.users:
            asyncio.create_task(
                user.websocket.send_json(send_response(True, "success", "", payload)))

    def match_compare(self):
        pass

    def add_user(self, user: User):
        self.users.append(user)
        self.broadcast_info(user)

    def remove_user(self, user: User):
        if (self.is_user_in_room(user)):
            self.users.remove(user)

    def is_user_in_room(self, user: User):
        return user in self.users


class RoomSystem:
    def __init__(self) -> None:
        self.rooms: list[Room] = []
        self.room_keys: list[str] = []

    def create_room(self, user: WebSocket) -> Room:
        key = self.generate_key()
        new_room = Room(key)
        self.rooms.append(new_room)
        new_room.add_user(user)
        print("MAKE room - key: {}, rooms: {}".format(key, len(self.rooms)))
        return new_room

    def join_room(self, user: User, key: str) -> Room:
        for room in self.rooms:

            if (room.key == key):
                room.add_user(user)
                print("JOIN room - key: {}, users: {}".format(room.key, len(room.users)))
                return room

        return None

    def leave_room(self, user: User):
        for room in self.rooms:
            if (room.is_user_in_room(user)):
                room.remove_user(user)
                print("EXIT room - key: {}, users: {}".format(room.key, len(room.users)))
                if (len(room.users) == 0):
                    self.rooms.remove(room)
                    print("REMOVE room - key: {}".format(room.key))

    def generate_key(self) -> Room:
        key = str(random.randint(0, 100_000)).zfill(5)
        if (key not in self.room_keys):
            self.room_keys.append(key)
            return key

        self.generate_key()

    def is_user_already_in_room(self, user: User) -> bool:
        for room in self.rooms:
            if (room.is_user_in_room(user)):
                return True

        return False

    def get_room(self, key: str) -> Room:
        for room in self.rooms:
            if (room.key == key):
                return room
