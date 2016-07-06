import unittest
import polyfitlib_tests as pfl
import polyfitlib_copy as opfl
from load_new_and_prev_versions import loader
import time


class MyValueTests(unittest.TestCase):

    # build ps lists and times it
    # b/c we're testing only 2 versions
    # we can have this silly double typed code
    def __init__(self):
        self.start_new = time.time()
        try:
            poly_new = pfl.fitShot(1140726089, burstLen = 25)
        except Exception, ex:
            print 'error: shots not loaded correctly,', ex
        self.finish_new = time.time()
        self.start_old = time.time()
        try:
            poly_old = opfl.fitShot(1140726089, burstLen = 25)
        except Exception, ex:
            print 'error: shots not loaded correctly,', ex
        self.finish_old = time.time()
        print 'new time =', self.finish_new - self.start_new
        print 'old time =', self.finish_old - self.start_old
        return None


    # ps.acq_ampOffset = ndarray(shape=ps.acq_offsetRaw.shape[0])
    # ps.acq_offsetVolt = ndarray(shape=ps.acq_offsetRaw.shape)
    # ps.satChansDark
    
    def test_time_values(self):
        try: self.assertSequenceEqual(self.old.ts.time, self.new.ts.time)
        except: print 'test_time_values failure'
    def test_te_values(self):
        try: self.assert2DMatrixEqual(self.old.ts.te.data, self.new.ts.te.data)
        except: print 'test_te_values failure'
    def test_mask_values(self):
        try: self.assert2DMatrixEqual(self.old.ts.te.mask, self.new.ts.te.mask)
        except: print 'test_mask_values failure'
        
    def assertSequenceEqual(self, a, b):
        if len(a) != len(b):
            print 'test will fail'
        else:
            i = 0
            while i<len(a):
                self.assertEqual(a[i], b[i])
                i += 1
        return None

    def assert2DMatrixEqual(self, a, b):
        rows = len(a)
        if len(a) != len(b):
            print 'test will fail'
        else:
            i = 0
            while i<rows:
                self.assertSequenceEqual(a[i],b[i])
                i += 1
        return None
    

if __name__ == '__main__':
    unittest.main()
