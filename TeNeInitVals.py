from numpy import logspace, log10, exp, linspace

from NeTeProbability import _calcNeTeProbability
def NeTeInitVals(ps, gridPts = 10.0, specFlag ="tsc"):
    """Perform a simple grid search to find apropriate initial ne and Te
    values. These values are used as the starting point for finding the most
    probable density and temperature.

    Parameters:
    ps -- The polySegData object.

    Returns: Nothing. Initial density and temperature values are stored in the
    polySegData object.
    """

    if specFlag == "old" or specFlag == "tsc":
        ne_MIN = 1e-3
        ne_MAX = 1e1
    else:
        ne_MIN = 1000.0
        ne_MAX = 100000.0

    maxProb = 0
    ps.ne0 = -1
    ps.Te0 = -1

    Te_MIN = ps.Te_MIN
    Te_MAX = ps.Te_MAX

    for Te in logspace(log10(Te_MIN), log10(Te_MAX), gridPts):
        for ne in logspace(log10(ne_MIN), log10(ne_MAX), gridPts):
            prob = -_calcNeTeProbability(ne, Te, ps, specFlag)
            if prob > maxProb:
                maxProb = prob
                ps.ne0 = ne
                ps.Te0 = Te

    # If the grid search failed, we run it again with more grid points.
    # We may need to set an upper limit on the density of the grid.
    if ps.ne0 == -1 or ps.Te0 == -1:
        if gridPts > 100:
            ps.setError(700)

        print "Grid search failed with %s points, retrying." % gridPts
        NeTeInitVals(ps, gridPts + 10.0)