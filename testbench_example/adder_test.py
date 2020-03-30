import cocotb

from cocotb.triggers import Timer, RisingEdge
from cocotb.result import TestFailure

from testbench_example import adder_model

# simulation clock period in ps
clock_period = 1000


@cocotb.coroutine
def clock_gen(signal, period=1000):
    """
    Clock generator co-routine.
    :param signal: reference to dut clock input
    :param period: clock period
    :return: None
    """
    while True:
        signal <= 0
        yield Timer(period / 2)
        signal <= 1
        yield Timer(period / 2)


@cocotb.coroutine
def adder_basic(dut, a, b):
    """
    Basic adder co-routine. Simulates an addition of two integer numbers from [0, 2**DATA_WIDTH) and compares the result to
    the software model.
    :param dut: device under test: testbench.sv
    :param a: first summand
    :param b: second summand
    :return: None
    """
    # init clockgen
    cocotb.fork(clock_gen(dut.clk_i, period=clock_period))
    # apply the reset signal
    dut.rst_i <= 1
    yield RisingEdge(dut.clk_i)
    # remove reset signal
    dut.rst_i <= 0
    yield RisingEdge(dut.clk_i)
    # apply the input signal
    dut.a_i <= a
    dut.b_i <= b
    yield RisingEdge(dut.clk_i)
    yield RisingEdge(dut.clk_i)
    # get result
    result = int(dut.sum_o.value)
    # check against software model
    if result != adder_model(a, b):
        raise TestFailure("Mismatch detected: got {}, exp {}!".format(result, adder_model(a, b)))
    else:
        dut._log.info("Got value: {}".format(result))


@cocotb.test()
def adder_basic_test(dut):
    """
    Simple add test case
    :param dut: device under test: testbench.sv
    :return: None
    """
    # wait for for the test case to finish
    yield adder_basic(dut, 35, 7)
