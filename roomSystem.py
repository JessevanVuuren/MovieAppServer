from helper import send_response, logger
from collections import Counter
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
        try:
            await self.websocket.close()
        except Exception as e:
            logger.warning("User disconnected forcefully")


class Room:
    def __init__(self, key: str) -> None:
        self.key: str = key  # -> 04232
        self.users: list[User] = []
        self.final_movie = None

    def add_unwanted(self, user: User, id: str):
        if (id not in user.list_of_unwanted):
            user.list_of_unwanted.append(id)

    def add_wanted(self, user: User, id: str):
        if (id not in user.list_of_wanted):
            user.list_of_wanted.append(id)
            self.match_compare()

    def broadcast_info(self, user: User, success=True, status="success", error=""):
        list_wanted: list[str] = []
        list_unwanted: list[str] = []

        for userI in self.users:
            list_wanted += userI.list_of_wanted
            list_unwanted += userI.list_of_unwanted

        payload = {
            "amount_of_users": len(self.users),
            "wanted_list": list_wanted,
            "unwanted_list": list_unwanted,
            "final_movie": self.final_movie,
            "key": self.key
        }
        asyncio.create_task(   
        self.broadcast(payload, success=True, status="success", error="")
        )

    async def broadcast(self, payload, success=True, status="success", error=""):
        for user in self.users:
            await user.websocket.send_json(send_response(success, status, error, payload))

    def match_compare(self):
        all_wanted_list = []

        for user in self.users:
            all_wanted_list += user.list_of_wanted

        counter = Counter(all_wanted_list)
        set_list = list(set(all_wanted_list))

        for movie in set_list:
            if (counter[movie] >= len(self.users)):
                self.final_movie = movie
                break

    def add_user(self, user: User):
        self.users.append(user)

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
        logger.debug(
            "MAKE room - key: {}, rooms: {}".format(key, len(self.rooms)))
        return new_room

    def join_room(self, user: User, key: str) -> Room:
        for room in self.rooms:

            if (room.key == key):
                room.add_user(user)
                logger.debug(
                    "JOIN room - key: {}, users: {}".format(room.key, len(room.users)))
                return room

        return None

    def leave_room(self, user: User):
        for room in self.rooms:
            if (room.is_user_in_room(user)):
                room.remove_user(user)
                logger.debug(
                    "EXIT room - key: {}, users: {}".format(room.key, len(room.users)))
                if (len(room.users) == 0):
                    self.rooms.remove(room)
                    logger.debug("REMOVE room - key: {}".format(room.key))

    def generate_key(self) -> Room:
        key = str(random.randint(0, 100_000)).zfill(5)
        if (key not in self.room_keys):
            self.room_keys.append(key)
            return key

        self.generate_key()

    def is_user_in_room(self, user: User) -> bool:
        for room in self.rooms:
            if (room.is_user_in_room(user)):
                return True

        return False

    def get_room(self, key: str) -> Room:
        for room in self.rooms:
            if (room.key == key):
                return room
