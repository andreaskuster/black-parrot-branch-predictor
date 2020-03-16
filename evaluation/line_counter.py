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

import os

if __name__ == "__main__":
    """
    Counts the number of traces in all trace files.
    """
    _BASE_PATH = "traces"

    traces = [f for f in os.listdir(_BASE_PATH) if os.path.isfile(os.path.join(_BASE_PATH, f)) and f.endswith(".trace")]

    for trace in traces:
        counter = 0
        with open(os.path.join("traces", trace)) as file:
            for line in file:
                counter += 1
        print("{}: {}".format(trace, counter))
