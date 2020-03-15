import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.result import TestFailure
from testbench_model import BranchPredictorGselect, TraceReader

clock_period = 1000

@cocotb.coroutine
def clock_gen(signal, period=10000):
    while True:
        signal <= 0
        yield Timer(period / 2)
        signal <= 1
        yield Timer(period / 2)

@cocotb.coroutine
def bp_init(dut):
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
    # read
    dut.r_v_i <= 1
    dut.idx_r_i <= index

    # simulate a clock edge
    yield RisingEdge(dut.clk_i)

    # read prediction
    dut_prediction = int(dut.predict_o.value)
    #dut._log.info('Got value: %d' % dut_prediction)
    if dut_prediction != model_prediction:
        raise TestFailure('Mismatch detected: dut %d, model %d!' % (dut_prediction, model_prediction))

    dut.r_v_i <= 0
    dut.idx_r_i <= 0

    # simulate a clock edge
    yield RisingEdge(dut.clk_i)


@cocotb.test()
def branch_predictor_basic(dut):
    """branch predictor basic"""
    _SAT_CNT_BITS = 2
    _BHT_ADDR_BITS = 9
    _N_HIST = 6

    # setup clock gen
    cocotb.fork(clock_gen(dut.clk_i, period=clock_period))

    # init vars
    yield bp_init(dut)

    # reset
    yield bp_reset(dut)

    tr = TraceReader("../evaluation/traces/dummy.trace")
    bp = BranchPredictorGselect(sat_cnt_bits=_SAT_CNT_BITS, bht_addr_bits=_BHT_ADDR_BITS, n_hist=_N_HIST)

    dut._log.info("global history: {}".format(dut.bp.gh))
    #dut._log.info("cnt0: {}, cnt1: {}, cnt2: {}, cnt3: {}".format(dut.bp.c0, dut.bp.c1, dut.bp.c2, dut.bp.c3))
    dut._log.info("test: {}".format(dut.bp.gh))
    dut._log.info("-----------START---------------")

    for address, taken in tr.read():

        address = address % (2**_BHT_ADDR_BITS)

        pred_model = bp.predict(address)
        yield bp_predict(dut, address, pred_model)

        correct = pred_model == taken
        bp.update(address, correct)
        yield bp_update(dut, address, correct)
        dut._log.info("global history: {}".format(dut.bp.gh))
        dut._log.info("write index: {}".format(dut.bp.idx_w_i))
        dut._log.info("correct: {}".format(dut.bp.correct_i))
        #dut._log.info("cnt0: {}, cnt1: {}, cnt2: {}, cnt3: {}".format(dut.bp.c0, dut.bp.c1, dut.bp.c2, dut.bp.c3))
        dut._log.info("--------------------------")


    yield RisingEdge(dut.clk_i)
    dut._log.info("Finished.")
