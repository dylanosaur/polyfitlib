import unittest
import polyfitlib_tests as pfl
import polyfitlib as opfl
import time


class AmpOffsetTests(unittest.TestCase):

    # build ps lists and times it
    # fitShot routine should return psList
    # not data for these tests
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

    def test_errNum_values(self):
        n = 0
        while n < len(self.old):
            try:
                self.assertEqual(self.new[n].errNum, self.old[n].errNum)
                n += 1
            except Exception, ex:
                print 'errNum_values failure, n=', n, 'ex =', ex
                break
        # close while loop

    def test_str_offsetRaw_values(self):
        n = 0
        while n < len(self.old):
            m = 0
            while m < len(self.old[n].str_offsetRaw):
                try:
                    self.assert2DMatrixEqual(self.old[n].str_offsetRaw[m], self.new[n].str_offsetRaw[m])
                    m += 1
                except Exception, ex:
                    print 'strOffsetRaw values failure, n=', n, 'm=', m, 'ex =', ex
                    break
            n += 1
        # close while loop

    def test_shapes_values(self):
        i = 0
        while i < len(self.old):
            try:
                self.assertSequenceEqual(self.old[i].str_offsetRaw.shape, self.new[i].str_offsetRaw.shape)
                self.assertSequenceEqual(self.old[i].acq_offsetRaw.shape, self.new[i].acq_offsetRaw.shape)
                i += 1
            except Exception, ex:
                print 'shapes (array dimensions) values mismatch, psNum=', i, 'ex=', ex
                break

    def test_chanFlagDC_values(self):
        i = 0
        while i < len(self.old):
            try:
                self.assertSequenceEqual(self.old[i].chanFlagDC, self.new[i].chanFlagDC)
                i += 1
            except Exception, ex:
                print 'chanFlagDC values mismatch, psNum=', i, 'ex=', ex
                break
        
        
    def assertSequenceEqual(self, a, b):
        if len(a) != len(b):
            print 'test will fail'
        else:
            i = 0
            while i < len(a):
                try:
                    self.assertEqual(a[i], b[i])
                except:
                    break
                i += 1

    def assert2DMatrixEqual(self, a, b):
        rows = len(a)
        if len(a) != len(b):
            print 'test will fail'
        else:
            i = 0
            while i < rows:
                try:
                    self.assertSequenceEqual(a[i], b[i])
                except:
                    break
                i += 1
    

if __name__ == '__main__':
    unittest.main()
