#!/usr/bin/env python3
# encoding: utf-8

"""
    Copyright (C) 2020  Andreas Kuster

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Andreas Kuster"
__copyright__ = "Copyright 2020"
__license__ = "GPL"

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
