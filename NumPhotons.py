from numpy import array, average, sum, max, min
from numpy import ndarray, abs, sqrt, absolute, where
from scipy.optimize import leastsq

def calcNumPhotons(ps):
    """Function fits the raw data of each APD with a polynomial and scaled
    characteristic pulse.

    Parameters:
    ps -- A PolySegData object.

    No return. The data is stored in ps.scatPhotonsDC, ps.scatPhotonsAC,
    ps.bgPhotons, ps.errPhotons.
    """

    # The coefficients of the fit are saved in the PolySegData object so they
    # can be analyzed later.
    ps.polyPulseCoeffs0 = ndarray(shape=[ps.str_voltData.shape[0], 4])
    ps.polyPulseCoeffsDC = ndarray(shape=[ps.str_voltData.shape[0], 4])
    ps.scatPhotonsDC = ndarray(shape=[ps.str_voltData.shape[0]])
    #ps.scatPhotonsAC = ndarray(shape=[ps.str_voltData.shape[0]])
    ps.bgPhotons = ndarray(shape=[ps.str_voltData.shape[0]])
    ps.errPhotons = ndarray(shape=[ps.str_voltData.shape[0]])
    ps.cPulseStart = ndarray(shape=[ps.str_voltData.shape[0]])
    ps.cPulseEnd = ndarray(shape=[ps.str_voltData.shape[0]])

    ps.satChans = []
    ps.noPulseFitChans = []
    STRUCK_MIN = ps.STRUCK_MIN
    STRUCK_MAX = ps.STRUCK_MAX

    for i in xrange(len(ps.str_voltData)):
        # The characteristic pulse is normalized so it integrates to one. Then
        # integral under it can be found directly from its coefficient from the
        # fit.
        #   -jdl
        charPulse = 1.0 * ps.calib.charPulseDC[i] / sum(ps.calib.charPulseDC[i])
        APDgainDC = abs(ps.calib.APDgainDC[i])
        APDfqeDC = ps.calib.APDfqeDC[i]
        t0 = ps.t0_dc
        voltData = ps.str_voltData[i][t0 : t0 + charPulse.shape[0]]
        rawData = ps.str_rawData[i][t0 : t0 + charPulse.shape[0]]

        # Raise a warning if there is saturation in the raw data around the
        # characteristic pulse.
        if any(rawData == STRUCK_MIN) or any(rawData == STRUCK_MAX):
            ps.satChans.append(i + ps.calib.skipAPD)
            ps.chanFlagDC[i] = 0
            ps.polyPulseCoeffs0[i] = array((0, 0, 0, 0))
            ps.polyPulseCoeffsDC[i] = array((0, 0, 0, 0))
            ps.scatPhotonsDC[i] = 0
            ps.bgPhotons[i] = 0
            ps.errPhotons[i] = 0
            continue

        # See _polyPulseFitFn for the meaning of these coefficients.
        # The constant should be approximately the y intercept.
        A = average(voltData[:8])

        # No guess for linear or quadratic terms.
        B = C = 0

        # The pulse coefficient is set to zero because we were getting results
        # that were too large by using the data height.
        D = 0

        ps.polyPulseCoeffs0[i] = array((A, B, C, D))
        x0 = ps.polyPulseCoeffs0[i].copy()

        # Now get the best fit coefficients.
        def errorFn((A, B, C, D)):
            return _polyPulseFitFn((A, B, C, D), charPulse) - voltData

        (coeffs, cov_x, info, mesg, ier) = leastsq(errorFn, x0, full_output=1)

        # The current documentation for leastsq gives an incorrect account of
        # the ier variable. It turns out that 1,2,3, and 4 indicate success.
        if ier not in (1,2,3,4):
	    ps.noPulseFitChans.append(i + ps.calib.skipAPD)
	    ps.chanFlagDC[i] = 0
            ps.polyPulseCoeffsDC[i] = array((0, 0, 0, 0))
            ps.scatPhotonsDC[i] = 0
            ps.bgPhotons[i] = 0
            ps.errPhotons[i] = 0
            continue

        ps.polyPulseCoeffsDC[i] = coeffs

        # The scattered photons are proportional to the coefficient on the
        # characteristic pulse. Recall the pulse was scaled such that its
        # integral was equal to 1, so the integral of the scaled pulse is equal
        # to its coefficient ps.polyPulseCoeffsDC[i][3].
        ps.scatPhotonsDC[i] = - ps.str_deltat[i] * ps.polyPulseCoeffsDC[i][-1] / APDgainDC
        ps.scatPhotonsDC[where(ps.scatPhotonsDC<0)]=0#photon number forced to be positive
        # For the background photons, we need to integrate the polynomial part
        # of the fit over the pulse width. We determine the limits of
        # integration from the characteristic pulse.
        (ll, ul) = _calcCharPulseBeginAndEnd(charPulse, ps.poly)
        ps.cPulseStart[i] = ll
        ps.cPulseEnd[i] = ul

        coeffs = ps.polyPulseCoeffsDC[i].copy()
        coeffs[-1] = 0
        rawIntegral = sum(_polyPulseFitFn(coeffs, charPulse)[ll:ul])

        # Here is an explanation for the factor of 1.8 appearing in the
        # background photon calculation from Rob O'Connell:
        # "... Also, since the DC gain is higher than the AC gain by factor of
        # about 2, a given DC-voltage corresponds to fewer photons than same
        # AC voltage. ..."
        ps.bgPhotons[i] =  -1.0*ps.str_deltat[i] * rawIntegral / (1.8 * APDgainDC)

        if ps.bgPhotons[i] < 0:
            ps.setWarning(2, 'Background photons : %s' % ps.bgPhotons[i])
            ps.bgPhotons[i] = 0

        # Calculate the error in the number of photons.
        ps.errPhotons[i] = sqrt((ps.scatPhotonsDC[i] + ps.bgPhotons[i]) * APDfqeDC)

    if len(ps.satChans) > 0:
        ps.setWarning(4)
    if len(ps.noPulseFitChans) > 0:
        ps.setWarning(32)

from numpy import arange, square
def _polyPulseFitFn((A, B, C, D), charPulse):
    """Function used to fit the pulse data for an APD with characteristic pulse
    given by charPulse.

    Parameters:
    (A, B, C, D) -- The coefficients in the equation.
    charPulse    -- The characteristic pulse.

    Returns: An array of the same length as charPulse calculated using the
    formula A + B*x + C*x^2 + D*charPulse.
    """
    x = arange(charPulse.shape[0], dtype=float)
    return A + B*x + C*square(x) + D*charPulse

def _calcCharPulseBeginAndEnd(charPulse, polynum):
    """Find the sample numbers corresponding to the beginning and end of the
    characteristic pulse.

    Parameters:
    charPulse -- A characteristic pulse.
    polynum -- The poly number.

    Return a tuple: (begin_index, end_index).
    """
    # The beginning and end of the pulse are used to calculate the background.
    # In reality we are only finding the approximate beginning of the pulse,
    # and setting the end as 50 samples further along.
    # I don't know why this is the case.
    #   -jdl
    idxArray = where(charPulse < 0.05 * min(charPulse))

    # I don't know how much of the pulse actually needs to be integrated over for
    # the background - a strict conversion of deltat from Acq to Str would mean
    # only 5 samples instead of 50.  But the pulse clearly extends to at least 10
    # samples or so.

    # the pulse length depends on which generation of amplifier boards is used
    if polynum < 16:
        pulse_length = 10
    else:
        pulse_length = 6
    return (idxArray[0][0], idxArray[0][0] + pulse_length)