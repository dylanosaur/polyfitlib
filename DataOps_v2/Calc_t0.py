from numpy import arange, sum, where, floor, zeros
from numpy import zeros_like, min
from scipy import polyfit, polyval

def calc_t0(ps):
    """Calculate the time of the pulse within the segment for both DC
    and AC data.

    Parameters:
    ps -- A PolySegData object.

    No return. The data is stored in ps.t0_dc and ps.t0_ac.
    """

    # DO THE DC T0 FIT FIRST
    # Get the data/characteristic pulse for finding t0.
    (yDataDC, cPulseDC) = _getDCDataAndCharPulse(ps)

    # Find indices of the minimum values of the composite pulse and data
    # arrays. We use the alignment of these as a starting point for finding
    # t0.
    minCPulseIdxDC = where(cPulseDC == min(cPulseDC))[0][0]
    minYDataIdxDC = where(yDataDC == min(yDataDC))[0][0]

    # Initial guess.
    ps.t00_dc = minYDataIdxDC - minCPulseIdxDC

    # Calculate the beginning and ending indices for searching, making sure
    # that we don't fall off the end. Currently search the neighborhood +/-10.
    idxBeginDC = ps.t00_dc - 10
    idxEndDC = ps.t00_dc + 10

    #if ps.t00_dc < 75:
    #    ps.t00_dc = 85
    #    idxBeginDC = ps.t00_dc - 10
    #    idxEndDC = ps.t00_dc + 10

    # Error catching in the initial guess and bounds
    if ps.t00_dc <= 0:
        idxBeginDC = 0
        idxEndDC = yDataDC.shape[0] - cPulseDC.shape[0]
    if idxBeginDC < 0:
	idxBeginDC = 0
    if idxEndDC > yDataDC.shape[0] - cPulseDC.shape[0]:
	idxEndDC = yDataDC.shape[0] - cPulseDC.shape[0]
    if idxBeginDC >= idxEndDC:
        idxBeginDC = 0
        idxEndDC = yDataDC.shape[0] - cPulseDC.shape[0]

    # We search using a least-squares approach to find the index
    # with the smallest error
    axisDC = arange(idxBeginDC,idxEndDC+1)
    errorDC = zeros(len(axisDC))
    for i in range(len(axisDC)):
        errorDC[i] = sum((cPulseDC - yDataDC[axisDC[i] : axisDC[i] + cPulseDC.shape[0]])**2)

    try:
        ps.t0_dc = where(errorDC == min(errorDC))[0][0] + idxBeginDC
    except:
        ps.setError(500)
    """
    # NEXT DO THE AC T0 FIT
    # Get the data/characteristic pulse for finding t0.
    (yDataAC, cPulseAC) = _getACDataAndCharPulse(ps)

    # Find indices of the minimum values of the composite pulse and data
    # arrays. We use the alignment of these as a starting point for finding
    # t0.
    minCPulseIdxAC = where(cPulseAC == min(cPulseAC))[0][0]
    minYDataIdxAC = where(yDataAC == min(yDataAC))[0][0]

    # Initial guess.
    ps.t00_ac = minYDataIdxAC - minCPulseIdxAC

    # Calculate the beginning and ending indices for searching, making sure
    # that we don't fall off the end. Currently search the neighborhood +/-50.
    idxBeginAC = ps.t00_ac - 50
    idxEndAC = ps.t00_ac + 50

    # Error catching in the initial guess and bounds
    if ps.t00_ac <= 0:
        idxBeginAC = 0
        idxEndAC = yDataAC.shape[0] - cPulseAC.shape[0]
    if idxBeginAC < 0:
	idxBeginAC = 0
    if idxEndAC > yDataAC.shape[0] - cPulseAC.shape[0]:
	idxEndAC = yDataAC.shape[0] - cPulseAC.shape[0]
    if idxBeginAC >= idxEndAC:
        idxBeginAC = 0
        idxEndAC = yDataAC.shape[0] - cPulseAC.shape[0]

    # We search using a least-squares approach to find the index
    # with the smallest error
    axisAC = arange(idxBeginAC,idxEndAC+1)
    errorAC = zeros(len(axisAC))
    for i in range(len(axisAC)):
        errorAC[i] = sum((cPulseAC - yDataAC[axisAC[i] : axisAC[i] + cPulseAC.shape[0]])**2)

    try:
        ps.t0_ac = where(errorAC == min(errorAC))[0][0] + idxBeginAC
    except:
	ps.setWarning(16)
    """

def _getDCDataAndCharPulse(ps):
    """Create a data array and characteristic pulse array by summing the DC data
    and characteristic pulse for each APD. Background fluctuations are removed
    from the data by fitting using a 5th order polynomial. The two arrays are
    then scaled so they are approximately the same size. This is all done in
    order to facilitate finding the t0 point.

    Parameters:
    ps -- A PolySegData object.

    Returns: A tuple (dataArray, charPulseArray)
    """
    # First we sum the data from the APDs to make the pulse easier to find.
    yData = zeros_like(ps.str_voltData[0])

    for data in ps.str_voltData:
        yData += data

    # Fit the averaged data with a polynomial to (hopefully) fit the
    # background. Currently using a 5th degree polynomial.
    xData = arange(ps.str_voltData.shape[1])
    ps.t0DCBgCoeffs = polyfit(xData, yData, 5) # The coefficients
    yFit = polyval(ps.t0DCBgCoeffs, xData) # The polynomial as an array

    yData -= yFit

    # Create a composite characteristic pulse by summing.
    cPulse = zeros_like(ps.calib.charPulseDC[0])
    for data in ps.calib.charPulseDC:
        cPulse += data


    # Normalize yData to the size of cPulse.
    # I don't know if this is really necessary.
    yData *= min(cPulse) / min(yData)

    return (yData, cPulse)

def _getACDataAndCharPulse(ps):
    """Create a data array and characteristic pulse array by summing the AC data
    and characteristic pulse for each APD. Background fluctuations are removed
    from the data by fitting using a 2nd order polynomial. The two arrays are
    then scaled so they are approximately the same size. This is all done in
    order to facilitate finding the t0 point.

    Parameters:
    ps -- A PolySegData object.

    Returns: A tuple (dataArray, charPulseArray)
    """
    # First we sum the data from the APDs to make the pulse easier to find.
    yData = zeros_like(ps.acq_voltData[0])
    for data in ps.acq_voltData:
        yData += data

    # Fit the averaged data with a polynomial to (hopefully) fit the
    # background. Currently using a 2nd degree polynomial.
    xData = arange(ps.acq_voltData.shape[1])
    ps.t0ACBgCoeffs = polyfit(xData, yData, 2) # The coefficients
    yFit = polyval(ps.t0ACBgCoeffs, xData) # The polynomial as an array

    yData -= yFit

    # Create a composite characteristic pulse by summing.
    cPulse = zeros_like(ps.calib.charPulseAC[0])
    for data in ps.calib.charPulseAC:
        cPulse += data

    # Normalize yData to the size of cPulse.
    # I don't know if this is really necessary.
    yData *= min(cPulse) / min(yData)

    return (yData, cPulse)
