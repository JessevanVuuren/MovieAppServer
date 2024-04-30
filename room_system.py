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
        self.key: str = key
        self.users: list[User] = []
        self.final_movie = None
        self.full_wanted_list: list[str] = []
        self.full_unwanted_list: list[str] = []

    def add_unwanted(self, user: User, id: str):
        if (id not in user.list_of_unwanted):
            self.full_unwanted_list.append(id)
            user.list_of_unwanted.append(id)
        
        if (id in self.full_wanted_list):
            self.full_wanted_list.remove(id)

    def add_wanted(self, user: User, id: str):
        if (id not in user.list_of_wanted):
            self.full_wanted_list.append(id)
            user.list_of_wanted.append(id)
            self.match_compare()

    def broadcast_info(self, success=True, status="success", error=""):
        payload = {
            "amount_of_users": len(self.users),
            "wanted_list": self.full_wanted_list,
            "unwanted_list": self.full_unwanted_list,
            "final_movie": self.final_movie,
            "key": self.key
        }

        asyncio.create_task(self.send_payload_to_user(payload, success=True, status="success", error=""))

    async def send_payload_to_user(self, payload, success=True, status="success", error=""):
        for user in self.users:
            await user.websocket.send_json(send_response(success, status, error, payload))

    def match_compare(self):
        counter = Counter(self.full_wanted_list)
        set_list = list(set(self.full_wanted_list))

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

    def cancel_final_movie(self):
        self.full_wanted_list.remove(self.final_movie)
        self.final_movie = None
        self.broadcast_info()

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
                room.broadcast_info()
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

    def get_amount_of_rooms(self) -> int:
        return len(self.rooms)

    def get_amount_of_users(self) -> int:
        users = 0
        for room in self.rooms:
            users += len(room.users)
        return users
