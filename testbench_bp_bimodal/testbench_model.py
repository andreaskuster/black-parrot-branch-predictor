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

from base import TraceReader, SaturationCounter, Evaluator


class BranchPredictorBimodal:
    """
    The bimodal branch predictor is a dynamic branch predictor. It indexes saturation counter in the branch history table
    which indicate the likelihood of predicting the branch to be 'taken'. The counter increments for each actual branch
    taken and decrements for each actual not taken branch. This is the python model implementation.
    """

    def __init__(self, sat_cnt_bits, bht_addr_bits):
        """
        Initialize internal state.
        :param sat_cnt_bits: saturating counter bit width
        :param bht_addr_bits: number of address bits for the branch history table index
        """
        # store parameters
        self.sat_cnt_bits = sat_cnt_bits
        self.bht_size = 2 ** bht_addr_bits
        # set helper variable for highest not-taken values
        self.saturation_size_half = (2 ** (sat_cnt_bits-1))-1
        # init branch history table
        self.bht = [SaturationCounter(n_bits=sat_cnt_bits, init_val=self.saturation_size_half) for _ in range(self.bht_size)]

    def update(self, address, correct):
        """
        Update internal state using the information from the most recent prediction result.
        :param address:
        :param correct:
        :return: None
        """
        # extract relevant index bits
        index = address % self.bht_size
        # update counter
        taken = self.predict(address)
        if (correct and taken) or (not correct and not taken):
            self.bht[index].count_up()
        else:
            self.bht[index].count_down()

    def predict(self, address):
        """
        Predict branch using the internal state and the branch address.
        :param address: branch address
        :return: prediction
        """
        # extract relevant index bits
        index = address % self.bht_size
        return self.bht[index].value() > self.saturation_size_half


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
        _SAT_CNT_BITS = 2
        _BHT_ADDR_BITS = 1
        bp = BranchPredictorBimodal(sat_cnt_bits=_SAT_CNT_BITS, bht_addr_bits=_BHT_ADDR_BITS)

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
        ev = Evaluator(branch_predictor=BranchPredictorBimodal, num_processes=4)

        # add all evaluation corners
        for trace in ["short_mobile_1", "long_mobile_1", "short_server_1", "long_server_1"]:
            for sat_bits in [1, 2, 3, 4, 5]:
                for addr_bits in [3, 6, 9, 12, 15]:
                    ev.submit(trace, sat_bits, addr_bits)

        # wait for all tasks to finish
        ev.finalize()
        # write result to file
        ev.write_result("gridsearch_bp_bimodal.csv")
        # print result
        ev.print_result()
