import unittest
import polyfitlib_tests as pfl
import polyfitlib as opfl
import time


class VoltageFromRawDataTests(unittest.TestCase):

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
            try:
                num_seg = len(self.old[n])
            except Exception, empty:
                continue
            for m in xrange(0,num_seg):
                try:
                    it_handler(self, method, n, m)
                except:
                    break
        finish = time.time()
        print 'time for test:', finish-start

# Build tests

    def check_errNum_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for errNum test'
            a = self.old[n][m].errNum
            b = self.new[n][m].errNum
            self.assertEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for errNum test'
    def check_str_voltData_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for str_voltData test'
            a = self.old[n][m].str_voltData
            b = self.new[n][m].str_voltData
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for str_voltData test'


    def assertSequenceEqual(self, a, b):
        if len(a) != len(b):
            print 'test will fail'
        else:
            i = 0
            while i < len(a):
                self.assertEqual(a[i], b[i])
                i += 1

    def assert2DMatrixEqual(self, a, b):
        rows = len(a)
        if len(a) != len(b):
            print 'test will fail'
        else:
            i = 0
            while i < rows:
                self.assertSequenceEqual(a[i], b[i])
                i += 1


if __name__ == '__main__':
    unittest.main()



def it_handler(test_obj, method, n, m):
    self = test_obj
    if method == 'errNum':
        try: self.check_errNum_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex
    if method == 'str_voltData':
        try: self.check_str_voltData_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex