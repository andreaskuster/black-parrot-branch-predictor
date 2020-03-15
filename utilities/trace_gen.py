#!/usr/bin/env python3
# encoding: utf-8

import numpy as np
from random import randint
from enum import Enum


class TraceCmd(Enum):
    SEND = "0001"
    RECV = "0010"
    WAIT = "0000"
    FINISH = "0100"


if __name__ == "__main__":
    _TRACE_FILE = "trace.tr"
    _WAIT_CMD = "0000"
    _FINISH_CMD = "0100"
    _SEND_CMD = "0001"
    _RECV_CMD = "0010"
    _PADDING = "{0:032b}".format(0)
    with open(_TRACE_FILE, "w") as file:
        # wait K=3 cycles
        K = 3
        for i in range(K):
            file.write("{}__{}__{}{}".format(_WAIT_CMD, _PADDING, _PADDING, "\n"))

        # generate L=2^12 examples
        L = 2**3
        L = min(L, 2 ** 31 - K - 1)
        for i in range(L):
            a, b = randint(0, (2 ** 32) - 1), randint(0, (2 ** 32) - 1)
            file.write("{}__{}__{}{}".format(_SEND_CMD, "{0:032b}".format(a), "{0:032b}".format(b), "\n"))
            file.write("{}__{}__{}{}".format(_RECV_CMD, "{0:032b}".format(0), "{0:032b}".format(np.gcd(a, b)), "\n"))

        # finish sim
        file.write("{}__{}__{}{}".format(_FINISH_CMD, _PADDING, _PADDING, "\n"))
