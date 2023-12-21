from networking import send_response
from fastapi import WebSocket

import asyncio
import random


class Room:
    def __init__(self, key) -> None:
        self.key: str = key  # -> 04232
        self.users = []


        self.final_movie = None
        self.list_of_wanted = []
        self.list_of_unwanted = []

    def add_unwanted(self, id):
        self.list_of_unwanted.append(id)
        self.match_compare()
        self.broadcast_info()

    def add_wanted(self, id):
        self.list_of_wanted.append(id)
        self.match_compare()
        self.broadcast_info()

    def broadcast_info(self):
        payload = {
            "amount_of_users": len(self.users),
            "wanted_list": self.list_of_wanted,
            "unwanted_list": self.list_of_unwanted,
            "final_movie": self.final_movie
        }

        self.broadcast(payload)

    def broadcast(self, payload):
        for user in self.users:
            asyncio.create_task(
                user.send_json(send_response(True, "success", "", payload)))

    def match_compare(self):
        pass

    def add_user(self, user):
        self.users.append(user)
        self.broadcast_info()

    def remove_user(self, user):
        if (self.is_user_in_room(user)):
            self.users.remove(user)

    def is_user_in_room(self, user):
        return user in self.users


class RoomSystem:
    def __init__(self) -> None:
        self.rooms: list[Room] = []
        self.room_keys: list[str] = []

    def create_room(self, user: WebSocket) -> str:
        key = self.generate_key()
        new_room = Room(key)
        self.rooms.append(new_room)
        new_room.add_user(user)
        print("MAKE room - key: {}, rooms: {}".format(key, len(self.rooms)))
        return key

    def join_room(self, user: WebSocket, key: str) -> bool:
        for room in self.rooms:

            if (room.key == key):
                room.add_user(user)
                print("JOIN room - key: {}, users: {}".format(room.key, len(room.users)))
                return True

        return False

    def leave_room(self, user: WebSocket):
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

    def is_user_already_in_room(self, user: WebSocket) -> bool:
        for room in self.rooms:
            if (room.is_user_in_room(user)):
                return True

        return False

    def get_room(self, key: str) -> Room:
        for room in self.rooms:
            if (room.key == key):
                return room
