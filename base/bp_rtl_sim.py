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

import cocotb

from cocotb.triggers import Timer, RisingEdge
from cocotb.result import TestFailure


class BpRtlSim:

    @staticmethod
    @cocotb.coroutine
    def clock_gen(signal, period=10000):
        while True:
            signal <= 0
            yield Timer(period / 2)
            signal <= 1
            yield Timer(period / 2)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    @cocotb.coroutine
    def bp_predict(dut, index, model_prediction):

        # read
        dut.r_v_i <= 1
        dut.idx_r_i <= index

        # simulate a clock edge
        yield RisingEdge(dut.clk_i)

        # read prediction
        dut_prediction = int(dut.predict_o.value)
        dut._log.info("Got value: {}".format(dut_prediction))
        if dut_prediction != model_prediction:
            raise TestFailure("Mismatch detected: dut {}, model {}".format(dut_prediction, model_prediction))

        dut.r_v_i <= 0
        dut.idx_r_i <= 0

        # simulate a clock edge
        yield RisingEdge(dut.clk_i)
