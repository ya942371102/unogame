import socket


class Player:
    def __init__(self, name=None, room_name=None, client_socket=None, client_address=None, is_admin=False):
        self.name = name #type:str
        self.client_socket = client_socket  # type:socket.socket
        self.client_address = client_address
        self.room_name = room_name
        self.room = None
        self.score = 0
        self.cards_in_hand = []

        self.is_admin = is_admin

    def set_room(self, room):
        self.room = room

    def __eq__(self, other):
        return self.name == other.name
