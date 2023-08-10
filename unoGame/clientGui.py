import sys
from tkinter.ttk import Combobox
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
import webbrowser
from constant import *
from player import Player
from player_view import PlayerView
from deck import Deck
from clientBackgroundThread import receive_message
from event import Event, EventType
from protocal import *
from card import *

sys.setrecursionlimit(10000000)


class ClientGUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
        self.root.resizable(width=False, height=False)
        self.root.title('Uno Game')
        self.create_menu_bar()
        self.players_frames = []  # type:list[PlayerView]
        self.init_frames()

        self.background_listening_thread = threading.Thread(target=receive_message, args=(self.client,))
        self.background_listening_thread.daemon = True

    def show_help(self):
        webbrowser.open('gameInstructions.html')

    def show_about(self):
        messagebox.showinfo(title='about', message='Version 1.0\nAuthor: me')

    def init_frames(self):
        self.top_frame = PlayerView(self.root, width=WINDOW_WIDTH, height=TOP_HEIGHT, bg='red', position='top')
        self.top_frame.pack(side=tk.TOP)

        self.bottom_frame = PlayerView(self.root, width=WINDOW_WIDTH, height=BOTTOM_HEIGHT, bg="blue", position='bottom')
        self.bottom_frame.update_player(self.client.player)
        self.bottom_frame.pack(side=tk.BOTTOM)

        self.left_frame = PlayerView(self.root, width=LEFT_WIDTH, height=WINDOW_HEIGHT - TOP_HEIGHT - BOTTOM_HEIGHT, bg="green", position='left')
        self.left_frame.pack(side=tk.LEFT)

        self.right_frame = PlayerView(self.root, width=RIGHT_WIDTH, height=WINDOW_HEIGHT - TOP_HEIGHT - BOTTOM_HEIGHT, bg="yellow", position='right')
        self.right_frame.pack(side=tk.RIGHT)

        self.center_frame = Deck(self.root, width=WINDOW_WIDTH - LEFT_WIDTH - RIGHT_WIDTH, height=WINDOW_HEIGHT - TOP_HEIGHT - BOTTOM_HEIGHT, bg="orange")
        self.center_frame.pack(side=tk.TOP)
        self.center_frame.player = self.client.player

        self.players_frames = [self.bottom_frame, self.left_frame, self.top_frame, self.right_frame]

        for player_frame in self.players_frames:
            player_frame.set_deck(self.center_frame)

    def create_menu_bar(self):
        menu_bar = tk.Menu(self.root)
        if self.client is not None and self.client.player.is_admin:
            game_menu = tk.Menu(menu_bar, tearoff=0)
            game_menu.add_command(label='New game', command=self.new_game)
            menu_bar.add_cascade(label='Game', menu=game_menu)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label='How to play', command=self.show_help)
        help_menu.add_command(label='About', command=self.show_about)
        menu_bar.add_cascade(label='Help', menu=help_menu)
        # self.root.config(menu=menu_bar)
        self.root['menu'] = menu_bar

    def new_game(self):
        packet = get_start_game_packet_client(self.client.player.name, self.client.player.room_name)
        self.client.player.client_socket.send(packet)

    def show(self):
        self.background_listening_thread.start()
        self.root.after(100, self.update_ui)
        self.root.mainloop()

    def update_ui(self):
        while self.client is not None and not self.client.events.empty():
            event = self.client.events.get(timeout=0.1)  # type:Event
            if event.event_type == EventType.UPDATE_PLAYER_LIST:
                myself_id = event.updated_player_list.index(self.client.player.name)
                players = [self.client.player, None, None, None]
                for i, name in enumerate(event.updated_player_list):
                    if i == myself_id:
                        continue
                    players[i - myself_id] = Player(name)
                for i, name in enumerate(players):
                    self.players_frames[i].update_player(players[i])
            elif event.event_type == EventType.START_GAME:
                self.center_frame.first = True
                for player_view in self.players_frames:
                    player = player_view.player
                    if player is not None:
                        player.cards_in_hand.clear()
                        player_view.update_view()
            elif event.event_type == EventType.GAME_STATE:
                print(event.cards_info)
                first = event.cards_info['first']
                self.center_frame.first = first
                self.center_frame.update_view(event.cards_info['cards_num'], event.cards_info['curr_card_id'], event.cards_info['curr_card_color'])

                for player_info in event.cards_info['players']:
                    for player_view in self.players_frames:
                        if player_view.player is not None and player_view.player.name == player_info['name']:
                            player_view.turn = player_info['turn']
                            player_view.player.cards_in_hand = [get_card_by_id(card_id, self.center_frame.all_cards) for card_id in player_info['cards']]
                            player_view.player.score = player_info['score']
                            player_view.update_view()
                self.center_frame.deck_clickable = False
                if self.bottom_frame.turn is True:
                    self.center_frame.my_turn = True
                    player_can_play = False
                    for card in self.bottom_frame.player.cards_in_hand:
                        card_id = card.id
                        if can_play(self.center_frame.curr_card_id, card_id, self.center_frame.curr_card_color):
                            player_can_play = True
                            break
                    if not player_can_play:
                        self.center_frame.set_clickable()
                else:
                    self.center_frame.my_turn = False

                if self.center_frame.first and event.cards_info['curr_card_id'] == 80:
                    choice = simpledialog.askstring('Select an color', 'Input "b", "g", "r", or "y" for blue, green, red, yellow respectively:')
                    while not choice or choice not in ['b', 'g', 'r', 'y']:
                        choice = simpledialog.askstring('Select an color', 'Input "b", "g", "r", or "y" for blue, green, red, yellow respectively:')
                    self.center_frame.curr_card_color = ['b', 'g', 'r', 'y'].index(choice) + 1
            elif event.event_type == EventType.CALL_UNO:
                for player_view in self.players_frames:
                    if player_view.player is not None and player_view.player.name == event.player_name:
                        player_view.call_uno()
            elif event.event_type == EventType.FINAL_WIN:
                for player_view in self.players_frames:
                    if player_view.player is not None:
                        player_view.player.cards_in_hand.clear()
                        player_view.turn = False
                        player_view.update_view()
                messagebox.showinfo('game over', message=f'The winner is {event.player_name}')
        self.root.after(100, self.update_ui)


if __name__ == '__main__':
    gui = ClientGUI(None)
    gui.show()

