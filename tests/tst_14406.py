# coding: UTF-8
import logging
import struct
import time
import unittest
import json
from datetime import datetime, timedelta

from framework_helper import logger

################################
# get the code
with open('framework_helper.py', 'r') as f1, open('../src/14406_tibber_sets.py', 'r') as f2:
    framework_code = f1.read()
    debug_code = f2.read()

exec (framework_code + debug_code)


################################################################################

class TestPriceInfo(unittest.TestCase):

    def setUp(self):
        # This data will be used in each test case
        self.data_cheap = {
            "startsAt": "2024-10-01T12:00:00.000+02:00",
            "total": 50.0,
            "level": "CHEAP"
        }
        self.data_expensive = {
            "startsAt": "2024-10-01T13:00:00.000+02:00.000+02:00",
            "total": 150.0,
            "level": "EXPENSIVE"
        }

        self.price_info_cheap = PriceInfo(self.data_cheap, duration_min=60)
        self.price_info_expensive = PriceInfo(self.data_expensive, duration_min=90)

    def test_initialization(self):
        # Test if the initialization works as expected
        self.assertEqual(self.price_info_cheap.start, datetime(2024, 10, 1, 12, 0, 0))
        self.assertEqual(self.price_info_cheap.stop, datetime(2024, 10, 1, 13, 0, 0))
        self.assertEqual(self.price_info_cheap.price, 50.0)
        self.assertEqual(self.price_info_cheap.level, "CHEAP")

    def test_comparisons(self):
        # Test __gt__ and __lt__ methods
        self.assertTrue(self.price_info_expensive > self.price_info_cheap)
        self.assertFalse(self.price_info_cheap > self.price_info_expensive)
        self.assertTrue(self.price_info_cheap < self.price_info_expensive)
        self.assertFalse(self.price_info_expensive < self.price_info_cheap)

    def test_get_start_s(self):
        # Test get_start_s method
        start_time_cheap = self.price_info_cheap.get_start_s()
        start_time_expensive = self.price_info_expensive.get_start_s()

        self.assertEqual(start_time_cheap, "12:00")
        self.assertEqual(start_time_expensive, "13:00")

    def test_get_stop_s(self):
        # Test get_stop_s method
        stop_time_cheap = self.price_info_cheap.get_stop_s()
        stop_time_expensive = self.price_info_expensive.get_stop_s()

        self.assertEqual(stop_time_cheap, "13:00")
        self.assertEqual(stop_time_expensive, "14:30")  # Since duration is 90 min

    def test_get_level(self):
        # Test get_level method
        self.assertEqual(self.price_info_cheap.get_level(), -1)
        self.assertEqual(self.price_info_expensive.get_level(), 1)


class TestPriceList(unittest.TestCase):

    def setUp(self):
        # Initialize PriceInfo objects
        self.data_cheap = {
            "startsAt": "2024-10-01T12:00:00.000+02:00",
            "total": 50.0,
            "level": "CHEAP"
        }
        self.data_expensive = {
            "startsAt": "2024-10-01T13:00:00.000+02:00",
            "total": 150.0,
            "level": "EXPENSIVE"
        }
        self.data_midrange = {
            "startsAt": "2024-10-01T12:30:00.000+02:00",
            "total": 100.0,
            "level": "MIDRANGE"
        }

        self.price_info_cheap = PriceInfo(self.data_cheap, duration_min=60)
        self.price_info_expensive = PriceInfo(self.data_expensive, duration_min=60)
        self.price_info_midrange = PriceInfo(self.data_midrange, duration_min=60)
        self.price_list = PriceList()

    def test_get_sets(self):
        data_0 = {"startsAt": "2024-10-01T12:00:00", "total": 30.0, "level": "CHEAP"}
        data_1 = {"startsAt": "2024-10-01T13:00:00", "total": 30.0, "level": "EXPENSIVE"}
        data_2 = {"startsAt": "2024-10-01T14:00:00", "total": 30.0, "level": "EXPENSIVE"}
        data_3 = {"startsAt": "2024-10-01T15:00:00", "total": 30.0, "level": "CHEAP"}
        data_4 = {"startsAt": "2024-10-01T16:00:00", "total": 30.0, "level": "VERY CHEAP"}
        data_5 = {"startsAt": "2024-10-01T17:00:00", "total": 30.0, "level": "NORMAL" }
        data_6 = {"startsAt": "2024-10-01T18:00:00", "total": 30.0, "level": "CHEAP"}
        data_7 = {"startsAt": "2024-10-01T19:00:00", "total": 30.0, "level": "VERY CHEAP"}

        price_list = PriceList()
        price_list.add(PriceInfo(data_0))
        price_list.add(PriceInfo(data_1))
        price_list.add(PriceInfo(data_2))
        price_list.add(PriceInfo(data_3))
        price_list.add(PriceInfo(data_4))
        price_list.add(PriceInfo(data_5))
        price_list.add(PriceInfo(data_6))
        price_list.add(PriceInfo(data_7))

        price_list.create_intervals(datetime(year=2024, month=9, day=30))

        self.assertEqual(3, len(price_list.cheap))
        self.assertEqual(1, len(price_list.expensive))
        self.assertEqual(1, len(price_list.normal))

    def test_add_method(self):
        # Add PriceInfo objects to PriceList and check sorting order
        self.price_list.add(self.price_info_expensive)
        self.price_list.add(self.price_info_cheap)
        self.price_list.add(self.price_info_midrange)

        # Ensure the prices are sorted by start time
        sorted_prices = self.price_list.prices
        self.assertEqual(sorted_prices[0], self.price_info_cheap)
        self.assertEqual(sorted_prices[1], self.price_info_midrange)
        self.assertEqual(sorted_prices[2], self.price_info_expensive)

    def test_bubble_sort_logic(self):
        # Test sorting logic of _bubble_sort separately
        prices_unsorted = [self.price_info_expensive, self.price_info_cheap, self.price_info_midrange]
        sorted_prices = self.price_list._bubble_sort(prices_unsorted)

        # Ensure the list is sorted correctly
        self.assertEqual(sorted_prices[0], self.price_info_cheap)
        self.assertEqual(sorted_prices[1], self.price_info_midrange)
        self.assertEqual(sorted_prices[2], self.price_info_expensive)


class TestSequenceFunctions(unittest.TestCase):
    cred = 0
    tst = 0

    def setUp(self):
        print("\n###setUp")

        self.json_data = '''
        [
            {
                "startsAt":"2024-10-03T00:00:00.000+02:00", "total":0.3, "level":"NORMAL"
            },
            {
                "startsAt":"2024-10-03T01:00:00.000+02:00", "total":0.3, "level":"CHEAP"
            },
            {
                "startsAt":"2024-10-03T02:00:00.000+02:00", "total":0.1, "level":"VERY CHEAP"
            },
            {
                "startsAt":"2024-10-03T03:00:00.000+02:00", "total":0.3, "level":"EXPENSIVE"
            },
            {
                "startsAt":"2024-10-03T04:00:00.000+02:00", "total":0.3, "level":"EXPENSIVE"
            },
            {
                "startsAt":"2024-10-03T05:00:00.000+02:00", "total":0.2, "level":"VERY CHEAP"
            },
            {
                "startsAt":"2024-10-03T06:00:00.000+02:00", "total":0.2, "level":"VERY CHEAP"
            },
            {
                "startsAt":"2024-10-03T07:00:00.000+02:00", "total":0.31, "level":"EXPENSIVE"
            }
        ]
        '''

        with open("credentials.txt") as f:
            self.cred = json.load(f)

        self.tst = Tibber_sets14406(0)
        self.tst.debug = True
        self.tst.debug_input_value[self.tst.PIN_I_CHEAP] = 0.05
        self.tst.debug_input_value[self.tst.PIN_I_EXPENSIVE] = 0.99
        self.tst.debug_input_value[self.tst.PIN_I_NORMAL_INTERVALL] = 0

        self.tst.interval_update_time_control = 0
        self.tst.interval_update = 0

        logger.setLevel(logging.INFO)

        self.tst.on_init()

    def test_pre_process_prices(self):
        print("\n\n### test_5")
        self.tst.debug_input_value[self.tst.PIN_I_CHEAP] = 0.05
        self.tst.debug_input_value[self.tst.PIN_I_EXPENSIVE] = 0.99
        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TODAY] = '[{"startsAt": "2024-10-09T00:00:00.000+02:00", "total": 0.2354, "level": "CHEAP"}, {"startsAt": "2024-10-09T01:00:00.000+02:00", "total": 0.2331, "level": "NORMAL"}, {"startsAt": "2024-10-09T02:00:00.000+02:00", "total": 0.2301, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T03:00:00.000+02:00", "total": 0.2331, "level": "NORMAL"}]'
        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TOMORROW] = "[]"
        self.tst.debug_now = datetime(year=2024, month=10, day=1, hour=00, minute=00)

        print("### 1")
        self.tst.debug_input_value[self.tst.PIN_I_NORMAL_INTERVALL] = 0
        res = self.tst.pre_process_prices()
        print("### res")
        print(json.dumps(res, indent=2))
        solution = {"2024-10-09T00:00:00.000+02:00": {"startsAt": "2024-10-09T00:00:00.000+02:00", "total": 0.2354, "level": "CHEAP"}, "2024-10-09T01:00:00.000+02:00": {"startsAt": "2024-10-09T01:00:00.000+02:00", "total": 0.2331, "level": "NORMAL"}, "2024-10-09T02:00:00.000+02:00": {"startsAt": "2024-10-09T02:00:00.000+02:00", "total": 0.2301, "level": "EXPENSIVE"}, "2024-10-09T03:00:00.000+02:00": {"startsAt": "2024-10-09T03:00:00.000+02:00", "total": 0.2331, "level": "NORMAL"}}
        self.assertEqual(solution, res)

        print("### 2")
        self.tst.debug_input_value[self.tst.PIN_I_NORMAL_INTERVALL] = -1
        res = self.tst.pre_process_prices()
        solution = {"2024-10-09T00:00:00.000+02:00": {"startsAt": "2024-10-09T00:00:00.000+02:00", "total": 0.2354, "level": "CHEAP"}, "2024-10-09T01:00:00.000+02:00": {"startsAt": "2024-10-09T01:00:00.000+02:00", "total": 0.2331, "level": "CHEAP"}, "2024-10-09T02:00:00.000+02:00": {"startsAt": "2024-10-09T02:00:00.000+02:00", "total": 0.2301, "level": "EXPENSIVE"}, "2024-10-09T03:00:00.000+02:00": {"startsAt": "2024-10-09T03:00:00.000+02:00", "total": 0.2331, "level": "CHEAP"}}
        self.assertEqual(solution, res)

        print("### 3")
        self.tst.debug_input_value[self.tst.PIN_I_NORMAL_INTERVALL] = 1
        res = self.tst.pre_process_prices()
        solution = {"2024-10-09T00:00:00.000+02:00": {"startsAt": "2024-10-09T00:00:00.000+02:00", "total": 0.2354, "level": "CHEAP"}, "2024-10-09T01:00:00.000+02:00": {"startsAt": "2024-10-09T01:00:00.000+02:00", "total": 0.2331, "level": "EXPENSIVE"}, "2024-10-09T02:00:00.000+02:00": {"startsAt": "2024-10-09T02:00:00.000+02:00", "total": 0.2301, "level": "EXPENSIVE"}, "2024-10-09T03:00:00.000+02:00": {"startsAt": "2024-10-09T03:00:00.000+02:00", "total": 0.2331, "level": "EXPENSIVE"}}
        self.assertEqual(solution, res)

    def test_date(self):
        old = datetime(year=2024, month=10, day=1)
        young = datetime(year=2024, month=10, day=2)

        print(old < young)  # True

    def test_1(self):
        print("### test_1")
        self.tst.debug_input_value[self.tst.PIN_I_CHEAP] = 0.05
        self.tst.debug_input_value[self.tst.PIN_I_EXPENSIVE] = 0.99
        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TODAY] = self.json_data

        self.tst.interval_update_time_control = 2
        self.tst.update_time_control()

        self.assertEqual("01:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_START])
        self.assertEqual("03:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_STOP])
        self.assertEqual("05:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_START])
        self.assertEqual("07:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_STOP])

        self.assertEqual("03:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_START])
        self.assertEqual("05:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_STOP])
        self.assertEqual("07:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_START])
        self.assertEqual("08:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_STOP])

    def test_empty(self):
        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TODAY] = []
        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TOMORROW] = []
        self.tst.update_time_control()

    def test_2(self):
        today = '[{"startsAt": "2024-10-08T00:00:00.000+02:00", "total": 0.2478, "level": "NORMAL"}, {"startsAt": "2024-10-08T01:00:00.000+02:00", "total": 0.2415, "level": "NORMAL"}, {"startsAt": "2024-10-08T02:00:00.000+02:00", "total": 0.2379, "level": "NORMAL"}, {"startsAt": "2024-10-08T03:00:00.000+02:00", "total": 0.2327, "level": "NORMAL"}, {"startsAt": "2024-10-08T04:00:00.000+02:00", "total": 0.2328, "level": "NORMAL"}, {"startsAt": "2024-10-08T05:00:00.000+02:00", "total": 0.242, "level": "NORMAL"}, {"startsAt": "2024-10-08T06:00:00.000+02:00", "total": 0.264, "level": "NORMAL"}, {"startsAt": "2024-10-08T07:00:00.000+02:00", "total": 0.2931, "level": "EXPENSIVE"}, {"startsAt": "2024-10-08T08:00:00.000+02:00", "total": 0.2882, "level": "EXPENSIVE"}, {"startsAt": "2024-10-08T09:00:00.000+02:00", "total": 0.2629, "level": "NORMAL"}, {"startsAt": "2024-10-08T10:00:00.000+02:00", "total": 0.2573, "level": "NORMAL"}, {"startsAt": "2024-10-08T11:00:00.000+02:00", "total": 0.2575, "level": "NORMAL"}, {"startsAt": "2024-10-08T12:00:00.000+02:00", "total": 0.2522, "level": "NORMAL"}, {"startsAt": "2024-10-08T13:00:00.000+02:00", "total": 0.2599, "level": "NORMAL"}, {"startsAt": "2024-10-08T14:00:00.000+02:00", "total": 0.2669, "level": "NORMAL"}, {"startsAt": "2024-10-08T15:00:00.000+02:00", "total": 0.2689, "level": "NORMAL"}, {"startsAt": "2024-10-08T16:00:00.000+02:00", "total": 0.2821, "level": "NORMAL"}, {"startsAt": "2024-10-08T17:00:00.000+02:00", "total": 0.3121, "level": "EXPENSIVE"}, {"startsAt": "2024-10-08T18:00:00.000+02:00", "total": 0.3483, "level": "EXPENSIVE"}, {"startsAt": "2024-10-08T19:00:00.000+02:00", "total": 0.3619, "level": "VERY_EXPENSIVE"}, {"startsAt": "2024-10-08T20:00:00.000+02:00", "total": 0.2979, "level": "EXPENSIVE"}, {"startsAt": "2024-10-08T21:00:00.000+02:00", "total": 0.2747, "level": "NORMAL"}, {"startsAt": "2024-10-08T22:00:00.000+02:00", "total": 0.2648, "level": "NORMAL"}, {"startsAt": "2024-10-08T23:00:00.000+02:00", "total": 0.2422, "level": "NORMAL"}]'
        tomorrow = '[{"startsAt": "2024-10-09T00:00:00.000+02:00", "total": 0.2354, "level": "NORMAL"}, {"startsAt": "2024-10-09T01:00:00.000+02:00", "total": 0.2331, "level": "NORMAL"}, {"startsAt": "2024-10-09T02:00:00.000+02:00", "total": 0.2301, "level": "NORMAL"}, {"startsAt": "2024-10-09T03:00:00.000+02:00", "total": 0.2264, "level": "CHEAP"}, {"startsAt": "2024-10-09T04:00:00.000+02:00", "total": 0.2299, "level": "NORMAL"}, {"startsAt": "2024-10-09T05:00:00.000+02:00", "total": 0.2377, "level": "NORMAL"}, {"startsAt": "2024-10-09T06:00:00.000+02:00", "total": 0.2649, "level": "NORMAL"}, {"startsAt": "2024-10-09T07:00:00.000+02:00", "total": 0.294, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T08:00:00.000+02:00", "total": 0.2938, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T09:00:00.000+02:00", "total": 0.2653, "level": "NORMAL"}, {"startsAt": "2024-10-09T10:00:00.000+02:00", "total": 0.2475, "level": "NORMAL"}, {"startsAt": "2024-10-09T11:00:00.000+02:00", "total": 0.233, "level": "NORMAL"}, {"startsAt": "2024-10-09T12:00:00.000+02:00", "total": 0.2329, "level": "NORMAL"}, {"startsAt": "2024-10-09T13:00:00.000+02:00", "total": 0.233, "level": "NORMAL"}, {"startsAt": "2024-10-09T14:00:00.000+02:00", "total": 0.2422, "level": "NORMAL"}, {"startsAt": "2024-10-09T15:00:00.000+02:00", "total": 0.2536, "level": "NORMAL"}, {"startsAt": "2024-10-09T16:00:00.000+02:00", "total": 0.2748, "level": "NORMAL"}, {"startsAt": "2024-10-09T17:00:00.000+02:00", "total": 0.3015, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T18:00:00.000+02:00", "total": 0.3075, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T19:00:00.000+02:00", "total": 0.313, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T20:00:00.000+02:00", "total": 0.2939, "level": "NORMAL"}, {"startsAt": "2024-10-09T21:00:00.000+02:00", "total": 0.2757, "level": "NORMAL"}, {"startsAt": "2024-10-09T22:00:00.000+02:00", "total": 0.2749, "level": "NORMAL"}, {"startsAt": "2024-10-09T23:00:00.000+02:00", "total": 0.2597, "level": "NORMAL"}]'
        self.tst.debug_input_value[self.tst.PIN_I_CHEAP] = 0.05
        self.tst.debug_input_value[self.tst.PIN_I_EXPENSIVE] = 0.99
        self.tst.debug_now = datetime(year=2024, month=10, day=8, hour=15)

        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TODAY] = today
        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TOMORROW] = tomorrow

        self.tst.interval_update_time_control = 2
        self.tst.on_input_value(self.tst.PIN_I_PRICES_TODAY, 0.01)

        self.assertEqual("03:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_START])
        self.assertEqual("04:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_STOP])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_START])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_STOP])

        self.assertEqual("17:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_START])
        self.assertEqual("21:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_STOP])
        self.assertEqual("07:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_START])
        self.assertEqual("09:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_STOP])

    def test_3(self):
        today = ('[{"startsAt": "2024-10-09T00:00:00.000+02:00", "total": 0.2354, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T01:00:00.000+02:00", "total": 0.2331, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T02:00:00.000+02:00", "total": 0.2301, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T03:00:00.000+02:00", "total": 0.2264, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T04:00:00.000+02:00", "total": 0.2299, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T05:00:00.000+02:00", "total": 0.2377, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T06:00:00.000+02:00", "total": 0.2649, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T07:00:00.000+02:00", "total": 0.294, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T08:00:00.000+02:00", "total": 0.2938, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T09:00:00.000+02:00", "total": 0.2653, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T10:00:00.000+02:00", "total": 0.2475, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T11:00:00.000+02:00", "total": 0.233, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T12:00:00.000+02:00", "total": 0.2329, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T13:00:00.000+02:00", "total": 0.233, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T14:00:00.000+02:00", "total": 0.2422, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T15:00:00.000+02:00", "total": 0.2536, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T16:00:00.000+02:00", "total": 0.2748, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T17:00:00.000+02:00", "total": 0.3015, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T18:00:00.000+02:00", "total": 0.3075, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T19:00:00.000+02:00", "total": 0.313, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T20:00:00.000+02:00", "total": 0.2939, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T21:00:00.000+02:00", "total": 0.2757, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T22:00:00.000+02:00", "total": 0.2749, "level": "CHEAP"}, '
                 '{"startsAt": "2024-10-09T23:00:00.000+02:00", "total": 0.2597, "level": "CHEAP"}]')
        tomorrow = '[]'
        self.tst.debug_input_value[self.tst.PIN_I_CHEAP] = 0.05
        self.tst.debug_input_value[self.tst.PIN_I_EXPENSIVE] = 0.99
        self.tst.debug_input_value[self.tst.PIN_I_NORMAL_INTERVALL] = 0
        self.tst.debug_now = datetime(year=2024, month=10, day=9, hour=7, minute=15)

        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TODAY] = today
        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TOMORROW] = tomorrow

        self.tst.interval_update_time_control = 2
        self.tst.update_time_control()

    def test_4(self):
        today = '[{"startsAt": "2024-10-08T00:00:00.000+02:00", "total": 0.2478, "level": "NORMAL"}, {"startsAt": "2024-10-08T01:00:00.000+02:00", "total": 0.2415, "level": "NORMAL"}, {"startsAt": "2024-10-08T02:00:00.000+02:00", "total": 0.2379, "level": "NORMAL"}, {"startsAt": "2024-10-08T03:00:00.000+02:00", "total": 0.2327, "level": "NORMAL"}, {"startsAt": "2024-10-08T04:00:00.000+02:00", "total": 0.2328, "level": "NORMAL"}, {"startsAt": "2024-10-08T05:00:00.000+02:00", "total": 0.242, "level": "NORMAL"}, {"startsAt": "2024-10-08T06:00:00.000+02:00", "total": 0.264, "level": "NORMAL"}, {"startsAt": "2024-10-08T07:00:00.000+02:00", "total": 0.2931, "level": "EXPENSIVE"}, {"startsAt": "2024-10-08T08:00:00.000+02:00", "total": 0.2882, "level": "EXPENSIVE"}, {"startsAt": "2024-10-08T09:00:00.000+02:00", "total": 0.2629, "level": "NORMAL"}, {"startsAt": "2024-10-08T10:00:00.000+02:00", "total": 0.2573, "level": "NORMAL"}, {"startsAt": "2024-10-08T11:00:00.000+02:00", "total": 0.2575, "level": "NORMAL"}, {"startsAt": "2024-10-08T12:00:00.000+02:00", "total": 0.2522, "level": "NORMAL"}, {"startsAt": "2024-10-08T13:00:00.000+02:00", "total": 0.2599, "level": "NORMAL"}, {"startsAt": "2024-10-08T14:00:00.000+02:00", "total": 0.2669, "level": "NORMAL"}, {"startsAt": "2024-10-08T15:00:00.000+02:00", "total": 0.2689, "level": "NORMAL"}, {"startsAt": "2024-10-08T16:00:00.000+02:00", "total": 0.2821, "level": "NORMAL"}, {"startsAt": "2024-10-08T17:00:00.000+02:00", "total": 0.3121, "level": "EXPENSIVE"}, {"startsAt": "2024-10-08T18:00:00.000+02:00", "total": 0.3483, "level": "EXPENSIVE"}, {"startsAt": "2024-10-08T19:00:00.000+02:00", "total": 0.3619, "level": "VERY_EXPENSIVE"}, {"startsAt": "2024-10-08T20:00:00.000+02:00", "total": 0.2979, "level": "EXPENSIVE"}, {"startsAt": "2024-10-08T21:00:00.000+02:00", "total": 0.2747, "level": "NORMAL"}, {"startsAt": "2024-10-08T22:00:00.000+02:00", "total": 0.2648, "level": "NORMAL"}, {"startsAt": "2024-10-08T23:00:00.000+02:00", "total": 0.2422, "level": "NORMAL"}]'
        tomorrow = '[{"startsAt": "2024-10-09T00:00:00.000+02:00", "total": 0.2354, "level": "NORMAL"}, {"startsAt": "2024-10-09T01:00:00.000+02:00", "total": 0.2331, "level": "NORMAL"}, {"startsAt": "2024-10-09T02:00:00.000+02:00", "total": 0.2301, "level": "NORMAL"}, {"startsAt": "2024-10-09T03:00:00.000+02:00", "total": 0.2264, "level": "CHEAP"}, {"startsAt": "2024-10-09T04:00:00.000+02:00", "total": 0.2299, "level": "NORMAL"}, {"startsAt": "2024-10-09T05:00:00.000+02:00", "total": 0.2377, "level": "NORMAL"}, {"startsAt": "2024-10-09T06:00:00.000+02:00", "total": 0.2649, "level": "NORMAL"}, {"startsAt": "2024-10-09T07:00:00.000+02:00", "total": 0.294, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T08:00:00.000+02:00", "total": 0.2938, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T09:00:00.000+02:00", "total": 0.2653, "level": "NORMAL"}, {"startsAt": "2024-10-09T10:00:00.000+02:00", "total": 0.2475, "level": "NORMAL"}, {"startsAt": "2024-10-09T11:00:00.000+02:00", "total": 0.233, "level": "NORMAL"}, {"startsAt": "2024-10-09T12:00:00.000+02:00", "total": 0.2329, "level": "NORMAL"}, {"startsAt": "2024-10-09T13:00:00.000+02:00", "total": 0.233, "level": "NORMAL"}, {"startsAt": "2024-10-09T14:00:00.000+02:00", "total": 0.2422, "level": "NORMAL"}, {"startsAt": "2024-10-09T15:00:00.000+02:00", "total": 0.2536, "level": "NORMAL"}, {"startsAt": "2024-10-09T16:00:00.000+02:00", "total": 0.2748, "level": "NORMAL"}, {"startsAt": "2024-10-09T17:00:00.000+02:00", "total": 0.3015, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T18:00:00.000+02:00", "total": 0.3075, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T19:00:00.000+02:00", "total": 0.313, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T20:00:00.000+02:00", "total": 0.2939, "level": "NORMAL"}, {"startsAt": "2024-10-09T21:00:00.000+02:00", "total": 0.2757, "level": "NORMAL"}, {"startsAt": "2024-10-09T22:00:00.000+02:00", "total": 0.2749, "level": "NORMAL"}, {"startsAt": "2024-10-09T23:00:00.000+02:00", "total": 0.2597, "level": "NORMAL"}]'
        self.tst.debug_input_value[self.tst.PIN_I_CHEAP] = 0.05
        self.tst.debug_input_value[self.tst.PIN_I_EXPENSIVE] = 0.99
        self.tst.debug_now = datetime(year=2024, month=10, day=1, hour=00)

        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TODAY] = today
        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TOMORROW] = tomorrow

        self.tst.interval_update_time_control = 2
        self.tst.on_input_value(self.tst.PIN_I_CHEAP, 0.01)

        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_START])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_STOP])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_START])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_STOP])

        self.assertEqual("17:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_START])
        self.assertEqual("21:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_STOP])
        self.assertEqual("07:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_START])
        self.assertEqual("09:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_STOP])

        self.tst.debug_input_value[self.tst.PIN_I_CHEAP] = 0.30
        time.sleep(4)

        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_START])
        self.assertEqual("17:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_STOP])
        self.assertEqual("20:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_START])
        self.assertEqual("17:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_STOP])

        self.assertEqual("17:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_START])
        self.assertEqual("20:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_STOP])
        self.assertEqual("17:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_START])
        self.assertEqual("20:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_STOP])

    def print_results(self, prefix=str()):
        print("\n###### {}".format(prefix))
        print("Cheap:\t\t{}-{}\t\t{}-{}\nExpensive:\t{}-{}\t\t{}-{}".format(self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_START],
                                                                      self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_STOP],
                                                                      self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_START],
                                                                      self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_STOP],
                                                                      self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_START],
                                                                      self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_STOP],
                                                                      self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_START],
                                                                      self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_STOP]))
        print("######\n")

    def test_5(self):
        print("\n\n### test_5")
        today = '[{"startsAt": "2024-10-09T00:00:00.000+02:00", "total": 0.2354, "level": "NORMAL"}, {"startsAt": "2024-10-09T01:00:00.000+02:00", "total": 0.2331, "level": "NORMAL"}, {"startsAt": "2024-10-09T02:00:00.000+02:00", "total": 0.2301, "level": "NORMAL"}, {"startsAt": "2024-10-09T03:00:00.000+02:00", "total": 0.2264, "level": "CHEAP"}, {"startsAt": "2024-10-09T04:00:00.000+02:00", "total": 0.2299, "level": "CHEAP"}, {"startsAt": "2024-10-09T05:00:00.000+02:00", "total": 0.2377, "level": "NORMAL"}, {"startsAt": "2024-10-09T06:00:00.000+02:00", "total": 0.2649, "level": "NORMAL"}, {"startsAt": "2024-10-09T07:00:00.000+02:00", "total": 0.294, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T08:00:00.000+02:00", "total": 0.2938, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T09:00:00.000+02:00", "total": 0.2653, "level": "NORMAL"}, {"startsAt": "2024-10-09T10:00:00.000+02:00", "total": 0.2475, "level": "NORMAL"}, {"startsAt": "2024-10-09T11:00:00.000+02:00", "total": 0.233, "level": "NORMAL"}, {"startsAt": "2024-10-09T12:00:00.000+02:00", "total": 0.2329, "level": "NORMAL"}, {"startsAt": "2024-10-09T13:00:00.000+02:00", "total": 0.233, "level": "NORMAL"}, {"startsAt": "2024-10-09T14:00:00.000+02:00", "total": 0.2422, "level": "NORMAL"}, {"startsAt": "2024-10-09T15:00:00.000+02:00", "total": 0.2536, "level": "NORMAL"}, {"startsAt": "2024-10-09T16:00:00.000+02:00", "total": 0.2748, "level": "NORMAL"}, {"startsAt": "2024-10-09T17:00:00.000+02:00", "total": 0.3015, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T18:00:00.000+02:00", "total": 0.3075, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T19:00:00.000+02:00", "total": 0.313, "level": "EXPENSIVE"}, {"startsAt": "2024-10-09T20:00:00.000+02:00", "total": 0.2939, "level": "NORMAL"}, {"startsAt": "2024-10-09T21:00:00.000+02:00", "total": 0.2757, "level": "NORMAL"}, {"startsAt": "2024-10-09T22:00:00.000+02:00", "total": 0.2749, "level": "NORMAL"}, {"startsAt": "2024-10-09T23:00:00.000+02:00", "total": 0.2597, "level": "NORMAL"}]'
        tomorrow = '[]'
        self.tst.debug_input_value[self.tst.PIN_I_CHEAP] = 0.05
        self.tst.debug_input_value[self.tst.PIN_I_EXPENSIVE] = 0.99
        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TODAY] = today
        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TOMORROW] = tomorrow

        self.tst.debug_now = datetime(year=2024, month=10, day=9, hour=19, minute=01)
        self.tst.interval_update_time_control = 2

        print("\n############ W/O tomorrow")
        self.tst.on_input_value(self.tst.PIN_I_CHEAP, 0.01)
        time.sleep(2)
        self.print_results(self.tst.debug_now)

        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_START])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_STOP])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_START])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_STOP])

        self.assertEqual("17:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_START])
        self.assertEqual("20:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_STOP])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_START])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_STOP])


        print("\n############ With tomorrow")
        self.tst.debug_now = datetime(year=2024, month=10, day=9, hour=19, minute=01)
        tomorrow = '[{"startsAt": "2024-10-10T00:00:00.000+02:00", "total": 0.2345, "level": "CHEAP"}, {"startsAt": "2024-10-10T01:00:00.000+02:00", "total": 0.2175, "level": "CHEAP"}, {"startsAt": "2024-10-10T02:00:00.000+02:00", "total": 0.2067, "level": "CHEAP"}, {"startsAt": "2024-10-10T03:00:00.000+02:00", "total": 0.1998, "level": "CHEAP"}, {"startsAt": "2024-10-10T04:00:00.000+02:00", "total": 0.197, "level": "CHEAP"}, {"startsAt": "2024-10-10T05:00:00.000+02:00", "total": 0.2089, "level": "CHEAP"}, {"startsAt": "2024-10-10T06:00:00.000+02:00", "total": 0.2356, "level": "CHEAP"}, {"startsAt": "2024-10-10T07:00:00.000+02:00", "total": 0.2628, "level": "NORMAL"}, {"startsAt": "2024-10-10T08:00:00.000+02:00", "total": 0.2575, "level": "NORMAL"}, {"startsAt": "2024-10-10T09:00:00.000+02:00", "total": 0.2421, "level": "NORMAL"}, {"startsAt": "2024-10-10T10:00:00.000+02:00", "total": 0.2236, "level": "CHEAP"}, {"startsAt": "2024-10-10T11:00:00.000+02:00", "total": 0.2081, "level": "CHEAP"}, {"startsAt": "2024-10-10T12:00:00.000+02:00", "total": 0.1878, "level": "CHEAP"}, {"startsAt": "2024-10-10T13:00:00.000+02:00", "total": 0.1807, "level": "CHEAP"}, {"startsAt": "2024-10-10T14:00:00.000+02:00", "total": 0.1855, "level": "CHEAP"}, {"startsAt": "2024-10-10T15:00:00.000+02:00", "total": 0.2074, "level": "CHEAP"}, {"startsAt": "2024-10-10T16:00:00.000+02:00", "total": 0.2313, "level": "CHEAP"}, {"startsAt": "2024-10-10T17:00:00.000+02:00", "total": 0.2639, "level": "NORMAL"}, {"startsAt": "2024-10-10T18:00:00.000+02:00", "total": 0.2761, "level": "NORMAL"}, {"startsAt": "2024-10-10T19:00:00.000+02:00", "total": 0.3037, "level": "EXPENSIVE"}, {"startsAt": "2024-10-10T20:00:00.000+02:00", "total": 0.2821, "level": "NORMAL"}, {"startsAt": "2024-10-10T21:00:00.000+02:00", "total": 0.2693, "level": "NORMAL"}, {"startsAt": "2024-10-10T22:00:00.000+02:00", "total": 0.2607, "level": "NORMAL"}, {"startsAt": "2024-10-10T23:00:00.000+02:00", "total": 0.2449, "level": "NORMAL"}]'
        self.tst.debug_input_value[self.tst.PIN_I_PRICES_TOMORROW] = tomorrow
        time.sleep(4)
        self.print_results(self.tst.debug_now)

        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_START])
        self.assertEqual("07:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_STOP])
        self.assertEqual("10:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_START])
        self.assertEqual("17:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_STOP])

        self.assertEqual("17:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_START])
        self.assertEqual("20:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_STOP])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_START])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_STOP])


        print("\n############ Later")
        self.tst.debug_now = datetime(year=2024, month=10, day=9, hour=23, minute=01)
        time.sleep(4)
        self.print_results(self.tst.debug_now)

        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_START])
        self.assertEqual("07:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP1_STOP])
        self.assertEqual("10:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_START])
        self.assertEqual("17:00", self.tst.debug_output_value[self.tst.PIN_O_CHEAP2_STOP])

        self.assertEqual("19:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_START])
        self.assertEqual("20:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE1_STOP])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_START])
        self.assertEqual("00:00", self.tst.debug_output_value[self.tst.PIN_O_EXPENSIVE2_STOP])

    def tearDown(self):
        print("\n### tearDown")
        self.tst.interval_update_time_control = 0
        self.tst.interval_update = 0
        print("DEBUG | tearDown | Finished.")


if __name__ == '__main__':
    unittest.main()
