# This program is written by Dylan Adams on 07/07/16
# My cheating ex girlfriend's birthday is today
# You bet she's not getting a happy birthday from me

# This file contains a
# 1. test running script: main
# 2. definition for test handling object: MyTests
# Common testing methods are in my_test_methods.py


import polyfitlib_tests as pfl
import polyfitlib as opfl
import time

def main():

    # time fitShot routine to compare new/ old analysis
    start_new = time.time()
    try:
        poly_new = pfl.fitShot(1140726089, burstLen=25)
        new = poly_new.data
    except Exception, ex:
        print 'error: shots not loaded correctly,', ex
    finish_new = time.time()
    print 'new time =', finish_new - start_new
    start_old = time.time()
    try:
        poly_old = opfl.fitShot(1140726089, burstLen=25)
        old = poly_old.data
    except Exception, ex:
        print 'error: shots not loaded correctly,', ex
    finish_old = time.time()
    print 'old time =', finish_old - start_old

    # Using shot data, check attributes in testing suite
    tests = MyTests()
    tests.load_shots(old, new)
    suite = ['errNum', 'chanFlagDC', 'chanFlagAC',
     'satChans', 'satChansDark', 'str_offsetVolt',
     'str_ampOffset', 'acq_offsetVolt', 'acq_ampOffset',
     'STRUCK_MIN', 'STRUCK_MAX']
    for i in xrange(0,len(suite)):
        tests.run_method(suite[i])

    return tests




# Test object takes shot data and performs analysis
# shots must be loaded into shot to maintain small size of test code
# This helps keep the test modular

import unittest
from my_test_methods import iterate_method, assertSequenceEqual, assert2DMatrixEqual

class MyTests(unittest.TestCase):

    def __init__(self):
        self.new = []
        self.old = []

    def load_shots(self, old, new):
        self.new = new
        self.old = old

    # essentially assertEqual for more than one comparison
    def run_method(self, method):
        iterate_method(self, method)

    def assertSequenceEqual(self, a, b):
        assertSequenceEqual(self, a, b)

    def assert2DMatrixEqual(self, a, b):
        assert2DMatrixEqual(self, a, b)



