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


class BranchPredictorTournament:
    """
    The tournament branch predictor is a dynamic branch predictor. It indexes saturation counter using the branch address
    xor-ed with the branch history in the branch history table which indicate the likelihood of predicting the branch
    to be 'taken'. The counter increments for each actual branch taken and decrements for each actual not taken
    branch. This is the python model implementation.
    """

    def __init__(self, sat_cnt_bits, bht_addr_bits, n_hist):
        """
        Initialize internal state.
        :param sat_cnt_bits: saturating counter bit width
        :param bht_addr_bits: number of address bits for the branch history table index and the branch history shift register
        :param n_hist:
        """
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
        """
        Update internal state using the information from the most recent prediction result.
        :param address: branch address
        :param correct: flag indicating whether the last prediction was correct
        :return: None
        """
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
        # update counter
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
        # compute correct branch decision
        local_correct = (local_prediction == taken_actual)
        global_correct = (global_prediction == taken_actual)
        # update counter
        if local_correct and not global_correct:
            self.bht_sel.count_down()
        elif not local_correct and global_correct:
            self.bht_sel.count_up()
        # update branch history shift register
        self.bh.shift(taken_actual)

    def predict(self, address):
        """
        Predict branch using the internal state and the branch address.
        :param address: branch address
        :return: prediction
        """
        # check which branch predictor we trust (selector)
        if self.predict_selector():
            return self.predict_global()
        else:
            return self.predict_local(address)

    def predict_local(self, address):
        """
        Predict local (branch address)
        :param address: branch address
        :return: local prediction
        """
        # local branch predictor
        return self.bht_local[address % self.bht_local_size].value() > self.saturation_size_half

    def predict_global(self):
        """
        Predict global (branch history).
        :return: global prediction
        """
        # global branch predictor
        return self.bht_global[self.bh.reg_to_number()].value() > self.saturation_size_half

    def predict_selector(self):
        """
        Decide which predictor (local vs global) to choose.
        :return: decision
        """
        # selector
        return self.bht_sel.value() > self.saturation_size_half


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
        _BHT_ADDR_BITS = 2
        _N_HIST = 2
        bp = BranchPredictorTournament(sat_cnt_bits=_SAT_CNT_BITS, bht_addr_bits=_BHT_ADDR_BITS, n_hist=_N_HIST)

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
        ev = Evaluator(branch_predictor=BranchPredictorTournament, num_processes=4)

        # add all evaluation corners
        for trace in ["short_mobile_1", "long_mobile_1", "short_server_1", "long_server_1"]:
            for sat_bits in [1, 2, 3, 4, 5]:
                for addr_bits in [3, 6, 9, 12, 15]:
                        ev.submit(trace, sat_bits, addr_bits)

        # wait for all tasks to finish
        ev.finalize()
        # write result to file
        ev.write_result("gridsearch_bp_gshare.csv")
        # print result
        ev.print_result()
