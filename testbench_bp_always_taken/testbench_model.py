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

class TraceReader:

    def __init__(self, filename):
        self.filename = filename

    def read(self):
        with open(self.filename, "r") as file:
            for line in file:
                address, taken = line.split()
                yield int(address)//4, int(taken)  # remove lowest 2 bits from address, since they are always 0


class BranchPredictorAlwaysTaken:

    def __init__(self):
        pass

    def update(self, address, correct):
        pass

    def predict(self, address):
        # always predict 'taken'
        return True


def evaluate(sat_bits, addr_bits, trace):

    n_correct = 0
    n_total = 0

    import os.path
    tr = TraceReader(os.path.join("traces", trace + ".trace"))
    bp = BranchPredictorAlwaysTaken()

    for address, taken in tr.read():
        prediction = bp.predict(address)
        correct = prediction == taken
        bp.update(address, correct)
        if correct:
            n_correct += 1
        n_total += 1
    print("{}, {}, {}, {}".format(trace, sat_bits, addr_bits, n_correct / n_total))
    return n_correct / n_total


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true')
    parser.add_argument("--gridsearch", action='store_true')
    args = parser.parse_args()

    if args.debug:
        tr = TraceReader("../evaluation/traces/dummy.trace")
        bp = BranchPredictorAlwaysTaken()

        for address, taken in tr.read():
            prediction = bp.predict(address)
            correct = prediction == taken
            bp.update(address, correct)

    if args.gridsearch:

        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=8) as executor:
            for sat_bits in [1, 2, 3, 4, 5]:
                for addr_bits in [3, 6, 9, 12, 15]:
                    for trace in ["short_mobile_1", "long_mobile_1", "short_server_1", "long_server_1"]:
                        executor.submit(evaluate, sat_bits, addr_bits, trace)
