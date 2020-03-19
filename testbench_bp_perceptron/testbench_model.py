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

import os
import argparse

import numpy as np


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


class TraceReader:

    def __init__(self, filename):
        self.filename = filename

    def read(self):
        with open(self.filename, "r") as file:
            for line in file:
                address, taken = line.split()
                yield int(address)//4, int(taken)  # remove lowest 2 bits from address, since they are always 0


class BranchPredictorPerceptron:
    """
        implementation details:
            - integer weights
            - input: boolean
            - online training with single "round" for training with new dataset
    """

    def __init__(self, bht_addr_bits, n_hist, learning_rate=1):
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
        bin_no = [int(x) for x in np.binary_repr(number)]
        if length is None:
            return bin_no
        else:
            return [0]*(length-len(bin_no)) + bin_no

    def update(self, address, correct):
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
        # prepare perceptron input
        inputs = ((address * (2 ** self.n_hist)) + self.gh.reg_to_number()) % (2**self.n_inputs)
        # convert int to bit vector
        input_vec = self.int_to_bit_vec(inputs, length=self.n_inputs)
        # compute sum(input[i]*weight[i]) + bias
        activation = np.dot(input_vec, self.weights[1:]) + self.weights[0]
        # apply activation function
        return 20 if activation > 10 else 0


def evaluate(sat_bits, addr_bits, n_hist, trace):

    n_correct = 0
    n_total = 0

    tr = TraceReader(trace)
    bp = BranchPredictorPerceptron(sat_cnt_bits=sat_bits, bht_addr_bits=addr_bits, n_hist=n_hist)

    for address, taken in tr.read():
        prediction = bp.predict(address)
        correct = prediction == taken
        bp.update(address, correct)
        if correct:
            n_correct += 1
        n_total += 1
    result = [trace, sat_bits, addr_bits, n_correct / n_total]
    print(result)
    return result


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--gridsearch", action="store_true")
    args = parser.parse_args()

    if args.debug:

        # params
        _BHT_ADDR_BITS = 4
        _N_HIST = 0

        tr = TraceReader("../evaluation/traces/dummy2.trace")
        bp = BranchPredictorPerceptron(bht_addr_bits=_BHT_ADDR_BITS, n_hist=_N_HIST)

        for address, taken in tr.read():
            # remove upper bits
            address = address % (2**_BHT_ADDR_BITS)
            # predict branch
            prediction = 1 if bp.predict(address) > 10 else 0
            # determine if prediction was correct
            correct = prediction == taken
            # update internal state
            bp.update(address, correct)

    if args.gridsearch:
        from multiprocessing import Pool
        tasks = list()
        with Pool(processes=64) as pool:
            for sat_bits in [1, 2, 3, 4, 5]:
                for addr_bits in [3, 6, 9, 12, 15]:
                    for trace in ["short_mobile_1", "long_mobile_1", "short_server_1", "long_server_1"]:
                        tasks.append(pool.apply_async(evaluate, (sat_bits, addr_bits, addr_bits, os.path.join("../evaluation/traces", trace + ".trace"))))
            results = list()
            for task in tasks:
                results.append(task.get())
            with open("gridsearch_perceptron.txt", "w") as file:
                for result in results:
                    file.write(str(result) + "\n")
        print("done")
