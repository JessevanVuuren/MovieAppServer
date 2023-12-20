import random



class Room:
    def __init__(self, key) -> None:
        self.key = key # -> 04232
        self.users = []


    def add_user(self, user):
        self.users.append(user)


    def remove_user(self, user):
        if (self.is_user_in_room(user)):
            self.users.remove(user)


    def is_user_in_room(self, user):
        return user in self.users
        


class RoomSystem:
    def __init__(self) -> None:
        self.rooms = []
        self.room_keys = []


    def create_room(self, user):
        key = self.generate_key()
        new_room = Room(key)
        self.rooms.append(new_room)
        new_room.add_user(user)
        print("MAKE room - key: {}, rooms: {}".format(key, len(self.rooms)))
        return key
    

    def join_room(self, user, key):
        for room in self.rooms:
            if (room.key == key):
                room.add_user(user)
                print("JOIN room - key: {}, users: {}".format(room.key, len(room.users)))
                return True

        return False
    

    def leave_room(self, user):
        for room in self.rooms:
            if (room.is_user_in_room(user)):
                room.remove_user(user)
                print("EXIT room - key: {}, users: {}".format(room.key, len(room.users)))
                if (len(room.users) == 0):
                    self.rooms.remove(room)
                    print("REMOVE room - key: {}".format(room.key))


    def generate_key(self):
        key = str(random.randint(0, 100_000)).zfill(5)
        if (key not in self.room_keys):
            self.room_keys.append(key)
            return key
        
        self.generate_key()


    def is_user_already_in_room(self, user):
        for room in self.rooms:
            if (room.is_user_in_room(user)):
                return True
            
        return False