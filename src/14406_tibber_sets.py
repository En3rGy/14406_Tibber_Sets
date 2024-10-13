# coding: UTF-8
import json
from datetime import datetime, timedelta
import threading
from logging import exception


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class Tibber_sets14406(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "tibber_sets_14406")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_PRICES_TODAY=1
        self.PIN_I_PRICES_TOMORROW=2
        self.PIN_I_CHEAP=3
        self.PIN_I_EXPENSIVE=4
        self.PIN_I_NORMAL_INTERVALL=5
        self.PIN_O_CHEAP1_START=1
        self.PIN_O_CHEAP1_STOP=2
        self.PIN_O_CHEAP2_START=3
        self.PIN_O_CHEAP2_STOP=4
        self.PIN_O_EXPENSIVE1_START=5
        self.PIN_O_EXPENSIVE1_STOP=6
        self.PIN_O_EXPENSIVE2_START=7
        self.PIN_O_EXPENSIVE2_STOP=8
        self.PIN_O_IS_CHEAP=9
        self.PIN_O_IS_EXPENSIVE=10

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

        self.out_sbc = {}
        self.price_list = PriceList()
        self.debug = False
        self.interval_update = 60
        self.interval_update_time_control = 3600
        self.time_control_timer = threading.Timer(self.interval_update_time_control, self.update_time_control)
        self.debug_now = datetime(month=10, day=1, year=2024)

    def set_output_value_sbc(self, pin, val):
        # type:  (int, any) -> None
        if pin in self.out_sbc:
            if self.out_sbc[pin] == val:
                self.LOGGER.debug("SBC: Pin {} <- data not send ({})".format(pin, str(val).decode("utf-8")))
                return

        self._set_output_value(pin, val)
        self.LOGGER.debug("OUT: Pin {} <-\t{}".format(pin, val))
        self.out_sbc[pin] = val

    def log_msg(self, text):
        self.DEBUG.add_message("14406 ({}): {}".format(self._get_module_id(), text))

    def log_data(self, key, value):
        self.DEBUG.set_value("14406 ({}) {}".format(self._get_module_id(), key), str(value))

    def _input_convert(self, data_in):
        if isinstance(data_in, list):
            return data_in
        elif isinstance(data_in, basestring):
            data_in = data_in.replace("'", '"').replace('u"', '"')
            return json.loads(data_in)
        return []

    def pre_process_prices(self):
        # 1. Collect price info
        # 2. Combine, if possible
        # 3. Override level info is required
        #
        # type: json
        # return: updated json object of price infos
        try:
            if self.debug: print("DEBUG | Entering pre_process_prices()...")

            cheap_price = float(self._get_input_value(self.PIN_I_CHEAP))
            expensive_price = float(self._get_input_value(self.PIN_I_EXPENSIVE))
            today = self._get_input_value(self.PIN_I_PRICES_TODAY)
            tomorrow = self._get_input_value(self.PIN_I_PRICES_TOMORROW)
            normal_index = self._get_input_value(self.PIN_I_NORMAL_INTERVALL)

            data = self._input_convert(today)
            prices_tomorrow = self._input_convert(tomorrow)
            data.extend(prices_tomorrow)
        except Exception as e:
            raise Exception("pre_process_prices | Error loading Tibber jsons: {}".format(e))

        try:
            for i in range(len(data)):
                if data[i]["total"] < cheap_price or (normal_index == -1 and data[i]["level"] == "NORMAL"):
                    data[i]["level"] = "CHEAP"
                elif data[i]["total"] > expensive_price or (normal_index == 1 and data[i]["level"] == "NORMAL"):
                    data[i]["level"] = "EXPENSIVE"
        except Exception as e:
            raise Exception("pre_process_prices | Error working with tibber jsons: {}".format(e))

        self.log_data("Today", json.dumps(today))
        self.log_data("Tomorrow", json.dumps(tomorrow))
        return data

    def update_time_control(self):
        if self.interval_update_time_control == 0:
            print("DEBUG | update_time_control | Timer interval = 0; Aborting.\n")
            return

        self.log_msg("Evaluating Time Sets.")

        try:
            data = self.pre_process_prices()

            # build price list
            self.price_list = PriceList(data)

            # create intervals
            if self.debug:
                self.price_list.create_intervals(self.debug_now)
            else:
                self.price_list.create_intervals()

            self.log_data("Identified Intervals", self.price_list.print_intervals())

            interval_defaults = {"startsAt": "00:00", "stopsAt": "00:00"}

            # Set cheap interval values
            cheap_intervals = self.price_list.get_intervals(-1)
            cheap1 = cheap_intervals[0] if len(cheap_intervals) > 0 else interval_defaults
            self.set_output_value_sbc(self.PIN_O_CHEAP1_START, cheap1["startsAt"])
            self.set_output_value_sbc(self.PIN_O_CHEAP1_STOP, cheap1["stopsAt"])

            cheap2 = cheap_intervals[1] if len(cheap_intervals) > 1 else interval_defaults
            self.set_output_value_sbc(self.PIN_O_CHEAP2_START, cheap2["startsAt"])
            self.set_output_value_sbc(self.PIN_O_CHEAP2_STOP, cheap2["stopsAt"])

            # Set expensive interval values
            expensive_intervals = self.price_list.get_intervals(1)
            exp1 = expensive_intervals[0] if len(expensive_intervals) > 0 else interval_defaults
            self.set_output_value_sbc(self.PIN_O_EXPENSIVE1_START, exp1["startsAt"])
            self.set_output_value_sbc(self.PIN_O_EXPENSIVE1_STOP, exp1["stopsAt"])

            exp2 = expensive_intervals[1] if len(expensive_intervals) > 1 else interval_defaults
            self.set_output_value_sbc(self.PIN_O_EXPENSIVE2_START, exp2["startsAt"])
            self.set_output_value_sbc(self.PIN_O_EXPENSIVE2_STOP, exp2["stopsAt"])

        except Exception as e:
            self.log_msg("update_time_control | Exception {}".format(e))

        self.time_control_timer = threading.Timer(self.interval_update_time_control, self.update_time_control)
        self.time_control_timer.start()

    def update(self):
        # calc status
        if self.interval_update == 0:
            print("DEBUG | update | Timer interval= 0; Aborting.")
            return

        now = datetime.now()
        for price in self.price_list.prices:
            if price.start < now < price.stop:
                level = price.get_level()
                self.set_output_value_sbc(self.PIN_O_IS_CHEAP, level == -1)
                self.set_output_value_sbc(self.PIN_O_IS_EXPENSIVE, level == 1)

        # try to run each full minute
        delay = self.interval_update - datetime.now().second
        threading.Timer(delay, self.update).start()

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        now = datetime.now()
        delay = self.interval_update - now.second
        self.update_time_control()
        self.update()

    def on_input_value(self, index, value):
        if self.time_control_timer.isAlive():
            self.time_control_timer.cancel()

        self.update_time_control()


class PriceList:
    def __init__(self, data=None):
        if data is None:
            data = []
        self.prices = [] # type: List[PriceInfo]
        self.cheap = []
        self.expensive = []
        self.normal = []
        self.intervals = []

        for price in data:
            price_info = PriceInfo(price)
            self.add(price_info)

    def __str__(self):
        result = []
        for price in self.prices:
            result.append(json.loads(str(price)))
        return json.dumps(result)

    def add(self, price):
        self.prices.append(price)
        self.prices = self._bubble_sort(self.prices)

    def print_intervals(self):
        res = []
        for interval in self.intervals:
            res.append({"startsAt": interval["startsAt"], "stopsAt": interval["stopsAt"], "level": interval["level"]})
        return json.dumps(res)

    def get_intervals(self, level):
        if level == -1:
            return self.cheap
        elif level == 0:
            return self.normal
        elif level == 1:
            return self.expensive

    def _get_time(self, time_s):
        try:
            hh = int(time_s.split(":")[0])
            mm = int(time_s.split(":")[1])
            return hh, mm
        except Exception as e:
            raise Exception("_get_time | {}".format(e))

    def create_intervals(self, now_dt=datetime.now()):
        self.intervals = []
        if not self.prices:
            return

        try:
            print("DEBUG | create_intervals | Checking {} time slots".format(len(self.prices)))

            start = self.prices[0].get_start_s()
            start_dt = self.prices[0].start
            stop_dt = self.prices[0].stop
            stop = self.prices[0].get_stop_s()
            level = self.prices[0].get_level()

            for price in self.prices[1:]:
                if price.get_level() == level:
                    stop_dt = price.stop
                    stop = price.get_stop_s()
                else:
                    # Close current interval and start a new one
                    self._add_interval(start, start_dt, stop, stop_dt, level)
                    start = price.get_start_s()
                    start_dt = price.start
                    stop = price.get_stop_s()
                    stop_dt = price.stop
                    level = price.get_level()

            # Final interval
            self._add_interval(start, start_dt, stop, stop_dt, level)

            self.cheap = []
            self.expensive = []
            self.normal = []

            for interval in self.intervals:
                if interval["stopsAt_dt"] < now_dt:
                    print("DEBUG | create_intervals | Interval outdated because {} < now_dt={}".format(interval["stopsAt_dt"], now_dt))
                    continue

                skip = False
                for former_interval in self.cheap + self.normal + self.expensive:
                    curr_start_h = interval["stopsAt_dt"].hour
                    curr_stop_h = interval["startsAt_dt"].hour
                    former_start_h = former_interval["startsAt_dt"].hour
                    former_stop_h = former_interval["stopsAt_dt"].hour
                    if former_start_h < curr_start_h < former_stop_h or former_start_h < curr_stop_h < former_stop_h:
                        print("DEBUG | create_intervals | Interval overlaps previous interval. Skipping it.")
                        skip = True
                        break

                if skip: continue

                if interval["level"] == -1:
                    self.cheap.append(interval)
                elif interval["level"] == 0:
                    self.normal.append(interval)
                elif interval["level"] == 1:
                    self.expensive.append(interval)

        except Exception as e:
            raise Exception("create_intervals | {}".format(e))

        print("DEBUG | create_interval | Active cheap intervals:     {}".format(self.cheap))
        print("DEBUG | create_interval | Active expensive intervals: {}".format(self.expensive))
        print("DEBUG | create_interval | Active normal intervals:    {}".format(self.normal))

    def _add_interval(self, start, start_dt, stop, stop_dt, level):
        """Helper method to add an interval and print debug information."""
        self.intervals.append({
            "startsAt": start,
            "startsAt_dt": start_dt,
            "stopsAt": stop,
            "stopsAt_dt": stop_dt,
            "level": level
        })
        print("DEBUG | create_intervals | Adding: {}".format(self.print_interval(-1)))

    def print_interval(self, index):
        interval = self.intervals[index]
        return "{} - {} // {}".format(interval["startsAt_dt"], interval["stopsAt_dt"], interval["level"])

    def _bubble_sort(self, arr):
        n = len(arr)
        for i in range(n):
            swapped = False
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    swapped = True
            if not swapped:
                break

        return arr


class PriceInfo:
    def __init__(self, data, duration_min=60):
        if "+" in data["startsAt"]:
            data["startsAt"] = data["startsAt"].split(".")[0] # ignoring msec & timezone information

        self.start = datetime.strptime(data["startsAt"], "%Y-%m-%dT%H:%M:%S")
        self.stop = self.start + timedelta(minutes=duration_min)
        self.price = data["total"]
        self.level = data["level"]

    def __gt__(self, other):
        return self.start > other.start

    def __lt__(self, other):
        return self.start < other.start

    def __str__(self):
        return json.dumps({"total": self.price, "level": self.level, "startsAt": self.get_start_s, "stopsAt": self.get_stop_s})

    def get_start_s(self):
        return self._get_time_s(self.start)

    def get_stop_s(self):
        return self._get_time_s(self.stop)

    def get_level(self):
        if self.level in ["EXPENSIVE", "VERY_EXPENSIVE"]:
            return 1
        elif self.level in ["CHEAP", "VERY CHEAP"]:
            return -1
        else:
            return 0

    def _get_time_s(self, date_time):
        if not date_time:
            return "00:00"

        #dt = datetime.strptime(date_time[:19], "%Y-%m-%dT%H:%M:%S")
        time_output = date_time.strftime("%H:%M")
        return time_output
