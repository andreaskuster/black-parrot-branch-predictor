import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.result import TestFailure
from adder_model import adder_model

clock_period = 1000


@cocotb.coroutine
def clock_gen(signal, period=10000):
    while True:
        signal <= 0
        yield Timer(period / 2)
        signal <= 1
        yield Timer(period / 2)


@cocotb.coroutine
def adder_basic(dut, a, b):
    cocotb.fork(clock_gen(dut.clk_i, period=clock_period))

    dut.rst_i <= 1
    yield RisingEdge(dut.clk_i)
    dut.rst_i <= 0

    dut.a_i <= a
    dut.b_i <= b

    yield RisingEdge(dut.clk_i)
    yield RisingEdge(dut.clk_i)

    got = int(dut.sum_o.value)

    if got != adder_model(a, b):
        raise TestFailure('Mismatch detected: got %d, exp %d!' % (got, adder_model(a, b)))
    else:
        dut._log.info('Got value: %d' % got)


@cocotb.test()
def adder_basic_test(dut):
    """ Test 35 + 7 = 42 """
    yield adder_basic(dut, 35, 7)
