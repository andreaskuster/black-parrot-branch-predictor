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