from enum import Enum


class EventType(Enum):
    UPDATE_PLAYER_LIST = 1
    START_GAME = 2
    GAME_STATE = 3
    CALL_UNO = 4
    FINAL_WIN = 5


class Event:
    def __init__(self, event_type):
        self.event_type = event_type
        self.updated_player_list = []  # type:list[str]
        self.cards_info = dict()
        self.player_name = None
