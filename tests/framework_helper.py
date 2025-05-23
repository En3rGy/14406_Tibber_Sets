# coding: utf8
import logging
import time
import random
import socket
import logging

class hsl20_4:
    LOGGING_NONE = 0

    def __init__(self):
        self.module_id = random.randint(1, 1000)
        pass

    class BaseModule:
        debug_output_value = {}  # type: {int, any}
        debug_set_remanent = {}  # type: {int, any}
        debug_input_value = {}  # type: {int: any}

        def __init__(self, a, b):
            self.module_id = 0
            logging.basicConfig()
            self.logger = logging.getLogger()

        def _get_framework(self):
            f = hsl20_4.Framework()
            return f

        def _get_logger(self, a, b):
            return self.logger

        def _get_remanent(self, key):
            # type: (str) -> any
            return 0

        def _set_remanent(self, key, val):
            # type: (str, any) -> None
            self.debug_set_remanent[key] = val
            logging.info("# Module #{} REMANENT: Pin {} -> \t{}".format(self._get_module_id(), key, val))

        def _set_output_value(self, pin, value):
            # type: (int, any) -> None
            self.debug_output_value[pin] = value

            name = ""
            for names, values in locals().items():
                if value == pin:
                    name = names
                    break

            logging.info("# Module #{} OUT: Pin {} ({}) -> \t{}".format(self._get_module_id(), pin, name, value))

        def _set_input_value(self, pin, value):
            # type: (int, any) -> None
            self.debug_input_value[int(pin)] = value
            logging.info("# Module #{} IN: Pin {} -> \t{}".format(self._get_module_id(), pin, value))

        def _get_input_value(self, pin):
            # type: (int) -> any
            if pin in self.debug_input_value:
                return self.debug_input_value[pin]
            else:
                return 0

        def _get_module_id(self):
            """

            :return: module id
            :rtype: int
            """
            if self.module_id == 0:
                self.module_id = random.randint(1, 1000)
            return self.module_id

    class Framework:
        def __init__(self):
            hostname = socket.gethostname()
            self.my_ip = socket.gethostbyname(hostname)

        def _run_in_context_thread(self, a):
            pass

        def create_debug_section(self):
            d = hsl20_4.DebugHelper()
            return d

        def get_homeserver_private_ip(self):
            # type: () -> str
            return self.my_ip

        def get_instance_by_id(self, id):
            # type: (int) -> HueGroup_14100_14100
            return HueGroup_14100_14100(0)

        def resolve_dns(self, a):
            return socket.gethostbyname(a)

    class DebugHelper:
        def __init__(self):
            pass

        def set_value(self, cap, text):
            curr_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.info("# SET VAL # {caption} -> {data}".format(time=curr_time, caption=cap, data=text))

        def add_message(self, msg):
            curr_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            logging.info("# ADD MSG # {msg}".format(time=curr_time, msg=msg))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("framework_helper")