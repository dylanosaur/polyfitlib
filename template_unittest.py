import unittest
import polyfitlib_tests as pfl
import polyfitlib as opfl
import time


class TemplateTests(unittest.TestCase):

    # build ps lists and times it
    # fitShot routine should return psList
    # not data for these tests
    def __init__(self):
        self.start_new = time.time()
        try:
            poly_new = pfl.fitShot(1140726089, burstLen=25)
            self.new = poly_new.data
        except Exception, ex:
            print 'error: shots not loaded correctly,', ex
        self.finish_new = time.time()
        self.start_old = time.time()
        try:
            poly_old = opfl.fitShot(1140726089, burstLen=25)
            self.old = poly_old.data
        except Exception, ex:
            print 'error: shots not loaded correctly,', ex
        self.finish_old = time.time()
        print 'new time =', self.finish_new - self.start_new
        print 'old time =', self.finish_old - self.start_old

# I have included this method to avoid the double nesting of loops
# as well as try/except statements
# since the ps objects have a segment and a polychromator this has
# maybe saved 4 lines of code per value check method test
# this also keeps the runner script modular
    def iterate_method(self, method='chanFlagDC'):
        start = time.time()
        num_poly = len(self.old)
        for n in xrange(0,num_poly):
# Iteration handler

# Build tests