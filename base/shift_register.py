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


class ShiftRegister:

    def __init__(self, size, init_val=0):
        """
        Initialize internal state.
        :param size: length of the shift register
        :param init_val: initial value of all elements in the register
        """
        self.size = size
        self.register = [init_val]*size

    def shift(self, new_item):
        """
        Shift new item.
        :param new_item: new value
        :return: None
        """
        # convert new item to integer
        new_item = int(new_item)
        # check value
        if new_item not in [0, 1]:
            print("Warning: not a binary number.")
        # shift value into register, drop oldest value
        self.register = [new_item] + self.register[0:self.size-1]

    def reg_to_number(self):
        """
        Converts the shift register bits to its integer value.
        :return: current integer value of shift register
        """
        # init var
        number = 0
        # compute integer value sum(2^i*bit[i]) for i=0..(N-1)
        for i in range(self.size):
            number += (2 ** i)*self.register[i]
        return number
