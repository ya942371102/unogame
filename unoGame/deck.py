import tkinter as tk
from player import Player
from constant import *
from card import Card, read_cards_from_csv, get_card_by_id
import random
from PIL import ImageTk, Image
from protocal import *

BRIGHT_COLORS = ['#55afff', '#55aa55', '#ff5555', '#ffaa00']


class Deck(tk.Frame):
    def __init__(self, master: tk.Tk, width, height, bg=PLAYER_VIEW_BACKGROUND):
        super().__init__(master, width=width, height=height)
        self.master = master
        self.width = width
        self.height = height
        self.player = None
        self.background_canvas = None
        self.curr_color_canvas = None
        self.color_rectangles_in_canvas = []
        self.content_frame = None
        # self.display_canvas = None

        self.deck_image = None
        self.deck_label = None
        self.curr_card_id = None
        self.curr_card_color = None
        self.curr_card_image = None
        self.curr_card_label = None
        self.first = True
        self.my_turn = False
        self.deck_clickable = False
        self.draw_background()

        self.content_frame = tk.Frame(self.background_canvas, width=self.width)
        self.content_frame.place(x=15, y=20)

        self.cards_num = 0
        self.all_cards = read_cards_from_csv()

    def draw_background(self):
        self.background_canvas = tk.Canvas(self, width=self.width, height=self.height)
        self.background_canvas.place(x=0, y=0)
        x1, y1 = 10, 10
        x2, y2 = self.width - 10, self.height - 35
        radius = 5
        outline_color = 'black'
        self.background_canvas.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, extent=90, style="arc", width=5, outline=outline_color)
        self.background_canvas.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, extent=90, style="arc", width=5, outline=outline_color)
        self.background_canvas.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, extent=90, style="arc", width=5, outline=outline_color)
        self.background_canvas.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, extent=90, style="arc", width=5, outline=outline_color)
        self.background_canvas.create_line(x1 + radius, y1, x2 - radius, y1, width=5, fill=outline_color)
        self.background_canvas.create_line(x2, y1 + radius, x2, y2 - radius, width=5, fill=outline_color)
        self.background_canvas.create_line(x2 - radius, y2, x1 + radius, y2, width=5, fill=outline_color)
        self.background_canvas.create_line(x1, y2 - radius, x1, y1 + radius, width=5, fill=outline_color)

    def draw_color_canvas(self):
        if self.curr_color_canvas is not None:
            self.curr_color_canvas.place_forget()
        self.curr_color_canvas = tk.Canvas(self.background_canvas, width=20, height=180, bg='white' if self.curr_card_color is None else BRIGHT_COLORS[self.curr_card_color - 1])
        self.curr_color_canvas.place(x=262, y=20)

        # for color_rectangle in self.color_rectangles_in_canvas:
        #     color_rectangle.place_forget()
        # self.curr_color_canvas.create_rectangle(0, 0, 20, 20, fill=BRIGHT_COLORS[0] if self.curr_card_color is not None and self.curr_card_color - 1 == 0 else 'white')
        # self.curr_color_canvas.create_rectangle(0, 53, 20, 73, fill=BRIGHT_COLORS[1] if self.curr_card_color is not None and self.curr_card_color - 1 == 1 else 'white')
        # self.curr_color_canvas.create_rectangle(0, 106, 20, 126, fill=BRIGHT_COLORS[2] if self.curr_card_color is not None and self.curr_card_color - 1 == 2 else DARK_COLORS[2])
        # self.curr_color_canvas.create_rectangle(0, 160, 20, 180, fill=BRIGHT_COLORS[3] if self.curr_card_color is not None and self.curr_card_color - 1 == 3 else DARK_COLORS[3])

    def draw_deck(self):
        image = Image.open(UNKNOWN_CARD_image_path)
        image = image.resize((120, 180))
        self.deck_image = ImageTk.PhotoImage(image)
        self.deck_label = tk.Label(self.content_frame, image=self.deck_image)
        self.deck_label.image = self.deck_image
        self.deck_label.pack(side=tk.LEFT)
        self.deck_label.bind('<Button-1>', self.on_deck_label_click)

    def on_deck_label_click(self, event):
        if not self.my_turn or not self.deck_clickable:
            return
        print('deck label clicked')
        packet = build_draw_card_packet(self.player.name, self.player.room_name)
        self.player.client_socket.send(packet)

    def set_my_turn(self, new_turn):
        self.my_turn = new_turn

    def update_view(self, cards_num, curr_card_id, curr_card_color):
        self.curr_card_id = curr_card_id
        self.curr_card_color = curr_card_color
        if cards_num == 0:
            self.deck_label.pack_forget()
            self.deck_label = None
        else:
            if self.deck_label is None:
                self.draw_deck()
        if self.curr_card_label is not None:
            self.curr_card_label.pack_forget()
            self.curr_card_label = None
            self.curr_card_image = None
        if curr_card_id is not None:
            card = get_card_by_id(curr_card_id, self.all_cards)
            image = Image.open(card.image_name)
            image = image.resize((120, 180))
            image = ImageTk.PhotoImage(image)
            self.curr_card_label = tk.Label(self.content_frame, image=image)
            self.curr_card_label.image = image
            self.curr_card_label.pack()
        self.draw_color_canvas()

    def set_clickable(self):
        self.deck_clickable = True
        pass
