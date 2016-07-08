# This program is written by Dylan Adams on 07/07/16
# My cheating ex girlfriend's birthday is today
# You bet she's not getting a happy birthday from me

# This file contains a
# 1. test running script: main
# 2. definition for test handling object: MyTests
# Common testing methods are in my_test_methods.py
# main script runs full suite comparing variables
# involved in each step of fitPolySeg routine
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
    # every str provided needs definition in it_handler()
    # this function is in my_test_methods.py

    tests = MyTests()
    tests.load_shots(old, new)
    suite_list = []

    suite_AmpOffset = ['errNum', 'chanFlagDC', 'chanFlagAC',
                       'satChans', 'satChansDark', 'str_offsetVolt',
                       'str_ampOffset', 'acq_offsetVolt', 'acq_ampOffset',
                       'STRUCK_MIN', 'STRUCK_MAX']
    suite_list.append((suite_AmpOffset, 'AmpOffset'))

    suite_VoltageFromRawData = ['errNum', 'str_ampOffset', 'acq_ampOffset',
                                'str_voltData', 'acq_voltData']
    suite_list.append((suite_VoltageFromRawData, 'VoltageFromRawData'))

    suite_T0 = ['errNum', 'str_voltData', 'acq_voltData',
                't00_dc', 't0_dc', 't00_ac',
                't0_ac', 't0DCBgCoeffs', 't0ACBgCoeffs',
                'calib.charPulseDC', 'calib.charPulseAC']
    suite_list.append((suite_T0, 'T0'))

    suite_TransMask = ['errNum', 'calib.trans']
    suite_list.append((suite_TransMask, 'TransMask'))

    suite_NumPhotons = ['errNum', 'chanFlagDC', 'satChans',
                        'noPulseFitChans', 'str_voltData', 't0_dc',
                        'polyPulseCoeffs0', 'polyPulseCoeffsDC',
                        'cPulseStart', 'cPulseEnd', 'scatPhotonsDC',
                        'bgPhotons', 'errPhotons', 'scatPhotonsAC',
                        'STRUCK_MIN', 'STRUCK_MAX']
    suite_list.append((suite_NumPhotons, 'NumPhotons'))

    suite_FilterChans = ['errNum', 'chanFlagDC', 'chanFlagAC',
                         'str_voltData', 'scatPhotonsDC', 'scatPhotonsAC',
                         'bgPhotons', 'scPhotons_Bayes', 'bgPhotons_Bayes',
                         'fqe_Bayes', 'trans_Bayes']
    suite_list.append((suite_FilterChans, 'FilterChans'))

    suite_ScatteringAngle = ['scatAng']
    suite_list.append((suite_ScatteringAngle, 'ScatteringAngle'))

    suite_LambdaArray = ['calib.lam']
    suite_list.append((suite_LambdaArray, 'LambdaArray'))


    # loop routine to run every test in every suite
    # print statement provides much needed clarity

    for j in xrange(0,len(suite_list)):
        print '\n'+'Moving onto', suite_list[j][1]
        for i in xrange(0,len(suite_list[j][0])):
            tests.run_method(suite_list[j][0][i])

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



