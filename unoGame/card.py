import csv
import os
from enum import Enum
from constant import CARDS_CSV


class CardColor(Enum):
    """
    Card color enumeration class
    """
    BLUE = 1
    GREEN = 2
    RED = 3
    YELLOW = 4


class CardAction(Enum):
    """
    An enumeration of the types of cards representing the action
    """
    SKIP = 1
    REVERSE = 2
    DRAW_TWO = 3


class Card:
    """
    Card class, simulate cards
    """

    def __init__(self, id, name, image_name):
        """
        Card initialization function
        :param id: The identity of the card
        :param name: The name of the card, not currently used in the program
        :param image_name: The name of the image file associated with the card
        """
        self.id = id
        self.name = name
        # All images are in the "images" folder
        self.image_name = os.path.join('images', image_name)


def read_cards_from_csv():
    """
    Read all the cards from the CSV file.
    :return: A list containing objects of all the cards.
    """
    cards = []
    with open(CARDS_CSV, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)  # skip the first line
        for row in reader:
            # For each subsequent line, read the card's name, ID, image name, and the quantity of that card.
            name, id, image_name, num = row[0], int(row[1]), row[2], int(row[3])
            for _ in range(num):
                # Add the card with the specified quantity to the "cards" list.
                cards.append(Card(id, name, image_name))
    return cards


def get_card_by_id(id, cards):
    """
    In the "cards" list, find the card corresponding to the given id.
    :param id: id
    :param cards: a list
    :return: the card whose id is id
    """
    for card in cards:
        if card.id == id:
            return card
    return None


def is_regular_card(card_id):
    """
    According to the card id to determine whether it is a regular card, that is, the card face is 0 to 9
    :param card_id: the id of a card
    :return: Ture or False
    """
    if 0 <= card_id <= 9 or 20 <= card_id <= 29 or 40 <= card_id <= 49 or 60 <= card_id <= 69:
        return True
    return False


def get_card_num(card_id):
    """
    Gets the number on the face of a regular card
    :param card_id: the id of a card
    :return: A number between 0 and 9
    """
    assert is_regular_card(card_id)
    return card_id % 10


def is_action_card(card_id):
    """
    According to the card id to determine whether it is an action card, that is, the card face is skip, reverse or draw_two
    :param card_id: the id of a card
    :return: True or False
    """
    if 10 <= card_id <= 12 or 30 <= card_id <= 32 or 50 <= card_id <= 52 or 70 <= card_id <= 72:
        return True
    return False


def get_card_action_by_id(card_id):
    """
    For an action card, get its specific action
    :param card_id: the id of a card
    :return: The corresponding enumeration value
    """
    assert is_action_card(card_id) is True
    if card_id in [10, 30, 50, 70]:
        return CardAction.SKIP.value
    elif card_id in [11, 31, 51, 71]:
        return CardAction.REVERSE.value
    else:
        return CardAction.DRAW_TWO.value


def is_wild_card(card_id):
    """
    According to the card id to determine whether it is an action card, that is, the card face is wild or wild draw four
    :param card_id: the id of a card
    :return:
    """
    if card_id == 80 or card_id == 90:
        return True
    return False


def can_play(curr_deck_card_id, curr_clicked_card_id, curr_deck_card_color=None):
    """
    The id and color of the card on the deck is known, judge whether the current clicked card id by the player can be played
    If the card on the deck is a regular or action card, we can get its color by its id directly. otherwise, if it's a wild card, the color is specified by the previous player.
    so there is curr_deck_card_color in the arguments.

    :param curr_deck_card_id:
    :param curr_clicked_card_id:
    :param curr_deck_card_color:
    :return:
    """
    # if the card on the deck is a regular card or an action card
    if is_regular_card(curr_deck_card_id) or is_action_card(curr_deck_card_id):
        # we can get the color of the card by its id, that is, the curr_deck_card_color in the arguments is ignored.

        curr_deck_card_color = get_card_color_by_id(curr_deck_card_id)
        # if the card on the deck is a regular card
        if is_regular_card(curr_deck_card_id):
            # Gets the number on the face of a regular card
            curr_deck_card_num = get_card_num(curr_deck_card_id)
            #  if the card clicked by the player is a regular card or an action card
            if is_regular_card(curr_clicked_card_id) or is_action_card(curr_clicked_card_id):
                # get the color of the card by the clicked card id,
                curr_clicked_card_color = get_card_color_by_id(curr_clicked_card_id)
                # if the clicked card is a regular card
                if is_regular_card(curr_clicked_card_id):
                    # get the number on the face of the clicked card
                    curr_clicked_card_num = get_card_num(curr_clicked_card_id)
                    # If two cards have the same number or the same color, return True
                    if curr_deck_card_num == curr_clicked_card_num or curr_deck_card_color == curr_clicked_card_color:
                        return True
                    else:
                        return False
                # if the clicked card is an action card
                else:
                    # If two cards have the same color, return True
                    if curr_deck_card_color == curr_clicked_card_color:
                        return True
                    else:
                        return False
            else:
                return True
        # if the card on the deck is an action card
        else:
            # get the action type of the card
            curr_deck_card_action_type = get_card_action_by_id(curr_deck_card_id)
            #  if the card clicked by the player is a regular card or an action card
            if is_regular_card(curr_clicked_card_id) or is_action_card(curr_clicked_card_id):
                # get the color of the card by the clicked card id,
                curr_clicked_card_color = get_card_color_by_id(curr_clicked_card_id)
                #  if the card clicked by the player is a regular card
                if is_regular_card(curr_clicked_card_id):
                    # If two cards have the same number or the same color, return True
                    if curr_deck_card_color == curr_clicked_card_color:
                        return True
                    else:
                        return False
                # if the card clicked by the player is an action card
                else:
                    curr_clicked_card_action_type = get_card_action_by_id(curr_clicked_card_id)
                    if curr_deck_card_color == curr_clicked_card_color or curr_deck_card_action_type == curr_clicked_card_action_type:
                        return True
                    else:
                        return False
            # the clicked card is wild or wild draw four
            else:
                return True
    # the card on the deck is a wild card
    else:
        assert is_wild_card(curr_deck_card_id)
        # if the card clicked by the player is a regular card or an action card
        if is_regular_card(curr_clicked_card_id) or is_action_card(curr_clicked_card_id):
            # get the color of the card by the clicked card id,
            curr_clicked_card_color = get_card_color_by_id(curr_clicked_card_id)
            # If two cards have the same color, return True
            if curr_clicked_card_color == curr_deck_card_color:
                return True
            else:
                return False
        else:
            return True


def get_card_color_by_id(card_id):
    """
    Get the color based on the card id
    :param card_id: the id of a card
    :return:
    """
    # Make sure this card is not of the wild type
    assert is_wild_card(card_id) is False
    if 0 <= card_id <= 12:
        return CardColor.BLUE.value
    elif 20 <= card_id <= 32:
        return CardColor.GREEN.value
    elif 40 <= card_id <= 52:
        return CardColor.RED.value
    elif 60 <= card_id <= 72:
        return CardColor.YELLOW.value
