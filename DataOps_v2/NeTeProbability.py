from numpy import trapz
import ts_c
import spectral_weave


def _N_model(ne, Te, ps, specFlag = "tsc"):
    """For a given temperature and density, return the number of expected
    photons for each APD in the poly.

    Parameters:
    ne -- The density.
    Te -- The temperature.
    ps -- The polySegData object.

    Returns: The expected number of photons for each APD in the poly
    (an array).
    updated 2014/03/27 by LAM
    """
    # NOTE: According to IDL code (and Hillary), this Selden equation
    # takes pi minus the angle as the scattering angle.
    # I've rewritten the calibration file with the corrected scattering angles.
    #    -jdl
    f = []
    cache_address = (ps.scatAng, Te,) # a list of tuple objects
    flag_len = len(ps.chanFlagDC)

    for i in xrange(0, flag_len):
        f.append(ps.chanFlagDC[i])
        cache_address = cache_address + (ps.chanFlagDC[i],)

    try:
        return ne * ps._modelCache[cache_address]
    except:
        ang = ps.scatAng
        if specFlag == "selden":
            dist = spectral_weave.selden_Spec(ps, Te)
        elif specFlag == "cold2o":
            dist = spectral_weave.cold2o_Spec(ps, Te)
        elif specFlag == "old":
            dist = spectral_weave.selden_old(ps, Te)
        elif specFlag == "tsc":
            dist = ts_c.selden(ps.calib.lam, 1.0, Te, ang)

        ps._modelCache[cache_address] = trapz(ps.trans_Bayes*dist,ps.calib.lam)
        # updated to use lam array for non-uniform spacing

        return ne * ps._modelCache[cache_address]

from numpy import log
def _calcNeTeProbability(ne, Te, ps, specFlag = "tsc"):
    """Calculate the probability of getting the number of measured photons
    given the temperature and density.

    Parameters:
    ne -- The density.
    Te -- The temperature.
    ps -- The polySegData object.

    Returns: The negative probability value. We return a negative value so
    we can utilize minimization routines.
    """

    N_model = _N_model(ne, Te, ps, specFlag)

    if specFlag == "tsc":
        val = ts_c.calcNeTeProbability(N_model, ps.scatPhotonsDC,
                                    ps.bgPhotons, ps.calib.APDfqeDC)
        # instead return constant + chi2 value
        # constant is some normalization constant from probability calculation
        return val
    else:
        return spectral_weave.calcModelProbability(ps, N_model)
