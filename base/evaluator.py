
import os.path

from multiprocessing import Pool

from base import TraceReader


class Evaluator:

    def __init__(self, branch_predictor, num_processes=4):
        self.dut = branch_predictor
        self.pool = Pool(processes=num_processes)
        self.tasks = list()
        self.results = list()

    def submit(self, trace, *args):
        self.tasks.append(self.pool.apply_async(Evaluator.evaluate, (trace, self.dut, *args)))

    def finalize(self):
        self.results = list()
        for task in self.tasks:
            self.results.append(task.get())

    def write_result(self, path):
        with open(path, "w") as file:
            for result in self.results:
                file.write(", ".join(result))
                file.write("\n")

    def get_result(self):
        return self.results

    def print_result(self):
        for result in self.results:
            print(" ".join(result))

    @staticmethod
    def evaluate(trace, dut, *args):

        n_correct = 0
        n_total = 0

        tr = TraceReader(os.path.join("../traces", trace + ".trace"))

        bp = dut(*args)

        for address, taken in tr.read():
            prediction = bp.predict(address)
            correct = prediction == taken
            bp.update(address, correct)
            if correct:
                n_correct += 1
            n_total += 1

        return [trace] + [str(arg) for arg in args] + [str(n_correct / n_total)]
