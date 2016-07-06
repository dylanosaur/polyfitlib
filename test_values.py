import unittest
from load_new_and_prev_versions import loader


class MyValueTests(unittest.TestCase):

    def __init__(self):
        #do nothing
        return None
    
    def setUp(self):
        #This function performs PFL analysis on MDS+ database
        #Then calls readTStree to create objects with results
        try:
            shot_old, shot_new = loader()
            self.old = shot_old
            self.new = shot_new
            print 'shots loaded correctly'
        except Exception, ex:
            print 'error: shots not loaded correctly,', ex
        return None
    
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
