from scipy.optimize import fmin
from NeTeProbability import _calcNeTeProbability, _N_model


def calcMostProbable_neTe(ps, specFlag = "tsc"):
    """Find the most likely temperature and density combination."""

    def __calcNeTeProbability(x, ps, specFlag):
        try:
            print 'before calcProb'
            return_val = _calcNeTeProbability(x[0], x[1], ps, specFlag)
            print 'after calcProb'
            return return_val
        except Exception, ex:
            print 'unknown error', ex

    x0 = (ps.ne0, ps.Te0)
    (xopt, fopt, iter, funcalls, warnflag) = fmin(__calcNeTeProbability, x0,
        args=(ps, specFlag, ), disp=0, full_output=1)

    predicted=_N_model(xopt[0],xopt[1],ps,'tsc')
    ps.chiRedMin=sum((predicted - ps.scatPhotonsDC)**2/((predicted + ps.bgPhotons) * ps.calib.APDfqeDC))/len(ps.scatPhotonsDC)
    ps.residual=(predicted - ps.scatPhotonsDC) #calculates a residual
    ps.weight = 1/((predicted + ps.bgPhotons) * ps.calib.APDfqeDC)
#    ps.weightSum = sum(ps.weight)
#    ps.normalizedResidual = ((sqrt((ps.weight*ps.weightSum)/(ps.weightSum-ps.weight)))*(predicted - ps.scatPhotonsDC)) #calculates a normalized residual
    if warnflag in (1, 2):
        ps.setError(800)

    ps.ne1 = xopt[0]
    ps.Te1 = xopt[1]