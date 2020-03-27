#!/usr/bin/env python3
# encoding: utf-8

"""
    Copyright (C) 2020  Andreas Kuster

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Andreas Kuster"
__copyright__ = "Copyright 2020"
__license__ = "GPL"

import os
import cocotb

from cocotb.triggers import RisingEdge

from testbench_bp_bimodal import BranchPredictorBimodal
from base import TraceReader, BpRtlSim


@cocotb.test()
def branch_predictor_basic(dut):
    """branch predictor basic"""

    # setup clock gen
    cocotb.fork(BpRtlSim.clock_gen(dut.clk_i, period=1000))

    # init vars
    yield BpRtlSim.bp_init(dut)

    # reset
    yield BpRtlSim.bp_reset(dut)

    # read trace name from environment variable (set in the Makefile)
    trace = os.environ["TRACE"]

    # instantiate trace reader with the given trace
    tr = TraceReader(os.path.join("../traces", trace + ".trace"))

    # instantiate branch predictor
    _SAT_CNT_BITS = 2
    _BHT_ADDR_BITS = 9
    bp = BranchPredictorBimodal(sat_cnt_bits=_SAT_CNT_BITS, bht_addr_bits=_BHT_ADDR_BITS)

    # loop over all trace lines
    for address, taken in tr.read():
        # predict branch
        pred_model = bp.predict(address)
        # wait for the simulation
        yield BpRtlSim.bp_predict(dut, address, pred_model)
        # check if prediction was correct
        correct = pred_model == taken
        # update internal predictor state
        bp.update(address, correct)
        # wait for the simulation
        yield BpRtlSim.bp_update(dut, address, correct)

    yield RisingEdge(dut.clk_i)
    dut._log.info("Co-simulation finished.")
