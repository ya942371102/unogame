import socket
import struct
import tkinter as tk
from tkinter import messagebox

from protocal import PacketType, build_packet_header_client
from player import Player


class LoginDialog:
    """
    Login dialog class
    """
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title('Login')
        self.root['height'] = 200
        self.root['width'] = 300
        self.label_server_ip = tk.Label(self.root, text='Server IP:', justify=tk.RIGHT, anchor='e', width=100)
        self.label_server_ip.place(x=10, y=10, width=100, height=20)

        self.var_server_ip = tk.StringVar(self.root, value='localhost')
        self.entry_server_ip = tk.Entry(self.root, width=200, textvariable=self.var_server_ip)
        self.entry_server_ip.place(x=120, y=10, width=100, height=20)

        self.label_server_port = tk.Label(self.root, text='Server Port:', justify=tk.RIGHT, anchor='e', width=100)
        self.label_server_port.place(x=10, y=40, width=100, height=20)

        self.var_server_port = tk.IntVar(self.root, value=8888)
        self.entry_server_port = tk.Entry(self.root, width=200, textvariable=self.var_server_port)
        self.entry_server_port.place(x=120, y=40, width=100, height=20)

        self.label_room = tk.Label(self.root, text='Room Name:', justify=tk.RIGHT, anchor='e', width=100)
        self.label_room.place(x=10, y=70, width=100, height=20)

        self.var_room = tk.StringVar(self.root, value='')
        self.entry_room = tk.Entry(self.root, width=200, textvariable=self.var_room)
        self.entry_room.place(x=120, y=70, width=100, height=20)

        self.label_player_name = tk.Label(self.root, text='Your Name:', justify=tk.RIGHT, anchor='e', width=100)
        self.label_player_name.place(x=10, y=100, width=100, height=20)

        self.var_player_name = tk.StringVar(self.root, value='')
        self.entry_player_name = tk.Entry(self.root, width=200, textvariable=self.var_player_name)
        self.entry_player_name.place(x=120, y=100, width=100, height=20)

        self.button_login = tk.Button(self.root, text='Login', command=self.login)
        self.button_login.place(x=100, y=130, width=80, height=20)

    def login(self):
        if not self.check_server_ip():
            messagebox.showerror(title='Error', message='Invalid ip address')
            return
        try:
            self.var_server_port.get()
        except tk.TclError:
            messagebox.showerror(title='Error', message='Empty port')
            return
        if self.var_room.get() == '':
            messagebox.showerror(title='Error', message='Empty room name')
            return
        if self.var_player_name.get() == '':
            messagebox.showerror(title='Error', message='Empty name')
            return
        self.client.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        player_name = self.var_player_name.get()
        room_name = self.var_room.get()
        try:
            self.client.client_socket.connect((self.var_server_ip.get(), self.var_server_port.get()))
            # packet = struct.pack(f'>III{len(room_name)}s{len(player_name)}s', PacketType.LOGIN.value, len(room_name), len(player_name), room_name.encode('ASCII'), player_name.encode('ASCII'))
            packet = build_packet_header_client(PacketType.LOGIN.value, player_name, room_name)
            self.client.client_socket.send(packet)
            packet = self.client.client_socket.recv(1024)
            packet_type, is_admin = struct.unpack('>Ic', packet[:5])
            is_admin = is_admin == b'A'
            if packet_type == PacketType.LOGIN_SUCCESS.value:
                self.client.player = Player(self.var_player_name.get(), self.var_room.get(), self.client.client_socket, None, is_admin)
                self.root.destroy()
            elif packet_type == PacketType.LOGIN_FAILED_GAME_STARTED.value:
                messagebox.showerror(title='Error', message='The room has started the game')
                return
            elif packet_type == PacketType.LOGIN_FAILED_NAME_ALREADY_EXISTS.value:
                messagebox.showerror(title='Error', message='The entered name already exists in the room')
                return
            elif packet_type == PacketType.ROOM_ALREADY_FULL.value:
                messagebox.showerror(title='Error', message='The room is already full')
                return

        except ConnectionRefusedError:
            messagebox.showerror(title='Error', message='Failed to connect to the server')
            return
        except ValueError:
            pass

    def check_server_ip(self):
        """
        Check whether the server address entered by the user is localhost or the correct ipv4 address
        :return:
        """
        ip = self.var_server_ip.get()
        if ip == 'localhost':
            return True
        tokens = ip.split('.')
        if len(tokens) != 4:
            return False
        for token in tokens:
            try:
                token = int(token)
                if token < 0 or token > 255:
                    return False
            except ValueError:
                return False
        return True

    def show(self):
        self.root.mainloop()
