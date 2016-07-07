import unittest
import polyfitlib_tests as pfl
import polyfitlib as opfl
import time


class FilterChansTests(unittest.TestCase):

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
                except Exception, ex:
                    print method, 'test failed ex=', ex
                    break
        finish = time.time()
        print 'time for test:', finish-start

# Build tests code
    def check_errNum_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for errNum test'
            a = self.old[n][m].errNum
            b = self.new[n][m].errNum
            self.assertEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for errNum test'
    def check_chanFlagDC_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for chanFlagDC test'
            a = self.old[n][m].chanFlagDC
            b = self.new[n][m].chanFlagDC
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for chanFlagDC test'
    def check_chanFlagAC_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for chanFlagAC test'
            a = self.old[n][m].chanFlagAC
            b = self.new[n][m].chanFlagAC
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for chanFlagAC test'
    def check_str_voltData_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for str_voltData test'
            a = self.old[n][m].str_voltData
            b = self.new[n][m].str_voltData
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for str_voltData test'
    def check_scatPhotonsDC_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for scatPhotonsDC test'
            a = self.old[n][m].scatPhotonsDC
            b = self.new[n][m].scatPhotonsDC
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for scatPhotonsDC test'
    def check_scatPhotonsAC_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for scatPhotonsAC test'
            a = self.old[n][m].scatPhotonsAC
            b = self.new[n][m].scatPhotonsAC
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for scatPhotonsAC test'
    def check_bgPhotons_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for bgPhotons test'
            a = self.old[n][m].bgPhotons
            b = self.new[n][m].bgPhotons
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for bgPhotons test'
    def check_scPhotons_Bayes_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for scPhotons_Bayes test'
            a = self.old[n][m].scPhotons_Bayes
            b = self.new[n][m].scPhotons_Bayes
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for scPhotons_Bayes test'
    def check_bgPhotons_Bayes_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for bgPhotons_Bayes test'
            a = self.old[n][m].bgPhotons_Bayes
            b = self.new[n][m].bgPhotons_Bayes
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for bgPhotons_Bayes test'
    def check_fqe_Bayes_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for fqe_Bayes test'
            a = self.old[n][m].fqe_Bayes
            b = self.new[n][m].fqe_Bayes
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for fqe_Bayes test'
    def check_trans_Bayes_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for trans_Bayes test'
            a = self.old[n][m].trans_Bayes
            b = self.new[n][m].trans_Bayes
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for trans_Bayes test'

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
        self.check_errNum_values(n, m)
    if method == 'chanFlagDC':
        self.check_chanFlagDC_values(n, m)
    if method == 'chanFlagAC':
        self.check_chanFlagAC_values(n, m)
    if method == 'str_voltData':
        self.check_str_voltData_values(n, m)
    if method == 'scatPhotonsDC':
        self.check_scatPhotonsDC_values(n, m)
    if method == 'scatPhotonsAC':
        self.check_scatPhotonsAC_values(n, m)
    if method == 'bgPhotons':
        self.check_bgPhotons_values(n, m)
    if method == 'scPhotons_Bayes':
        self.check_scPhotons_Bayes_values(n, m)
    if method == 'bgPhotons_Bayes':
        self.check_bgPhotons_Bayes_values(n, m)
    if method == 'fqe_Bayes':
        self.check_fqe_Bayes_values(n, m)
    if method == 'trans_Bayes':
        self.check_trans_Bayes_values(n, m)

    # IT handler code