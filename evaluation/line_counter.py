import os

if __name__ == "__main__":
    """
    Counts the number of traces in all trace files.
    """
    _BASE_PATH = "traces"

    traces = [f for f in os.listdir(_BASE_PATH) if os.path.isfile(os.path.join(_BASE_PATH, f)) and f.endswith(".trace")]

    for trace in traces:
        counter = 0
        with open(os.path.join("traces", trace)) as file:
            for line in file:
                counter += 1
        print("{}: {}".format(trace, counter))
