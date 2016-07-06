import unittest
import polyfitlib_tests as pfl
import polyfitlib as opfl
import time


class AmpOffsetTests(unittest.TestCase):

    # build ps lists and times it
    # b/c we're testing only 2 versions
    # we can have this silly double typed code
    def __init__(self):
        self.start_new = time.time()
        try:
            poly_new = pfl.fitShot(1140726089, burstLen=25)
            self.new = poly_new
        except Exception, ex:
            print 'error: shots not loaded correctly,', ex
        self.finish_new = time.time()
        self.start_old = time.time()
        try:
            poly_old = opfl.fitShot(1140726089, burstLen=25)
            self.old = poly_old
        except Exception, ex:
            print 'error: shots not loaded correctly,', ex
        self.finish_old = time.time()
        print 'new time =', self.finish_new - self.start_new
        print 'old time =', self.finish_old - self.start_old

    def test_errNum_values(self, n):
        try:
            self.assertEqual(self.new[n].errNum, self.old[n].errNum)
        except Exception, ex:
            print 'errNum_values failure, n=', n, 'ex =', ex

    def test_str_offsetRaw_values(self, n, m):
        try:
            self.assert2DMatrixEqual(self.old[n].str_offsetRaw[m], self.new[n].str_offsetRaw[m])
        except Exception, ex:
            print 'strOffsetRaw values failure, n=', n, 'm=', m, 'ex =', ex
        
        
    def assertSequenceEqual(self, a, b):
        if len(a) != len(b):
            print 'test will fail'
        else:
            i = 0
            while i < len(a):
                self.assertEqual(a[i], b[i])
                if a[i] != b[i]:
                    i = len(a)
                i += 1

    def assert2DMatrixEqual(self, a, b):
        rows = len(a)
        test_ind = 0
        if len(a) != len(b):
            print 'test will fail'
        else:
            i = 0
            while i < rows:
                try:
                    self.assertSequenceEqual(a[i],b[i])
                except:
                    i = rows
                i += 1
    

if __name__ == '__main__':
    unittest.main()
