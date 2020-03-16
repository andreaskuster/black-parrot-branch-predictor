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

import argparse

class ShiftRegister:

    def __init__(self, size, init_val=0):
        self.size = size
        self.register = [init_val]*size

    def shift(self, new_item):
        new_item = int(new_item)
        if new_item not in [0, 1]:
            print("Warning: not a binary number.")
        self.register = [new_item] + self.register[0:self.size-1]

    def reg_to_number(self):
        number = 0
        for i in range(self.size):
            number += (2 ** i)*self.register[i]
        return number


class SaturationCounter:

    def __init__(self, n_bits=0, init_val=0):
        self.counter = init_val
        self.max_val = 2**n_bits - 1

    def count_up(self):
        if self.counter < self.max_val:
            self.counter += 1

    def count_down(self):
        if self.counter > 0:
            self.counter -= 1

    def value(self):
        return self.counter


class TraceReader:

    def __init__(self, filename):
        self.filename = filename

    def read(self):
        with open(self.filename, "r") as file:
            for line in file:
                address, taken = line.split()
                yield int(address)//4, int(taken)  # remove lowest 2 bits from address, since they are always 0


class BranchPredictorGselect:

    def __init__(self, sat_cnt_bits, bht_addr_bits, n_hist):
        # store parameters
        self.sat_cnt_bits = sat_cnt_bits
        self.bht_size = 2 ** bht_addr_bits
        self.n_hist = n_hist
        # set helper variable for highest not-taken values
        self.saturation_size_half = (2 ** (sat_cnt_bits-1))-1
        # init branch history table
        self.bht = [SaturationCounter(n_bits=sat_cnt_bits, init_val=self.saturation_size_half) for x in range(self.bht_size)]
        # init global history shift reg
        self.gh = ShiftRegister(size=6, init_val=0)

    def update(self, address, correct):
        # extract relevant index bits
        index = ((address * (2**self.n_hist)) + self.gh.reg_to_number()) % self.bht_size
        # update counter
        taken_prediction = self.predict(address)
        taken_actual = (correct and taken_prediction) or (not correct and not taken_prediction)
        if taken_actual:
            self.bht[index].count_up()
        else:
            self.bht[index].count_down()
        self.gh.shift(taken_actual)

    def predict(self, address):
        # extract relevant index bits
        index = ((address * (2**self.n_hist)) + self.gh.reg_to_number()) % self.bht_size
        return self.bht[index].value() > self.saturation_size_half


def evaluate(sat_bits, addr_bits, n_hist, trace):

    n_correct = 0
    n_total = 0

    import os.path
    tr = TraceReader(os.path.join("traces", trace + ".trace"))
    bp = BranchPredictorGselect(sat_cnt_bits=sat_bits, bht_addr_bits=addr_bits, n_hist=n_hist)

    for address, taken in tr.read():
        prediction = bp.predict(address)
        correct = prediction == taken
        bp.update(address, correct)
        if correct:
            n_correct += 1
        n_total += 1
    print("{}, {}, {}, {}, {}".format(trace, sat_bits, addr_bits, n_hist, n_correct / n_total))
    return n_correct / n_total


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true')
    parser.add_argument("--gridsearch", action='store_true')
    args = parser.parse_args()

    if args.debug:

        # params
        _SAT_CNT_BITS = 2
        _BHT_ADDR_BITS = 6
        _N_HIST = 6

        tr = TraceReader("../evaluation/traces/dummy.trace")
        bp = BranchPredictorGselect(sat_cnt_bits=_SAT_CNT_BITS, bht_addr_bits=_BHT_ADDR_BITS, n_hist=_N_HIST)

        for address, taken in tr.read():
            # remove upper bits
            address = address % (2**_BHT_ADDR_BITS)
            # predict branch
            prediction = bp.predict(address)
            # determine if prediction was correct
            correct = prediction == taken
            # update internal state
            bp.update(address, correct)

    if args.gridsearch:

        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=16) as executor:
            for sat_bits in [1, 2, 3, 4, 5]:
                for addr_bits in [3, 6, 9, 12, 15]:
                    for n_hist in [3, 6]:
                        for trace in ["short_mobile_1", "long_mobile_1", "short_server_1", "long_server_1"]:
                            executor.submit(evaluate, sat_bits, addr_bits, n_hist, trace)
