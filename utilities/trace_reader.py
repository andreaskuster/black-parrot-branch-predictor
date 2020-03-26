class TraceReader:
    """
    The trace reader is a (memory-) lightweight iterator that yields tuples of the form (address: int, taken: bool)
    from the given trace file.
    """
    def __init__(self, filename):
        """
        Class initialization.
        :param filename: trace file location
        """
        self.filename = filename

    def read(self):
        """
        Trace file read iterator.
        :return: tuple (address: int, taken: bool)
        """
        # open file
        with open(self.filename, "r") as file:
            # read line-by-line
            for line in file:
                # split address and taken
                address, taken = line.split()
                # remove lowest 2 bits (offset) from address and return tuple
                yield int(address) // 4, int(taken)
