import random
import struct
from typing import Dict

from card import *
from constant import CARDS_CSV
from player import Player
from protocal import *


class Room:
    """
    Room class
    """

    def __init__(self, name=None):
        self.name = name
        self.players = []  # type:list[Player] # The players in the room
        self.cards = []  # cards in Deck
        self.discard_pile = []  # Discard Pile
        self.curr_card = None  # type:Card # The current card, which can also be said to be the last card played, That's the top of the discard pile
        self.curr_card_color = None  # the color of the current card
        self.curr_player = None  # type:Player # The current player, that is, the player who is going to play
        self.clockwise = True  # Clockwise(True) or counterclockwise(False)
        self.started = False  # Is the game started?

    def is_full(self):
        """
        Determine if the room is full
        :return: True or False
        """
        return len(self.players) >= 4

    def player_exists(self, player_name):
        """
        Determine if the player's name already exists
        :param player_name:
        :return: True or False
        """

        for p in self.players:
            if p.name == player_name:
                return True
        return False

    def add_player(self, player):
        """
        Add a player
        :param player: a new player
        :return:
        """
        player.set_room(self)
        self.players.append(player)
        # Because the player in the room has updated, notify the other players
        names_str = ''
        for player in self.players:
            names_str += player.name + ';'
        names_str = names_str[:-1]
        packet = struct.pack(f'>II{len(names_str)}s', PacketType.PLAYER_LIST.value, len(names_str), names_str.encode('ASCII'))
        for p in self.players:
            if p.name != player.name:
                p.client_socket.send(packet)

    def shuffling_cards(self):
        """
        shuffle cards
        :return:
        """
        self.cards = read_cards_from_csv()  # type:list[Card] # Re-read all card information
        random.shuffle(self.cards)  # Shuffle the order of the cards
        self.curr_player = self.get_admin_player()  # The next player to play is the caretaker of the room
        # Each player is dealt seven cards
        for i in range(7):
            for player in self.players:
                card = self.cards.pop()
                player.cards_in_hand.append(card)
        self.started = True

        # Start discarding the pile
        self.curr_card = self.cards.pop()
        self.discard_pile.append(self.curr_card)

        if self.curr_card.id in [10, 30, 50, 70]:
            # the current player misses a turn
            self.curr_player = self.get_next_player()
        elif self.curr_card.id in [11, 31, 51, 71]:
            # play proceeds counterclockwise
            self.clockwise = False
        elif self.curr_card.id in [12, 32, 52, 72]:
            # the player to the left of the current player draws two cards and misses a turn
            self.curr_player = self.get_next_player()
            self.curr_player.cards_in_hand.append(self.cards.pop())
            self.curr_player.cards_in_hand.append(self.cards.pop())
            self.curr_player = self.get_next_player()
        elif self.curr_card.id == 80:
            pass
        elif self.curr_card.id == 90:
            # Card is returned to the deck, then a new card is laid down into the discard pile (deck may be reshuffled first if needed)
            while self.curr_card.id == 90:
                self.discard_pile.remove(self.curr_card)
                self.cards.append(self.curr_card)
                random.shuffle(self.cards)
                self.curr_card = self.cards.pop()
                self.discard_pile.append(self.curr_card)
        if not is_wild_card(self.curr_card.id):
            self.curr_card_color = get_card_color_by_id(self.curr_card.id)
        else:
            self.curr_card_color = 0
        #  Sends the current game state information to each player
        for player in self.players:
            packet = get_game_state_packet_server(self, True)
            player.client_socket.send(packet)

    def get_admin_player(self):
        for player in self.players:
            if player.is_admin is True:
                return player

    def get_next_player(self):
        """
        Get the next player.
        :return:
        """
        if self.curr_player is None:
            return self.get_admin_player()
        else:
            if self.clockwise:
                return self.players[(self.players.index(self.curr_player) + 1) % len(self.players)]
            else:
                return self.players[(self.players.index(self.curr_player) + len(self.players) - 1) % len(self.players)]

    def reset_game(self, clean_score=False):
        """
        reset the game.
        :param clean_score: whether score records are cleared
        :return:
        """

        self.started = True
        self.curr_card = None
        self.curr_player = None
        self.clockwise = True
        self.discard_pile.clear()
        for player in self.players:
            if clean_score:
                player.score = 0
            player.cards_in_hand.clear()
        packet = get_start_game_packet_server()
        for player in self.players:
            player.client_socket.send(packet)

    def play_card(self, player_name, card_id, card_color):
        played_card = None
        assert self.curr_player.name == player_name
        # Removes the card played by the player from the cards in his hand
        for card in self.curr_player.cards_in_hand:
            if card.id == card_id:
                played_card = card
                self.curr_player.cards_in_hand.remove(card)
                break
        assert played_card is not None

        self.curr_card = played_card
        self.curr_card_color = card_color
        # Add to discard pile
        self.discard_pile.append(self.curr_card)
        # Check if the game is over
        if self.check_game_over():
            # Calculate the score for the winner
            self.calculate_score_for_winner()
            # Check if the player has more than 500 points
            final_winner = self.check_500()
            #  if it is,
            if final_winner is not None:
                # Sends a game over message to all clients
                packet = build_game_over_packet_server(final_winner)
                for player in self.players:
                    player.client_socket.send(packet)
                return
            # Move on to the next round
            self.reset_game(False)
            self.shuffling_cards()
            return
        # If a regular card is played,
        if is_regular_card(self.curr_card.id):
            # The next player to play is the next player
            self.curr_player = self.get_next_player()
        # If it's an action card
        elif is_action_card(self.curr_card.id):
            # Get the action type
            action_type = get_card_action_by_id(self.curr_card.id)
            # If it's a skip card
            if action_type == CardAction.SKIP.value:
                # The next player to play is the next player after the next
                self.curr_player = self.get_next_player()
                self.curr_player = self.get_next_player()
            # if it's a reverse card
            elif action_type == CardAction.REVERSE.value:
                # Reverse clockwise,
                self.clockwise = not self.clockwise
                self.curr_player = self.get_next_player()
            # if it's a draw two card
            elif action_type == CardAction.DRAW_TWO.value:
                # Move on to the next player first
                self.curr_player = self.get_next_player()
                # Deal two cards to this player
                self.check_cards()
                self.curr_player.cards_in_hand.append(self.cards.pop())
                self.check_cards()
                self.curr_player.cards_in_hand.append(self.cards.pop())
                # Move past this player and on to the next player
                self.curr_player = self.get_next_player()
        else:
            assert is_wild_card(self.curr_card.id)
            #
            if self.curr_card.id == 80:
                self.curr_card_color = card_color
                self.curr_player = self.get_next_player()
            else:
                self.curr_player = self.get_next_player()
                for _ in range(4):
                    self.check_cards()
                    self.curr_player.cards_in_hand.append(self.cards.pop())
                self.curr_player = self.get_next_player()
        packet = get_game_state_packet_server(self)
        for player in self.players:
            player.client_socket.send(packet)

    def remove_player(self, i):
        self.players.pop(i)

    def draw_card(self, player_name):
        assert player_name == self.curr_player.name
        self.check_cards()
        self.curr_player.cards_in_hand.append(self.cards.pop())
        player_can_play = False
        for card in self.curr_player.cards_in_hand:
            card_id = card.id
            if can_play(self.curr_card.id, card_id, self.curr_card_color):
                player_can_play = True
                break
        if not player_can_play:
            self.curr_player = self.get_next_player()
        packet = get_game_state_packet_server(self)
        for player in self.players:
            player.client_socket.send(packet)

    def call_uno(self, packet):
        for player in self.players:
            player.client_socket.send(packet)

    def check_game_over(self):
        if len(self.curr_player.cards_in_hand) == 0:
            return True
        return False

    def calculate_score_for_winner(self):
        score = 0
        for player in self.players:
            if player == self.curr_player:
                continue
            score += self.calculate_score_for_player(player)
        self.curr_player.score += score

    def calculate_score_for_player(self, player):
        score = 0
        for card in player.cards_in_hand:
            card_id = card.id
            if is_regular_card(card_id):
                score += card_id % 10
            elif is_action_card(card_id):
                score += 20
            else:
                score += 50
        return score

    def check_500(self):
        for player in self.players:
            if player.score >= 500:
                return player
        return None

    def check_cards(self):
        if len(self.cards) == 0:
            for card in self.discard_pile:
                if card != self.curr_card:
                    self.cards.append(card)
            random.shuffle(self.cards)
