from scipy.optimize import fmin
from NeTeProbability import _calcNeTeProbability, _N_model
from numpy import log


def calcMostProbable(ps, specFlag ="tsc"):
    """Find the most likely temperature and density combination."""

    def __calcNeTeProbability(x, ps, specFlag):
        try:
            return_val = _calcNeTeProbability(x[0], x[1], ps, specFlag)
            # return_val = A * e^(-chi2)/2
            # --> chi2 + log(A), log(A) are normalization terms
            offset_chi2 = -1.0* log(-1.0*return_val)
            return offset_chi2
        except Exception, ex:
            print 'unknown error', ex

    x0 = (ps.ne0, ps.Te0)
    (xopt, fopt, iter, funcalls, warnflag) = fmin(__calcNeTeProbability, x0,
        args=(ps, specFlag, ), disp=0, full_output=1)

    predicted=_N_model(xopt[0],xopt[1],ps,'tsc')

    # identified most of 100 errors related to shape mismatch here
    # added these 4 lines + function at end as possible bug fix
    if len(predicted) != len(ps.scatPhotonsDC):
        ps.scatPhotonsDC = remove_zeros(ps.scatPhotonsDC, ps.chanFlagDC)
        ps.bgPhotons = remove_zeros(ps.bgPhotons, ps.chanFlagDC)
        ps.calib.APDfqeDC = remove_zeros(ps.calib.APDfqeDC, ps.chanFlagDC)

    # new error message defined here for diagnosis
    try: ps.chiRedMin=sum((predicted - ps.scatPhotonsDC)**2/((predicted + ps.bgPhotons) * ps.calib.APDfqeDC))/len(ps.scatPhotonsDC)
    except Exception, ex:
        ps.errNum = 900
        ps.errMsg = ex


    ps.chiRedMin=sum((predicted - ps.scatPhotonsDC)**2/((predicted + ps.bgPhotons) * ps.calib.APDfqeDC))/len(ps.scatPhotonsDC)
    ps.residual=(predicted - ps.scatPhotonsDC) #calculates a residual
    ps.weight = 1/((predicted + ps.bgPhotons) * ps.calib.APDfqeDC)
#    ps.weightSum = sum(ps.weight)
#    ps.normalizedResidual = ((sqrt((ps.weight*ps.weightSum)/(ps.weightSum-ps.weight)))*(predicted - ps.scatPhotonsDC)) #calculates a normalized residual
    if warnflag in (1, 2):
        ps.setError(800)

    ps.ne1 = xopt[0]
    ps.Te1 = xopt[1]

# function takes 2 1-D arrays of size n
# flag array is an array of 1's and 0's
# return shortened array with entries corresponding
# to 0's in flag array removed
from numpy import ndarray
def remove_zeros(array, flag_array):
    n = len(array)
    count = 0
    for i in xrange(0, n):
        if flag_array[i] != 0: count += 1
        else: pass

    new = ndarray([count])
    index = 0
    for i in xrange(0, n):
        if flag_array[i] != 0: new[index] = array[i]
        else: index -= 1
        index += 1

    return new