import unittest
import polyfitlib_tests as pfl
import polyfitlib as opfl
import time


class NumPhotonsTests(unittest.TestCase):

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
    def check_satChans_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for satChans test'
            a = self.old[n][m].satChans
            b = self.new[n][m].satChans
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for satChans test'
    def check_noPulseFitChans_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for noPulseFitChans test'
            a = self.old[n][m].noPulseFitChans
            b = self.new[n][m].noPulseFitChans
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for noPulseFitChans test'

    def check_polyPulseCoeffs0_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for polyPulseCoeffs0 test'
            a = self.old[n][m].polyPulseCoeffs0
            b = self.new[n][m].polyPulseCoeffs0
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for polyPulseCoeffs0 test'
    def check_polyPulseCoeffsDC_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for polyPulseCoeffsDC test'
            a = self.old[n][m].polyPulseCoeffsDC
            b = self.new[n][m].polyPulseCoeffsDC
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for polyPulseCoeffsDC test'

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
    def check_errPhotons_values(self, n, m):
        if n ==1 and m ==0:
            print 'sequence assert starting for errPhotons test'
            a = self.old[n][m].errPhotons
            b = self.new[n][m].errPhotons
            self.assertSequenceEqual(a, b)
        if n == len(self.old)-1 and m == len(self.old[n])-1:
            print 'sequence assert complete for errPhotons test'

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

def it_handler(test_obj, method, n, m):
    self = test_obj

    # IT handler code
    if method == 'errNum':
        try: self.check_errNum_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex
    if method == 'chanFlagDC':
        try: self.check_chanFlagDC_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex
    if method == 'satChans':
        try: self.check_satChans_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex
    if method == 'noPulseFitChans':
        try: self.check_noPulseFitChans_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex
    if method == 'polyPulseCoeffs0':
        try: self.check_polyPulseCoeffs0_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex
    if method == 'polyPulseCoeffsDC':
        try: self.check_polyPulseCoeffsDC_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex
    if method == 'scatPhotonsDC':
        try: self.check_scatPhotonsDC_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex
    if method == 'scatPhotonsAC':
        try: self.check_scatPhotonsAC_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex
    if method == 'bgPhotons':
        try: self.check_bgPhotons_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex
    if method == 'errPhotons':
        try: self.check_errPhotons_values(n, m)
        except Exception, ex:
            print method, 'test failed ex=', ex