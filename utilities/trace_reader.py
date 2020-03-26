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


class TraceReader:
    """
    The trace reader is a (memory-) lightweight iterator that yields tuples of the form (address: int, taken: bool)
    from the given trace file.
    """
    def __init__(self, filename):
        """
        Class initialization.
        :param filename: trace file location
        """
        self.filename = filename

    def read(self):
        """
        Trace file read iterator.
        :return: tuple (address: int, taken: bool)
        """
        # open file
        with open(self.filename, "r") as file:
            # read line-by-line
            for line in file:
                # split address and taken
                address, taken = line.split()
                # remove lowest 2 bits (offset) from address and return tuple
                yield int(address) // 4, int(taken)
