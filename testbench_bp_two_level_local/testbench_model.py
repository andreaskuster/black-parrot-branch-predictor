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


class BranchPredictorTwoLevelLocal:

    def __init__(self, sat_cnt_bits, bht_addr_bits, n_hist):
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
        # extract relevant index bits
        bct_index = address % self.bct_size
        # level 1 lookup
        gpt_index = self.bct[bct_index].reg_to_number()
        # level 2 lookup and comparison
        return self.gpt[gpt_index].value() > self.saturation_size_half


def evaluate(sat_bits, addr_bits, n_hist, trace):

    n_correct = 0
    n_total = 0

    tr = TraceReader(trace)
    bp = BranchPredictorTwoLevelLocal(sat_cnt_bits=sat_bits, bht_addr_bits=addr_bits, n_hist=n_hist)

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
    parser.add_argument("--debug", action='store_true')
    parser.add_argument("--gridsearch", action='store_true')
    args = parser.parse_args()

    if args.debug:

        # params
        _SAT_CNT_BITS = 2
        _BHT_ADDR_BITS = 1
        _N_HIST = 1

        tr = TraceReader("../evaluation/traces/dummy.trace")
        bp = BranchPredictorTwoLevelLocal(sat_cnt_bits=_SAT_CNT_BITS, bht_addr_bits=_BHT_ADDR_BITS, n_hist=_N_HIST)

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
            with open("gridsearch_two_level_local.txt", "w") as file:
                for result in results:
                    file.write(str(result) + "\n")
        print("done")
