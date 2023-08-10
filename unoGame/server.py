import logging
import socket
import struct
import threading
from room import Room
from player import Player
from constant import *
from protocal import *

SERVER_ADDRESS = '0.0.0.0'
SERVER_PORT = 8888


class Server:
    """
    Server class
    """

    def __init__(self):
        """
        Initialization function
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Server socket
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set the port to be reusable
        self.server_socket.bind((SERVER_ADDRESS, SERVER_PORT))  # Bind the ip address and port of the server
        self.rooms = {}  # type:dict[str,Room]

    def room_exists(self, room_name):
        """
        Determine if a room exists
        :param room_name:
        :return: True or False
        """
        return room_name in self.rooms

    def handle_client(self, client_socket: socket.socket, client_address):
        """
        Continuously receive client data and respond accordingly
        :param client_socket: client socket
        :param client_address: not used here
        :return:
        """
        while True:
            packet = None
            try:
                packet = client_socket.recv(1024)
            except ConnectionResetError:
                # If the client disconnects, remove the corresponding player from the room
                for room_name in self.rooms.keys():
                    for i in range(len(self.rooms[room_name].players)):
                        if self.rooms[room_name].players[i].client_address == client_address:
                            self.rooms[room_name].remove_player(i)
                            break
                break
            if len(packet) == 0:  # 对方关闭连接
                break
            # Extract the type of packet, the length of the room name, and the length of the username from the packet
            packet_type, len_room_name, len_player_name = struct.unpack('>III', packet[:12])
            # Continue to extract the room name and player name from the packet
            room_name = struct.unpack(f'{len_room_name}s', packet[12:12 + len_room_name])[0].decode('ASCII')
            player_name = struct.unpack(f'{len_player_name}s', packet[12 + len_room_name:12 + len_room_name + len_player_name])[0].decode('ASCII')
            # Calculate offset
            offset = 12 + len_room_name + len_player_name
            info = f'[SERVER] received client packet: packet type={packet_type} room is:{room_name} player name is:{player_name}'
            logging.info(info)
            print(info)

            if packet_type == PacketType.LOGIN.value:  # Client login request, that is, enter the room request
                if self.room_exists(room_name):  # If the room already exists
                    if self.rooms[room_name].is_full():  # If the room is full, the number of players is greater than or equal to 4
                        # Respond to the message that the room is full and return to the client
                        packet = struct.pack('>Ic', PacketType.ROOM_ALREADY_FULL.value, b'N')
                        client_socket.send(packet)
                        client_socket.close()
                        break
                    if self.rooms[room_name].started:  # If the game in the room has started
                        packet = struct.pack('>Ic', PacketType.LOGIN_FAILED_GAME_STARTED.value, b'N')
                        client_socket.send(packet)
                        client_socket.close()
                        break
                    if self.rooms[room_name].player_exists(player_name):  # If a player with the same name already exists in the room
                        packet = struct.pack('>Ic', PacketType.LOGIN_FAILED_NAME_ALREADY_EXISTS.value, b'N')
                        client_socket.send(packet)
                        break
                    else:
                        # Create a Player object and add it to the room
                        player = Player(player_name, room_name, client_socket, client_address, False)
                        self.rooms[room_name].add_player(player)
                        packet = struct.pack('>Ic', PacketType.LOGIN_SUCCESS.value, b'N')  # N: Non-administrator, common user
                        client_socket.send(packet)  # Send a response indicating successful login
                        # Package all the usernames in the room and send them to the client who just logged in
                        names_str = ''
                        for player in self.rooms[room_name].players:
                            names_str += player.name + ';'
                        names_str = names_str[:-1]
                        packet = struct.pack(f'>II{len(names_str)}s', PacketType.PLAYER_LIST.value, len(names_str), names_str.encode('ASCII'))
                        client_socket.send(packet)
                else:
                    # A room doesn't exist. Create a room
                    self.rooms[room_name] = Room(room_name)
                    player = Player(player_name, room_name, client_socket, client_address, True)
                    self.rooms[room_name].add_player(player)
                    packet = struct.pack('>Ic', PacketType.LOGIN_SUCCESS.value, b'A')  # A administrator
                    client_socket.send(packet)
            # Start the game
            elif packet_type == PacketType.START_GAME.value:
                self.rooms[room_name].reset_game(True)
                self.rooms[room_name].shuffling_cards()
            # The player plays a card.
            elif packet_type == PacketType.PLAY_CARD.value:
                # Extract the id and color of the cards played from the packet
                card_id, card_color = struct.unpack('>II', packet[offset:offset + 8])
                self.rooms[room_name].play_card(player_name, card_id, card_color)
            # The player draws a card from the deck
            elif packet_type == PacketType.DRAW_CARD.value:
                self.rooms[room_name].draw_card(player_name)
            # The player calls uno
            elif packet_type == PacketType.CALL_UNO.value:
                self.rooms[room_name].call_uno(packet)

    def start(self):
        print('server started')
        self.server_socket.listen(1)  # Start listening

        while True:
            client_socket, client_address = self.server_socket.accept()  # Client connection received
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)  # Keep the client connected continuously
            # Create a child thread that receives data from the client
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address), daemon=True)
            client_thread.start()


if __name__ == '__main__':
    # Log setting
    logging.basicConfig(
        filename='logging.txt',
        level=logging.INFO,
        format='',
        filemode='w'
    )
    # Construct a Server object and start it
    server = Server()
    server.start()
