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

import numpy as np

from base import Evaluator, TraceReader, ShiftRegister


class BranchPredictorPerceptron:
    """
        TODO: add description

        implementation details:
            - integer weights
            - input: boolean
            - online training with single "round" for training with new dataset
    """

    def __init__(self, bht_addr_bits, n_hist, learning_rate=1):
        """
        Initialize internal state.
        :param bht_addr_bits: number of address bits for the branch history table index and the branch history shift register
        :param n_hist: number of branch history bits
        :param learning_rate: perceptron learning rate
        :return: None
        """
        # save params
        self.bht_addr_bits = bht_addr_bits
        self.n_hist = n_hist
        # number of inputs
        self.n_inputs = bht_addr_bits + n_hist
        # perceptron params
        self.learning_rate: int = learning_rate
        self.weights: np.array = np.zeros(self.n_inputs + 1, dtype=int)
        # add global history shift register
        self.gh = ShiftRegister(size=n_hist)

    def int_to_bit_vec(self, number, length=None):
        """
        Convert the integer value to its bit representation as a vector.
        :param number: input integer value
        :param length: length of bit vector
        :return: corresponding bit vector
        """
        bin_no = [int(x) for x in np.binary_repr(number)]
        if length is None:
            return bin_no
        else:
            return [0]*(length-len(bin_no)) + bin_no

    def update(self, address, correct):
        """
        Update internal state using the information from the most recent prediction result.
        :param address: branch address
        :param correct: flag indicating whether the last prediction was correct
        :return: None
        """
        # prepare perceptron input
        inputs = ((address * (2 ** self.n_hist)) + self.gh.reg_to_number()) % (2**self.n_inputs)
        # convert int to bit vector
        input_vec = np.array(self.int_to_bit_vec(inputs, length=self.n_inputs))
        # compute prediction
        prediction = self.predict(inputs)
        # determine actual outcome
        taken_actual = (correct and prediction) or (not correct and not prediction)
        # update perceptron weights
        label = 20 if taken_actual else 0
        # update weights
        self.weights[1:] += self.learning_rate * (label - prediction) * input_vec
        # update bias
        self.weights[0] += self.learning_rate * (label - prediction)

    def predict(self, address):
        """
        Predict branch using the internal state and the branch address.
        :param address: branch address
        :return: prediction
        """
        # prepare perceptron input
        inputs = ((address * (2 ** self.n_hist)) + self.gh.reg_to_number()) % (2**self.n_inputs)
        # convert int to bit vector
        input_vec = self.int_to_bit_vec(inputs, length=self.n_inputs)
        # compute sum(input[i]*weight[i]) + bias
        activation = np.dot(input_vec, self.weights[1:]) + self.weights[0]
        # apply activation function
        return 20 if activation > 10 else 0


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
        _BHT_ADDR_BITS = 4
        _N_HIST = 0
        bp = BranchPredictorPerceptron(bht_addr_bits=_BHT_ADDR_BITS, n_hist=_N_HIST)

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
        ev = Evaluator(branch_predictor=BranchPredictorPerceptron, num_processes=4)

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
