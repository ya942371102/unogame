import unittest

from room import Room
from constant import *


class TestRoom(unittest.TestCase):
    def test_1(self):
        room = Room('room1')
        room.reset_cards()
        self.assertTrue(len(room.cards) == 108)


if __name__ == '__main__':
    unittest.main()
