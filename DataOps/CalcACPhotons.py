# there may exist numpy dependencies not included here
from numpy import *

def calcACPhotons(ps):
    """Function fits the raw AC data of each APD with a polynomial and scaled
    characteristic pulse.

    Parameters:
    ps -- A PolySegData object.

    No return. The data is stored in ps.scatPhotonsAC
    """

    # The coefficients of the fit are saved in the PolySegData object so they
    # can be analyzed later.
    ps.scatPhotonsAC = ndarray(shape=[ps.str_voltData.shape[0]])
    ps.polyPulseCoeffsAC = ndarray(shape=[ps.str_voltData.shape[0], 3])

    polyPulseCoeffs0 = ndarray(shape=[ps.str_voltData.shape[0], 3])

    # find the AC neg-pos crossing point of the charPulse
    cp_max = where(ps.calib.charPulseAC[0] == max(ps.calib.charPulseAC[0]))
    cp_min = where(ps.calib.charPulseAC[0] == min(ps.calib.charPulseAC[0]))
    cp_cross = 0
    compare = abs(ps.calib.charPulseAC[0,cp_min[0][0]])
    for i in range(cp_min[0][0],cp_max[0][0]):
        if abs(ps.calib.charPulseAC[0,i]) < compare:
	    cp_cross = i
	    compare = abs(ps.calib.charPulseAC[0,i])

    for i in xrange(len(ps.acq_voltData)):
        charPulse = -1.0 * ps.calib.charPulseAC[i] / sum(ps.calib.charPulseAC[i, :cp_cross])
        APDgainAC = abs(ps.calib.APDgainAC[i])
	APDfqeAC = ps.calib.APDfqeAC[i]
	t0 = ps.t0_ac
	voltData = ps.acq_voltData[i][t0 : t0 + charPulse.shape[0]]
	rawData = ps.acq_rawData[i][t0 : t0 + charPulse.shape[0]]

        # Raise a warning if there is saturation in the raw data around the
        # characteristic pulse.
        if any(rawData == ACQIRIS_MIN) or any(rawData == ACQIRIS_MAX):
	    ps.setWarning(4)
	    ps.satChans.append(i + ps.calib.skipAPD)

	A = average(voltData[:32])
	B = 0
	D = 0

	polyPulseCoeffs0[i] = array((A, B, D))
	x0 = polyPulseCoeffs0[i].copy()

	def errorFn((A, B, D)):
	    return _polyPulseFitFn((A, B, 0, D), charPulse) - voltData

	(coeffs, cov_x, info, mesg, ier) = leastsq(errorFn, x0, full_output=1)

	if ier not in (1,2,3,4):
	    print "error in leastsq"
	    break

	ps.polyPulseCoeffsAC[i] = coeffs

	if ps.polyPulseCoeffsAC[i][-1] < 0:
	    ps.polyPulseCoeffsAC[i][-1] = 0

	ps.scatPhotonsAC[i] = ps.acq_deltat[i] * ps.polyPulseCoeffsAC[i][-1] / APDgainAC