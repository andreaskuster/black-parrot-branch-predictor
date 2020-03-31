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

from base import Evaluator, TraceReader, SaturationCounter, ShiftRegister


class BranchPredictorTwoLevelLocal:
    """
    The two-level local branch predictor is a dynamic branch predictor. The saturating counter is choosen indirectly via
    a lookup in in the correlation table. The correlation table stores branch histories indexed by the address bits. This
    is the python model implementation.
    """

    def __init__(self, sat_cnt_bits, bht_addr_bits, n_hist):
        """
        Initialize internal state.
        :param sat_cnt_bits: saturating counter bit width
        :param bht_addr_bits: number of address bits for the branch history table index and the branch history shift register
        """
        # store parameters
        self.sat_cnt_bits = sat_cnt_bits
        self.bct_size = 2 ** bht_addr_bits
        self.n_hist = n_hist
        self.gpt_size = 2 ** n_hist
        # set helper variable for highest not-taken values
        self.saturation_size_half = (2 ** (sat_cnt_bits-1))-1
        # init correlation table
        self.bct = [ShiftRegister(size=n_hist) for x in range(self.bct_size)]
        # init global pattern table
        self.gpt = [SaturationCounter(n_bits=sat_cnt_bits, init_val=self.saturation_size_half) for x in range(self.gpt_size)]

    def update(self, address, correct):
        """
        Update internal state using the information from the most recent prediction result.
        :param address: branch address
        :param correct: flag indicating whether the last prediction was correct
        :return: None
        """
        # extract relevant index bits
        bct_index = address % self.bct_size
        # update counter
        taken_predict = self.predict(address)
        taken_actual = (correct and taken_predict) or (not correct and not taken_predict)
        # level 1 lookup
        gpt_index = self.bct[bct_index].reg_to_number()
        if taken_actual:
            # level 2 update
            self.gpt[gpt_index].count_up()
        else:
            # level 2 update
            self.gpt[gpt_index].count_down()
        # update global history
        self.bct[bct_index].shift(taken_actual)

    def predict(self, address):
        """
        Predict branch using the internal state and the branch address.
        :param address: branch address
        :return: prediction
        """
        # extract relevant index bits
        bct_index = address % self.bct_size
        # level 1 lookup
        gpt_index = self.bct[bct_index].reg_to_number()
        # level 2 lookup and comparison
        return self.gpt[gpt_index].value() > self.saturation_size_half


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
        _N_HIST = 1
        bp = BranchPredictorTwoLevelLocal(sat_cnt_bits=_SAT_CNT_BITS, bht_addr_bits=_BHT_ADDR_BITS, n_hist=_N_HIST)

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
        ev = Evaluator(branch_predictor=BranchPredictorTwoLevelLocal, num_processes=4)

        # add all evaluation corners
        for trace in ["short_mobile_1", "long_mobile_1", "short_server_1", "long_server_1"]:
            for sat_bits in [1, 2, 3, 4, 5]:
                for addr_bits in [3, 6, 9, 12, 15]:
                        ev.submit(trace, sat_bits, addr_bits)

        # wait for all tasks to finish
        ev.finalize()
        # write result to file
        ev.write_result("gridsearch_bp_two_level_local.csv")
        # print result
        ev.print_result()