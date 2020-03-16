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
        self.register = [init_val] * size

    def shift(self, new_item):
        new_item = int(new_item)
        if new_item not in [0, 1]:
            print("Warning: not a binary number.")
        self.register = [new_item] + self.register[0:self.size - 1]

    def reg_to_number(self):
        number = 0
        for i in range(self.size):
            number += (2 ** i) * self.register[i]
        return number


class SaturationCounter:

    def __init__(self, n_bits=0, init_val=0):
        self.counter = init_val
        self.max_val = 2 ** n_bits - 1

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
                yield int(address) // 4, int(taken)  # remove lowest 2 bits from address, since they are always 0


class BranchPredictorTournament:

    def __init__(self, sat_cnt_bits, bht_addr_bits, n_hist):
        # store general parameters
        self.sat_cnt_bits = sat_cnt_bits
        self.bht_addr_bits = bht_addr_bits
        # set helper variable for highest not-taken values
        self.saturation_size_half = (2 ** (sat_cnt_bits - 1)) - 1
        #
        # LOCAL BRANCH PREDICTOR
        # store params
        self.bht_local_size = 2 ** bht_addr_bits
        # local branch history table
        self.bht_local = [SaturationCounter(n_bits=sat_cnt_bits, init_val=self.saturation_size_half) for x in
                          range(self.bht_local_size)]
        #
        # GLOBAL BRANCH PREDICTOR
        # store params
        self.bht_global_size = 2 ** n_hist
        # branch history shift register
        self.bh = ShiftRegister(size=n_hist)
        # global branch history table
        self.bht_global = [SaturationCounter(n_bits=sat_cnt_bits, init_val=self.saturation_size_half) for x in
                           range(self.bht_global_size)]
        #
        # SELECTOR
        # selector saturation counter
        self.bht_sel = SaturationCounter(n_bits=sat_cnt_bits, init_val=self.saturation_size_half)

    def update(self, address, correct):
        # get the selector decision
        select_prediction = self.predict_selector()
        # get the local prediction
        local_prediction = self.predict_local(address)
        # get the global prediction
        global_prediction = self.predict_global()
        # compute the actual outcome
        if select_prediction:  # (True: global, False: local)
            taken_actual = (correct and global_prediction) or (not correct and not global_prediction)
        else:
            taken_actual = (correct and local_prediction) or (not correct and not local_prediction)
        # update counters
        if taken_actual:
            # local
            self.bht_local[address % self.bht_local_size].count_up()
            # global
            self.bht_global[self.bh.reg_to_number()].count_up()
        else:
            # local
            self.bht_local[address % self.bht_local_size].count_down()
            # global
            self.bht_global[self.bh.reg_to_number()].count_down()
        # update selector
        local_correct = (local_prediction == taken_actual)
        global_correct = (global_prediction == taken_actual)
        if local_correct and not global_correct:
            self.bht_sel.count_down()
        elif not local_correct and global_correct:
            self.bht_sel.count_up()
        # update branch history shift register
        self.bh.shift(taken_actual)

    def predict(self, address):
        # check which branch predictor we trust (selector)
        if self.predict_selector():
            return self.predict_global()
        else:
            return self.predict_local(address)

    def predict_local(self, address):
        # local branch predictor
        return self.bht_local[address % self.bht_local_size].value() > self.saturation_size_half

    def predict_global(self):
        # global branch predictor
        return self.bht_global[self.bh.reg_to_number()].value() > self.saturation_size_half

    def predict_selector(self):
        # selector
        return self.bht_sel.value() > self.saturation_size_half


def evaluate(sat_bits, addr_bits, n_hist, trace):
    n_correct = 0
    n_total = 0

    import os.path
    tr = TraceReader(os.path.join("../evaluation/traces", trace + ".trace"))
    bp = BranchPredictorTournament(sat_cnt_bits=sat_bits, bht_addr_bits=addr_bits, n_hist=n_hist)

    for address, taken in tr.read():
        prediction = bp.predict(address)
        correct = prediction == taken
        bp.update(address, correct)
        if correct:
            n_correct += 1
        n_total += 1
    result = "{}, {}, {}, {}".format(trace, sat_bits, addr_bits, n_correct / n_total)
    print(result)
    return result


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true')
    parser.add_argument("--gridsearch", action='store_true')
    args = parser.parse_args()

    if args.debug:

        # params
        _SAT_CNT_BITS = 2
        _BHT_ADDR_BITS = 2
        _N_HIST = 2

        tr = TraceReader("../evaluation/traces/dummy.trace")
        bp = BranchPredictorTournament(sat_cnt_bits=_SAT_CNT_BITS, bht_addr_bits=_BHT_ADDR_BITS, n_hist=_N_HIST)

        for address, taken in tr.read():
            # remove upper bits
            address = address % (2 ** _BHT_ADDR_BITS)
            # predict branch
            prediction = bp.predict(address)
            # determine if prediction was correct
            correct = prediction == taken
            # update internal state
            bp.update(address, correct)

    if args.gridsearch:

        from multiprocessing import Pool

        tasks = list()
        with Pool(processes=7) as pool:
            for sat_bits in [1, 2, 3, 4, 5]:
                for addr_bits in [3, 6, 9, 12, 15]:
                    for trace in ["short_mobile_1", "long_mobile_1", "short_server_1", "long_server_1"]:
                        tasks.append(pool.apply_async(evaluate, (sat_bits, addr_bits, addr_bits, trace)))
            results = list()
            for task in tasks:
                results.append(task.get())
            with open("gridsearch_tournament.txt", "w") as file:
                for result in results:
                    file.write(result + "\n")
        print("done")
