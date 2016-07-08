# this will include various test methods

# 1. iterate_method
# applies specific method to every polychrom for every laser pulse
# exceptions change boolean indicator failed
# should cause break from both for loops
import time
def iterate_method(self, method='chanFlagDC'):
    start = time.time()
    num_poly = len(self.old)
    for n in xrange(0,num_poly):
        failed = 'false'
        try:
            num_seg = len(self.old[n])
        except:
            continue
        for m in xrange(0,num_seg):
            try:
                it_handler(self, method, n, m)
            except Exception, ex:
                print method, 'test failed, ex:', ex
                failed = 'true'
                break
        if failed == 'true': break
    finish = time.time()
    print 'time (s) for', method, 'test:'+'%.5s' % (finish-start)+' s'

# 2. assertSequenceEqual
# called by test object, more convenient to defined here
def assertSequenceEqual(self, a, b):
    rows = len(a)
    for i in xrange(0,rows): self.assertEqual(a[i], b[i])

# 3. assert2DMatrixEqual
# assumes data like a list of linked lists, matrix is subcase in python
def assert2DMatrixEqual(self, a, b):
    rows = len(a)
    for i in xrange(0,rows): assertSequenceEqual(self, a[i], b[i])

# 4. it_handler : iteration case handler
# where the ugliness in this module lies
# used a keyword matching algorithm to find possible values of interest
# this is a directory of attributes like ps.att from Data.py
# additional attributes may need to be added (calib attributes)
def it_handler(self, method, n, m):
    new = self.new[n][m]
    old = self.old[n][m]
    if method == 'errNum': self.assertEqual(old.errNum, new.errNum)
    if method == 'errMsg': self.assertSequenceEqual(old.errMsg, new.errMsg)
    if method == 'warnNum': self.assertSequenceEqual(old.warnNum, new.warnNum)
    if method == 'warnMsg': self.assertSequenceEqual(old.warnMsg, new.warnMsg)
    if method == 'chanFlagDC': self.assertSequenceEqual(old.chanFlagDC, new.chanFlagDC)
    if method == 'chanFlagAC': self.assertSequenceEqual(old.chanFlagAC, new.chanFlagAC)
    if method == 'satChans': self.assertSequenceEqual(old.satChans, new.satChans)
    if method == 'satChansDark': self.assertSequenceEqual(old.satChansDark, new.satChansDark)
    if method == 'noPulseFitChans':
        self.assertSequenceEqual(old.noPulseFitChans, new.noPulseFitChans)
    if method == 'str_offsetVolt':
        self.assert2DMatrixEqual(old.str_offsetVolt, new.str_offsetVolt)
    if method == 'offsetRaw': self.assertSequenceEqual(old.offsetRaw, new.offsetRaw)
    if method == 'str_ampOffset': self.assertSequenceEqual(old.str_ampOffset, new.str_ampOffset)
    if method == 'acq_offsetVolt':
        self.assert2DMatrixEqual(old.acq_offsetVolt, new.acq_offsetVolt)
    if method == 'offsetRaw':
        self.assertSequenceEqual(old.offsetRaw, new.offsetRaw)
    if method == 'acq_ampOffset': self.assertSequenceEqual(old.acq_ampOffset, new.acq_ampOffset)
    if method == 'str_voltData': self.assert2DMatrixEqual(old.str_voltData, new.str_voltData)
    if method == 'acq_voltData': self.assert2DMatrixEqual(old.acq_voltData, new.acq_voltData)
    if method == 't00_dc': self.assertEqual(old.t00_dc, new.t00_dc)
    if method == 't0_dc': self.assertEqual(old.t0_dc, new.t0_dc)
    if method == 't00_ac': self.assertEqual(old.t00_ac, new.t00_ac)
    if method == 't0_ac': self.assertEqual(old.t0_ac, new.t0_ac)
    if method == 'scatAng': self.assertEqual(old.scatAng, new.scatAng)
    if method == 't0DCBgCoeffs': self.assertSequenceEqual(old.t0DCBgCoeffs, new.t0DCBgCoeffs)
    if method == 't0ACBgCoeffs': self.assertSequenceEqual(old.t0ACBgCoeffs, new.t0ACBgCoeffs)
    if method == 'polyPulseCoeffs0':
        self.assert2DMatrixEqual(old.polyPulseCoeffs0, new.polyPulseCoeffs0)
    if method == 'polyPulseCoeffsDC':
        self.assert2DMatrixEqual(old.polyPulseCoeffsDC, new.polyPulseCoeffsDC)
    if method == 'polyPulseCoeffsAC':
        self.assert2DMatrixEqual(old.polyPulseCoeffsAC, new.polyPulseCoeffsAC)
    if method == 'cPulseStart': self.assertSequenceEqual(old.cPulseStart, new.cPulseStart)
    if method == 'cPulseEnd': self.assertSequenceEqual(old.cPulseEnd, new.cPulseEnd)
    if method == 'scatPhotonsDC': self.assertSequenceEqual(old.scatPhotonsDC, new.scatPhotonsDC)
    if method == 'scatPhotonsAC': self.assertSequenceEqual(old.scatPhotonsAC, new.scatPhotonsAC)
    if method == 'bgPhotons': self.assertSequenceEqual(old.bgPhotons, new.bgPhotons)
    if method == 'errPhotons': self.assertSequenceEqual(old.errPhotons, new.errPhotons)
    if method == 'residual': self.assertSequenceEqual(old.residual, new.residual)
    if method == 'weight': self.assertSequenceEqual(old.weight, new.weight)
    if method == 'weightSum': self.assertSequenceEqual(old.weightSum, new.weightSum)
    if method == 'normalizedResidual':
        self.assertSequenceEqual(old.normalizedResidual, new.normalizedResidual)
    if method == 'chiRedMin': self.assertSequenceEqual(old.chiRedMin, new.chiRedMin)
    if method == 'scPhotons_Bayes':
        self.assertSequenceEqual(old.scPhotons_Bayes, new.scPhotons_Bayes)
    if method == 'bgPhotons_Bayes':
        self.assertSequenceEqual(old.bgPhotons_Bayes, new.bgPhotons_Bayes)
    if method == 'fqe_Bayes': self.assertSequenceEqual(old.fqe_Bayes, new.fqe_Bayes)
    if method == 'trans_Bayes': self.assert2DMatrixEqual(old.trans_Bayes, new.trans_Bayes)
    if method == 'lam': self.assertSequenceEqual(old.lam, new.lam)
    if method == 'STRUCK_MIN': self.assertEqual(old.STRUCK_MIN, new.STRUCK_MIN)
    if method == 'STRUCK_MAX': self.assertEqual(old.STRUCK_MAX, new.STRUCK_MAX)
    if method == 'Te_MIN': self.assertSequenceEqual(old.Te_MIN, new.Te_MIN)
    if method == 'Te_MAX': self.assertSequenceEqual(old.Te_MAX, new.Te_MAX)
    if method == 'NE_STEPS': self.assertSequenceEqual(old.NE_STEPS, new.NE_STEPS)
    if method == 'TE_STEPS': self.assertSequenceEqual(old.TE_STEPS, new.TE_STEPS)
    if method == '_modelCache': self.assert2DMatrixEqual(old._modelCache, new._modelCache)
    if method == 'Te0': self.assertEqual(old.Te0, new.Te0)
    if method == 'ne0': self.assertEqual(old.ne0, new.ne0)
    if method == 'Te1': self.assertSequenceEqual(old.Te1, new.Te1)
    if method == 'ne1': self.assertSequenceEqual(old.ne1, new.ne1)
    if method == 'TeArray': self.assertSequenceEqual(old.TeArray, new.TeArray)
    if method == 'neArray': self.assertSequenceEqual(old.neArray, new.neArray)
    if method == 'probGrid': self.assertSequenceEqual(old.probGrid, new.probGrid)
    if method == 'TeProb': self.assertSequenceEqual(old.TeProb, new.TeProb)
    if method == 'neProb': self.assertSequenceEqual(old.neProb, new.neProb)
    if method == 'Te': self.assertEqual(old.Te, new.Te)
    if method == 'TeErrMin': self.assertSequenceEqual(old.TeErrMin, new.TeErrMin)
    if method == 'TeErrMax': self.assertSequenceEqual(old.TeErrMax, new.TeErrMax)
    if method == 'ne': self.assertEqual(old.ne, new.ne)
    if method == 'neErrMin': self.assertSequenceEqual(old.neErrMin, new.neErrMin)
    if method == 'neErrMax': self.assertSequenceEqual(old.neErrMax, new.neErrMax)
    if method == 'calib.lam': self.assertSequenceEqual(old.calib.lam, new.calib.lam)
    if method == 'calib.trans': self.assert2DMatrixEqual(old.calib.trans, new.calib.trans)
    if method == 'calib.charPulseAC':
        self.assert2DMatrixEqual(old.calib.charPulseAC, new.calib.charPulseAC)
    if method == 'calib.charPulseDC':
        self.assert2DMatrixEqual(old.calib.charPulseDC, new.calib.charPulseDC)
