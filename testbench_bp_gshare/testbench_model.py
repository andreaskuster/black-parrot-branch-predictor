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
"""
        for i in range(self.size):
            number += (2 ** i)*self.register[i]
        return number
"""

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


class BranchPredictorGshare:

    def __init__(self, sat_cnt_bits, bht_addr_bits):
        # store parameters
        self.sat_cnt_bits = sat_cnt_bits
        self.bht_size = 2 ** bht_addr_bits
        # set helper variable for highest not-taken values
        self.saturation_size_half = (2 ** (sat_cnt_bits-1))-1
        # init branch history table
        self.bht = [SaturationCounter(n_bits=sat_cnt_bits, init_val=self.saturation_size_half) for x in range(self.bht_size)]
        # init global history shift reg
        self.gh = ShiftRegister(size=bht_addr_bits, init_val=0)

    def update(self, address, correct):
        # extract relevant index bits
        index = (address ^ self.gh.reg_to_number()) % self.bht_size
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
        index = (address ^ self.gh.reg_to_number()) % self.bht_size
        return self.bht[index].value() > self.saturation_size_half


def evaluate(sat_bits, addr_bits, trace):

    n_correct = 0
    n_total = 0

    import os.path
    tr = TraceReader(os.path.join("traces", trace + ".trace"))
    bp = BranchPredictorGshare(sat_cnt_bits=sat_bits, bht_addr_bits=addr_bits)

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


    _SAT_CNT_BITS = 2
    _BHT_ADDR_BITS = 6

    if args.debug:
        tr = TraceReader("../evaluation/traces/dummy.trace")
        bp = BranchPredictorGshare(sat_cnt_bits=_SAT_CNT_BITS, bht_addr_bits=_BHT_ADDR_BITS)

        for address, taken in tr.read():
            # remove upper bits
            address = address % (2**_BHT_ADDR_BITS)

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
