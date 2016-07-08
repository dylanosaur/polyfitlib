from numpy import arange
def calcLambdaArray(ps):
    """Calculates an array of lambda values. This serves as the abscissa axis
    for the transmission functions. Updated 2014/03/27 by LAM.
    """
    if ps.shotNum < 1140327000:
        lam0 = ps.calib.lam0
        lam1 = lam0 + ps.calib.deltaLam * ps.calib.trans[0].shape[0]
        ps.calib.lam = arange(lam0, lam1, ps.calib.deltaLam)
    else:
        pass #we've just imported the array straight from the calib.nc file

