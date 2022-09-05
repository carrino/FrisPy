#  Copyright (c) 2022 John Carrino
from pprint import pprint
from unittest import TestCase
from frispy.discs import Discs

class TestRotations(TestCase):
    def test_flight_nums(self):
        flight_nums = {"speed": 9, "turn": 0, "fade": "2", "glide": 5, "weight": 165}
        Discs.from_flight_numbers(flight_nums)

        flight_nums = {"speed": 9, "turn": 0, "fade": "2", "glide": 5}
        Discs.from_flight_numbers(flight_nums)

        flight_nums = {"speed": 12, "turn": -1, "glide": 5}
        should_be_destroyer = Discs.from_flight_numbers(flight_nums)
        destroyer = Discs.stable_destroyer
        pprint(should_be_destroyer)
