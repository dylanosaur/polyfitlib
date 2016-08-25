from numpy import e, linspace, ndarray, where
from NeTeProbability import _calcNeTeProbability

def calcWithErrors(ps, specFlag ="tsc"):
    """Calculates the temperature and density with error bars. This is
    accomplished by creating a grid and calculating the probability for each
    point on the grid.
    """
    TE_STEPS = ps.TE_STEPS
    NE_STEPS = ps.NE_STEPS
    # Calculate the box to integrate on.
    TeSpread = ps.Te1 * 0.3
    neSpread = ps.ne1 * 0.3

    # Create arrays in temperature and density to define the grid.
    #ne_STEPS = 51
    #Te_STEPS = 101

    ps.TeArray = linspace(ps.Te1 - TeSpread, ps.Te1 + TeSpread, TE_STEPS)
    ps.neArray = linspace(ps.ne1 - neSpread, ps.ne1 + neSpread, NE_STEPS)

    # Create and populate the grid.
    ps.probGrid = ndarray(shape = (TE_STEPS, NE_STEPS))

    # This takes about 50% of the time of the entire program.
    # I'd like to speed it up if I could.
    for i, Te in enumerate(ps.TeArray):
        for j, ne in enumerate(ps.neArray):
            ps.probGrid[i][j] = _calcNeTeProbability(ne, Te, ps, specFlag = "tsc")


    # Calculate the probability curves for temperature and density.
    ps.TeProb = ps.probGrid.sum(axis=1)
    ps.neProb = ps.probGrid.sum(axis=0)

    # Calculate the temperature and density.
    neProbMin = ps.neProb.min()
    TeProbMin = ps.TeProb.min()

    neIdx = where(ps.neProb == neProbMin)[0][0]
    TeIdx = where(ps.TeProb == TeProbMin)[0][0]

    ps.ne = ps.neArray[neIdx]
    ps.Te = ps.TeArray[TeIdx]

    try:
        ps.neErrMin = ps.neArray[where(ps.neProb < neProbMin/e)[0][ 0]]
        ps.neErrMax = ps.neArray[where(ps.neProb < neProbMin/e)[0][-1]]

        ps.TeErrMin = ps.TeArray[where(ps.TeProb < TeProbMin/e)[0][ 0]]
        ps.TeErrMax = ps.TeArray[where(ps.TeProb < TeProbMin/e)[0][-1]]

        # TODO.
        # If there are error points are end points, then we should issue a
        # warning.

        # Version 1.3 code change 1/1 start
        if ps.neErrMin != ps.neArray[0] or ps.neErrMax != ps.neArray[-1]:
            ps.setWarning(256, 'ne uncertainties are too small')
        if ps.TeErrMin != ps.TeArray[0] or ps.neErrMax != ps.TeArray[-1]:
            ps.setWarning(256, 'Te uncertainties are too small')
        # Version 1.3 code change 1/1 end

    except Exception, ex:
        # An exception will be thrown if there are no points in the
        # temperature or density probability distributions with values less
        # than min(prob) / e. (Recall the probability distribution is
        # negative.)
        ps.setError(900)