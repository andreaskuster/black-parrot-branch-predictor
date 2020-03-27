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

import os.path

from base import BranchPredictor, TraceReader, Evaluator


class BranchPredictorAlwaysTaken(BranchPredictor):
    """
    The always taken branch predictor is a static and ultra light-weight (area, power) branch predictor. Like the name
    already reveals, it simply predicts all branches as 'taken'. This is the python model implementation.
    """

    def __init__(self):
        """
        Initialize internal state.
        """
        # no internal state to initialize
        pass

    def update(self, address, correct):
        """

        :param address:
        :param correct:
        :return:
        """
        # nothing to update
        pass

    def predict(self, address):
        """

        :param address:
        :return:
        """
        # always predict 'taken'
        return True


def evaluate(sat_bits, addr_bits, trace):

    n_correct = 0
    n_total = 0

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

    # process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--gridsearch", action="store_true")
    args = parser.parse_args()

    # debugging
    if args.debug:

        # instantiate trace reader with the dummy trace
        tr = TraceReader("../traces/dummy.trace")

        # instantiate branch predictor
        bp = BranchPredictorAlwaysTaken()

        # loop over all trace lines
        for address, taken in tr.read():
            # predict branch
            prediction = bp.predict(address)
            # check if prediction was correct
            correct = prediction == taken
            # update internal predictor state
            bp.update(address, correct)

    # parameter grid search
    if args.gridsearch:

        # instantiate evaluator
        ev = Evaluator(branch_predictor=BranchPredictorAlwaysTaken, num_processes=4)

        # add all evaluation corners
        for trace in ["short_mobile_1", "long_mobile_1", "short_server_1", "long_server_1"]:
            ev.submit(trace)

        # wait for all tasks to finish
        ev.finalize()
        # write result to file
        ev.write_result("gridsearch_bp_always_not_taken.csv")
        # print result
        ev.print_result()
