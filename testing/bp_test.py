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
import sys
import unittest

import os.path

from subprocess import Popen, PIPE

import xml.etree.ElementTree as ET


class TestbenchTest(unittest.TestCase):

    _TEST_BENCHES = ["testbench_example", "testbench_bp_bimodal", "testbench_bp_gshare", "testbench_bp_always_taken"
                     "testbench_bp_gselect", "testbench_bp_tournament", "testbench_bp_two_level_local"]

    def test_all(self):

        for test_bench in self._TEST_BENCHES:
            self.run_testbench(test_case=test_bench)

    def run_testbench(self, verbose=True, test_case="testbench_example"):

        parent = os.path.abspath(os.path.join(os.path.curdir, os.pardir))

        process = Popen(["make", test_case], stdout=PIPE, stderr=PIPE, cwd=parent)

        if verbose:
            while process.poll() is None:
                line = str(process.stdout.readline(), encoding="utf-8")
                print(line)
            print(str(process.stdout.read(), encoding="utf-8"))
        else:
            process.wait()

        tree = ET.parse(os.path.join(parent, test_case, "results.xml"))

        root = tree.getroot()
        results = root.findall("testsuite/testcase")

        for item in results:
            print("test case: {}".format([str(x) + ": " + str(item.attrib[x]) for x in item.attrib]))
            for subitem in item:
                if subitem.tag == "failure":
                    error = "test case: {}".format([str(x) + ": " + str(item.attrib[x]) for x in item.attrib]) + \
                            "\n failure: {}".format([str(x) + ": " + str(subitem.attrib[x]) for x in subitem.attrib])
                    self.fail(error)


if __name__ == "__main__":
    """
        Run all unit tests.
    """
    # run tests
    unittest.main()
    # exit
    sys.exit(0)




