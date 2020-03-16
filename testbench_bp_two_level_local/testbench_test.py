import cocotb

from cocotb.triggers import Timer, RisingEdge
from cocotb.result import TestFailure

from testbench_model import BranchPredictorTwoLevelLocal, TraceReader

# simulation clock period in ps
clock_period = 1000


@cocotb.coroutine
def clock_gen(signal, period=10000):
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
def bp_init(dut):
    """
    Branch predictor initialisation co-routine.
    :param dut: device under test: testbench.sv
    :return: None
    """
    # reset
    dut.reset_i = 1
    # write branch result
    dut.w_v_i = 0
    dut.idx_w_i = 0
    dut.correct_i = 0
    # read branch prediction
    dut.r_v_i = 0
    dut.idx_r_i = 0
    dut.predict_o = 0
    # simulate a clock edge
    yield RisingEdge(dut.clk_i)


@cocotb.coroutine
def bp_reset(dut):
    """
    Branch predictor reset co-routine.
    :param dut: device under test: testbench.sv
    :return: None
    """
    # reset
    dut.reset_i <= 1
    # simulate a clock edge
    yield RisingEdge(dut.clk_i)
    # remove reset flag
    dut.reset_i <= 0
    # simulate a clock edge
    yield RisingEdge(dut.clk_i)


@cocotb.coroutine
def bp_update(dut, index, correct):
    """
    Branch predictor internal state update co-routine.
    :param dut: device under test: testbench.sv
    :param index: access index
    :param correct: correct/incorrect prediction feedback
    :return: None
    """
    # write
    dut.w_v_i <= 1
    dut.idx_w_i <= index
    dut.correct_i <= correct
    # simulate a clock edge
    yield RisingEdge(dut.clk_i)
    dut.w_v_i <= 0
    dut.idx_w_i <= 0
    dut.correct_i <= 0
    # simulate a clock edge
    yield RisingEdge(dut.clk_i)


@cocotb.coroutine
def bp_predict(dut, index, model_prediction):
    """
    Branch predictor internal state update co-routine.
    :param dut: device under test: testbench.sv
    :param index: access index
    :param model_prediction: prediction from the model (for comparison)
    :return: None
    """
    # read
    dut.r_v_i <= 1
    dut.idx_r_i <= index
    # simulate a clock edge
    yield RisingEdge(dut.clk_i)
    # read prediction
    dut_prediction = int(dut.predict_o.value)
    # check correctness
    if dut_prediction != model_prediction:
        raise TestFailure("Mismatch detected: dut {}, model {}!".format(dut_prediction, model_prediction))
    # remove read signals
    dut.r_v_i <= 0
    dut.idx_r_i <= 0
    # simulate a clock edge
    yield RisingEdge(dut.clk_i)


@cocotb.test()
def branch_predictor_basic(dut):
    """
    Branch predictor trace test case.
    :param dut: device under test: testbench.sv
    :return: None
    """
    # define parameter values of the dut instance
    _SAT_CNT_BITS = 2
    _BHT_ADDR_BITS = 2
    _B_HIST = 2
    # setup clock gen
    cocotb.fork(clock_gen(dut.clk_i, period=clock_period))
    # init vars
    yield bp_init(dut)
    # reset
    yield bp_reset(dut)
    # load trace
    tr = TraceReader("../evaluation/traces/dummy.trace")
    # load model
    bp = BranchPredictorTwoLevelLocal(sat_cnt_bits=_SAT_CNT_BITS, bht_addr_bits=_BHT_ADDR_BITS, n_hist=_B_HIST)
    # co-simulate trace (model and rtl simulation)
    for address, taken in tr.read():
        # cut upper bits
        address = address % (2 ** _BHT_ADDR_BITS)
        # get model prediction
        pred_model = bp.predict(address)
        # run rtl prediction
        yield bp_predict(dut, address, pred_model)
        # compute correct predicted flag
        correct = pred_model == taken
        # update model
        bp.update(address, correct)
        # run rtl update
        yield bp_update(dut, address, correct)
    yield RisingEdge(dut.clk_i)
    # end simulation
    dut._log.info("Finished.")
