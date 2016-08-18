from __future__ import with_statement

# Grid search parameters - rough search
Te_MIN = 10.0
Te_MAX = 3498.0
NE_STEPS = 51
TE_STEPS = 101
#ne_MIN = 0.01
#ne_MAX = 1.0

# Saturation levels
ACQIRIS_MIN = -128
ACQIRIS_MAX = 127
STRUCK_MIN = 0
STRUCK_MAX = 65535

# Laser wavelength
LASER_LAM = 1064.3

# Logbook quality
LOGBOOK_TRUE = 1
LOGBOOK_UNSURE = -1

#MPTS_LASERON = '\\mraw_ops::btdot_128_180'
#DIM_MPTS_LASERON = 'dim_of(\\mraw_ops::btdot_128_180)*1000.0'


# The chunk-size is the approximate number of poly-segments each processor
# should fit at one time. This affects the efficiency of the multiprocessing
# code. You would like to maximize the concurrent use of processors while 
# minimizing the overhead of fetching new jobs. After some testing, it looks
# like any small number (1 - 16) is fine. Even 1. This might change for larger 
# numbers of jobs, or for faster processors / more processors. 
MULTIPROC_CHUNK_SIZE = 8

from numpy import mean, where, max, array, roll, absolute, arange,linspace, concatenate, diff, amin, logical_and, median
from util import getMdsServer

try:
    from pmds import mdsconnect, mdsopen, mdsvalue, mdsclose, mdsdisconnect
    from pmds import mdsput
except:
    print "MDSPlus module missing: some functionality will be unavailable."


import warnings
warnings.simplefilter("ignore")



def getLaserFireTimes(shotNum, burstLen = 0):
    """Find the times at which the laser fired based on the laser diode for the
    given shot number.

    Parameters:
    shotNum -- The MDSPlus shot number.

    Return: A list of times that a laser fired. If no firings are detected,
    return an empty list. Also return an emtpy list if an exception occurs.
    """
    """
    #HACK!:
    print "\n\n *******************\n WARNING: USING PRESET FIRE TIMES.  NOT CHECKING LASER DIODE! \n *********************\n\n"
    npulses=15  #typically 30
    start=28.0 # start time in ms
    step=0.5 #0.5 ms for 2kHz, 1.0ms for 1 kHz
    indices=arange(npulses)
    times=step*indices+start
    return (times,0)
    """
    # Connect to MDSPlus system.
    mdsconnect(getMdsServer(shotNum))
    mdsopen('mst', shotNum)

    
    #figure out where the laser fire diode was digitized (we kept blowing up digitizer channels...)
    if shotNum>1130719000:
        addr='\\mraw_ops::top.camac.euv_dense:tr1612_dense:input_10'
    elif shotNum>1130624000:
        #HACK!!! Laser fire diode was dead for awhile 
        temp = linspace(8.014,22.0159,15) 
        prelasing=False
        return (temp,prelasing)
    elif shotNum > 1121001016:
        addr='\\mraw_ops::top.camac.euv_dense:tr1612_dense:input_09'   
    elif shotNum > 1110408001:
        addr='\\mraw_ops::top.camac.euv_dense:tr1612_dense:input_08'
    #elif shotNum > 1140718000 and shotNum<1140719000:#HACK, laser fire diode wasn't being triggered
    #    times=linspace(5.0,34.0,30)
    #    prelase=False
    #    return(times,prelase)
    else:
        addr='\\mpts_laser_on'

    # Read the data from the laser diode and subtract the dc offset.
    try:
        laserOn = mdsvalue(addr)
        laserTime = mdsvalue('dim_of('+addr+')*1000.0') 
    except:
        print("laser diode address:",addr)
        raise
    laserOn = laserOn - mean(laserOn[0:200])
    laserMax = max(laserOn) # Get the maximum value in mpts_laser_on
    threshold=0.5

    #For part of a day, the clock to the laser diode digitizer was set to 500 kHz
    #instead of 3 MHz, this will store the correct fire times to the tree
    if (shotNum > 1140725000) and (shotNum < 1140725085):
        laserTime = (laserTime + 1) * 6 - 1    

    
    # If the maximum reading is low, we probably just have noise.
    if laserMax < threshold: raise Exception('Maximum reading (%.2f) below threshold %.2f.'%(laserMax,threshold))
    
    # Get laser derivative. 
    dLaser = laserOn[1:] - laserOn[:-1]
    # Find points where the derivative is above threshold (ie, rising edge).
    # Different threshold used for FastThomson if burstLen set
    if burstLen == 0:
        ind = where(dLaser > 0.5)[0]
    else:
        ind = where(dLaser > 0.1)[0]

    # Find those indices that are not sequential with more than 2
    # samples between them.  
    ind = ind[where(absolute(ind - roll(ind,1)) > 2)]

    #filter out spurious noise spikes.  Morton 10/2/2012
    # Uncommented 16-Sep-2013 due to noise pickup at end of PPCD (Parke)
    # Ignored for fast Thomson
    if burstLen == 0:
        ind2=[]
        for i in ind:
            if mean(laserOn[i:i+25])>0.05:
                ind2.append(i)
        ind=array(ind2)
    else:
        ind2=[]
        for i in ind:
            if mean(laserOn[i:(i+5)])>0.05:
                ind2.append(i)
        ind=array(ind2)

    # Crude burst filter for fast thomson
    # Modified so laser diode only used to find start of burst, due to 
    # laser diode missing some pulses
    ind2=array([],dtype='int64')
    burstInd = []
    lastTime = 0
    if burstLen > 0:
        for i in ind:
            if laserTime[i] < lastTime + 0.002: #Reject double pulse/spikes faster than FT's 250kHz
                continue
            if len(burstInd) > 0 and laserTime[i] > lastTime + 0.7:
                if len(burstInd) > 2:
                    dbi = diff(array(burstInd))
                    dbi = dbi[logical_and(dbi < 1.5*median(dbi), dbi > 0.5 * median(dbi))]    #Trying to catch large gaps where a pulse is missed
                    ftdt = int(round(mean(dbi)))
                    ind2 = concatenate((ind2, arange(burstInd[0], burstInd[0]+ftdt*burstLen, ftdt)))
                    burstInd = []
                else:   # Not enough info to get pulsing rate, or a noise spike was caught
                    burstInd = []
            if len(burstInd) < burstLen:  #ignoring extra pulses because spacing may be irregular
                lastTime = laserTime[i]
                burstInd.append(i)
        if len(burstInd) > 1:
            dbi = diff(array(burstInd))
            dbi = dbi[logical_and(dbi < 1.5*median(dbi), dbi > 0.5 * median(dbi))]    #Trying to catch large gaps where a pulse is missed
            ftdt = int(round(mean(dbi)))
            ind2 = concatenate((ind2, arange(burstInd[0], burstInd[0]+ftdt*burstLen, ftdt)))
        ind = ind2

    prelasing=False
    for i in ind:
        if any(dLaser[(i-60):(i-5)]>0.075):
           prelasing = True   
 
    # Disconnect from MDSPlus.
    mdsclose('mst', shotNum)
    mdsdisconnect()
    
    return (laserTime[ind],prelasing)
    


from Data import Data
import util
import itertools
def fitShot(shotNum, specFlag = "tsc", numProcs = None, burstLen = 0):
    """This function fits an entire shot. This version will use up to the 
    number of detected processors on the machine if the multiprocessing 
    module is installed. The multiprocessing module is a standard part of 
    python 2.6, and has been backported to 2.5:
    
    http://code.google.com/p/python-multiprocessing/
    
    Parameters:
    shotNum  -- The shot number to fit. For example 1070814040.
    numProcs -- The number of processes to create. Defaults to the number 
                of CPUs in the machine.
    burstLen -- For culling of extra Fast Thomson laser diode pulses
                Default of 0 acts like old system, keeping all pulses
                Any other value n will cause laser diode to skip pulses
                ~200 us after n pulses before looking for next burst
    """
    data = Data()
    try:
        data.loadData(shotNum)
    except Exception, ex:
        print "Failed to fit shot:", ex
        return None

    # Get laser fire times from the laser diode. 
    # We will check that the number of laser fire times matches the number
    # of data segments before we save the data.
    try:
        print 'Obtaining Laser Fire Times'
        (data.laserFireTimes,data.prelasing) = getLaserFireTimes(shotNum, burstLen)
    except Exception, ex:
        print "Failed to get laser fire times:", ex
        return None
    #data.laserFireTimes = array(range(30))*0.5 + 22
        
    print "Fitting shot %s. %s segments." % (shotNum, len(data.getSegments()))
    
    # Create a list of all poly-segments.
    psList = []
    for segment in data.getSegments():
        for poly in data.getPolyList():
            psList.append(data.getPolySegData(poly, segment))

    try: 
        # The Pool class creates a pool of workers, one for each processor
        # detected. The map function applies the given function to each 
        # element of the given list. The final parameter is the chunk size,
        # which is the approximate size of the chunks sent to each worker.
        # Increasing the chunk size may yield faster results on largers sets.
        from multiprocessing import Pool, cpu_count
        if numProcs is None:
            numProcs = cpu_count()
        pool = Pool(numProcs)
        #for ps in pool.map(fitPolySeg, psList, MULTIPROC_CHUNK_SIZE):
        #    data.setPolySegData(ps.poly, ps.segment, ps)
        for ps in pool.map(fitPSstar, itertools.izip(psList, itertools.repeat(specFlag)), MULTIPROC_CHUNK_SIZE):
            data.setPolySegData(ps.poly, ps.segment, ps)

    except:
        print "Multiprocessing module missing: using only one processor."
        map(fitPolySeg, psList)

    #print "Saving data to MDSplus."
    #try:
    #    saveToMDSplus(data)
    #except Exception, ex:
    #    print "MDSplus save failed: %s" % ex

    #print "Writing output file."
    #try:
    #    writeOutputFile(data)
    #except Exception, ex:
    #    print "Failed to write output: %s" % ex

    return data
    
    
def fitPSstar(tup_in):
    # takes a tuple input (ps, specFlag) and passes
    # the elements to fitPolySeg
    return fitPolySeg(*tup_in)

def fitWithWarnings(ps):
    """Fit a single poly and segment.

    Parameters:
    polySegData -- A PolySegData object.

    Returns: The polySegData object
    """
    if 1:
        calcAmpOffset(ps)
        calcVoltageFromRawData(ps)
        calc_t0(ps)
        calcTransMask(ps)
        calcNumPhotons(ps)
        filterChans(ps)
	    #calcACPhotons(ps)
        calcScatteringAngle(ps)
        calcLambdaArray(ps)
        calcTeNeInitVals(ps, 10.0, 'tsc')
        calcMostProbable_neTe(ps, 'tsc')
        calcNeTeValuesWithErrors(ps, 'tsc')

    return ps

def fitPolySeg(ps, specFlag = "tsc"):
    """Fit a single poly and segment.

    Parameters:
    polySegData -- A PolySegData object.

    Returns: The polySegData object
    """

    try:
        calcAmpOffset(ps)
        calcVoltageFromRawData(ps)
        calc_t0(ps)
        calcTransMask(ps)
        calcNumPhotons(ps)
        filterChans(ps)
	    #calcACPhotons(ps)
        calcScatteringAngle(ps)
        calcLambdaArray(ps)
        calcTeNeInitVals(ps, 10.0, specFlag)
        calcMostProbable_neTe(ps, specFlag)
        calcNeTeValuesWithErrors(ps, specFlag)
    except Exception, ex:
        # If we haven't set an error number, it is an unknown error. 
        if ps.errNum == 0:
            try: ps.setError(100, str(ex))
            except: pass

        # Set warning: fatal error occured.
        ps.warnNum = ps.warnNum | 1

    #if ps.getErrWarnStr() != None:
        #print ps.getErrWarnStr()

    return ps

# the effect of calcTransMask has been shifted to the makeCDF routine,
# so the calibration file already contains a masked transmission function.
# calcTransMask can be removed from PolyFitLib to save time

from numpy import where
def calcTransMask(ps):
    """Using the original method of finding the expected number of photons: the
    transmission functions need to be masked to remove noise.
    
    Parameters: 
    ps -- A PolySegData object.

    No return. The data is stored in the ps.calib.trans variables.
    """
    for i in range(len(ps.calib.trans)):
        for j in range(10):
            ps.calib.trans[i][j] = 0
        
        mask = zeros_like(ps.calib.trans[i])
        idx = where(ps.calib.trans[i] > 0.5 * max(ps.calib.trans[i]))[0]
        mask[idx] = 1
        (ll, ul) = (min(idx), max(idx))
        while ll > 0 and ps.calib.trans[i][ll-1] > 0:
            ll -= 1
            mask[ll] = 1
        
        while ul < len(ps.calib.trans[i]) - 2 and ps.calib.trans[i][ul+1] > 0:
            ul += 1
            mask[ul] = 1
        ps.calib.trans[i] = ps.calib.trans[i] * mask



from numpy import ndarray, any, average
def calcAmpOffset(ps):
    """Calculates the AC and DC amplifier offsets from the PolySegData.acq_offsetRaw 
    and str_offsetRaw variables. That is a data segment taken with no light so we
    can measure the "dark voltage," or amplifier offsets.  Technically, the AC offset
    should not be needed, but there seems to be a DC offset on the AC channel.

    Parameters:
    ps -- A PolySegData object.
    
    No return. The offsets are stored in ps.str_ampOffset and ps.acq_ampOffset.
    """

    # Create unitialized arrays to store resuts.
    ps.str_ampOffset = ndarray(shape=ps.str_offsetRaw.shape[0])
    ps.str_offsetVolt = ndarray(shape=ps.str_offsetRaw.shape)

    ps.acq_ampOffset = ndarray(shape=ps.acq_offsetRaw.shape[0])
    ps.acq_offsetVolt = ndarray(shape=ps.acq_offsetRaw.shape)
    
    ps.satChansDark = []

    # Check for saturation in the offset data.
    for i in range(ps.str_offsetRaw.shape[0]):
        if any(ps.str_offsetRaw[i] == STRUCK_MIN) or any(ps.str_offsetRaw[i] == STRUCK_MAX):
	    ps.satChansDark.append(i + ps.calib.skipAPD)
	    ps.chanFlagDC[i] = 0

    #for i in range(ps.acq_offsetRaw.shape[0]):
    #    if any(ps.acq_offsetRaw[i] == ACQIRIS_MIN) or any(ps.acq_offsetRaw[i] == ACQIRIS_MAX):
    #    ps.satChansDark.append(i + ps.calib.skipAPD)
    #        ps.chanFlagAC[i] = 0

    if len(ps.satChansDark) > 0:
        ps.setWarning(8)

    # Calculate the amplifier offsets.
    for i in range(ps.str_offsetRaw.shape[0]):
        ps.str_offsetVolt[i] = (ps.str_offsetRaw[i] - ps.str_zeroBit[i]) * ps.str_voltsPerBit[i]
        ps.str_ampOffset[i] = average(ps.str_offsetVolt[i])
    #for i in range(ps.acq_offsetRaw.shape[0]):
    #    ps.acq_offsetVolt[i] = ps.acq_offsetRaw[i] * ps.acq_voltsPerBit[i] - ps.acq_offset[i]
    #    ps.acq_ampOffset[i] = average(ps.acq_offsetVolt[i])
    
    

from numpy import ndarray, any
def calcVoltageFromRawData(ps):
    """Calculate the AC and DC voltage data points from the raw data and calibrations.

    Parameters:
    ps -- A PolySegData object.

    No return. The data is stored in ps.str_voltData and ps.acq_voltData. 
    """
    # Create an unitialized array of floats (the default) of the same shape as
    # the raw data.
    ps.str_voltData = ndarray(shape=ps.str_rawData.shape)
    ps.acq_voltData = ndarray(shape=ps.acq_rawData.shape)

    # Check for saturation in the raw data.
    #if any(ps.str_rawData == STRUCK_MIN) or any(ps.str_rawData == STRUCK_MAX):
    #    ps.setWarning(4)

    # Fill the voltData arrays.
    for i in range(ps.str_rawData.shape[0]):
        ps.str_voltData[i] = (ps.str_rawData[i] - ps.str_zeroBit[i]) * ps.str_voltsPerBit[i] - ps.str_ampOffset[i]
    #for i in range(ps.acq_rawData.shape[0]):
    #    offset = ps.acq_ampOffset[i] + ps.acq_offset[i]
    #    ps.acq_voltData[i] = ps.acq_rawData[i] * ps.acq_voltsPerBit[i] - offset
        


from numpy import zeros_like, min
from scipy import polyfit, polyval
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



from numpy import arange, sum, where, floor
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



from numpy import where, min
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



from numpy import array, average, sum, max, min, ndarray, abs, sqrt, absolute
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



def filterChans(ps):
    """Utilizes the channel quality flags to determine which channels to use for the
    Bayesian probability analysis.

    Parameters:
    ps -- A PolySegData object.

    No return. The filtered channel information is stored in ps.
    """

    # Determine the number of good channels
    nchans = ps.str_voltData.shape[0]
    nchans_good = 0

    for i in range(nchans):
        if ps.chanFlagAC[i] == 1: nchans_good += 1
        elif ps.chanFlagDC[i] == 1: nchans_good += 1
        else: pass

    if nchans_good < nchans: ps.setWarning(64)
    if nchans_good < 2: ps.setError(650)

    # Create the final arrays to be passed to the Bayesian functions
    ps.scPhotons_Bayes = ndarray(shape=(nchans_good))
    ps.bgPhotons_Bayes = ndarray(shape=(nchans_good))
    ps.fqe_Bayes = ndarray(shape=(nchans_good))
    ps.trans_Bayes = ndarray(shape=(nchans_good, ps.calib.trans.shape[1]))

    index = 0
    for i in range(nchans):
        if ps.chanFlagAC[i] == 1:
            ps.scPhotons_Bayes[index] = ps.scatPhotonsAC[i]
            ps.fqe_Bayes[index] = ps.calib.APDfqeAC[i]
            ps.trans_Bayes[index, :] = ps.calib.trans[i,:]

            ps.bgPhotons_Bayes[index] = ps.bgPhotons[i]

            index += 1
        elif ps.chanFlagDC[i] == 1:
            ps.scPhotons_Bayes[index] = ps.scatPhotonsDC[i]
            ps.bgPhotons_Bayes[index] = ps.bgPhotons[i]
            ps.fqe_Bayes[index] = ps.calib.APDfqeDC[i]
            ps.trans_Bayes[index, :] = ps.calib.trans[i,:]

            index += 1
        else: pass



from numpy import pi, arctan
def calcScatteringAngle(ps):
    """Calculates the scattering angle for the given roa value of the poly."""
    a     = 0.5200 # The radius.
    alpha = 0.1733 # Height of detector above r = 0.
    beta  = 0.5163 # Perpendicular distance from laser to detector.
    r = ps.roa * a
    ps.scatAng = pi - arctan(beta / (alpha + r))



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



# Caching the model values for given angles and temperatures provides a
# substantial speedup at the expense of greater memory usage.
_modelCache = {}

import spectral_weave
import ts_c
from numpy import dot, pi,trapz
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
    try:
        return ne * _modelCache[(ps.scatAng, Te)]
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
        _modelCache[(ang, Te)] = trapz(ps.trans_Bayes*dist,ps.calib.lam) #updated to use lam array for non-uniform spacing
        return ne * _modelCache[(ang, Te)]

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
        return ts_c.calcNeTeProbability(N_model, ps.scatPhotonsDC, 
                                    ps.bgPhotons, ps.calib.APDfqeDC)
    else:
        return spectral_weave.calcModelProbability(ps, N_model)



from numpy import logspace, log10, exp, linspace
from pylab import amap, where
def calcTeNeInitVals(ps, gridPts = 10.0, specFlag = "tsc"):
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
        calcTeNeInitVals(ps, gridPts + 10.0)



from scipy.optimize import fmin
def calcMostProbable_neTe(ps, specFlag = "tsc"):
    """Find the most likely temperature and density combination."""
    
    def __calcNeTeProbability(x, ps, specFlag):
        return _calcNeTeProbability(x[0], x[1], ps, specFlag)

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



from numpy import e, linspace
def calcNeTeValuesWithErrors(ps, specFlag = "tsc"):
    """Calculates the temperature and density with error bars. This is 
    accomplished by creating a grid and calculating the probability for each
    point on the grid.
    """
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
    except Exception, ex:
        # An exception will be thrown if there are no points in the 
        # temperature or density probability distributions with values less
        # than min(prob) / e. (Recall the probability distribution is 
        # negative.)
        ps.setError(900)



from numpy import zeros, transpose

from datetime import date
from util import getMdsServer
def saveToMDSplus(data):
    """The code in this function was adapted from the idl function with few
    if any changes to the TDI expressions. 
    """
    
    # The time basis of stored data is given by the laser diode.
    timePoints = data.laserFireTimes

    if len(data.laserFireTimes) != len(data.segments):
        raise Exception("Laser diode # of shots (%s) doesn't match data segments (%s)" % (
            len(data.laserFireTimes), len(data.segments)))
    
    # Construct roa array.
    polyList = data.getPolyListSortedROA()

    # Construct the temperature and density arrays.
    roaArray = zeros(shape=(len(polyList), len(timePoints)))
    qualArray = zeros(shape=(len(polyList), len(timePoints)), dtype=int)
    TeArray = zeros(shape=(len(polyList), len(timePoints)))
    neArray = zeros(shape=(len(polyList), len(timePoints)))
    TeErr   = zeros(shape=(len(polyList), len(timePoints)))
    neErr   = zeros(shape=(len(polyList), len(timePoints)))

    #ProbGrid = zeros(shape=(len(polyList), len(timePoints), TE_STEPS, NE_STEPS))

    for i in data.getSegments():
        for j,poly in enumerate(polyList):
            ps = data.getPolySegData(poly, i)
            roaArray[j][i] = ps.roa
            TeArray[j][i] = ps.Te
            neArray[j][i] = ps.ne
            TeErr[j][i] = (ps.TeErrMax - ps.TeErrMin)/2.0
            neErr[j][i] = (ps.neErrMax - ps.neErrMin)/2.0
            qualArray[j][i] = ps.warnNum

            #ProbGrid[j,i] = ps.probGrid

    # Connect to MDSplus system.
    mdsconnect(getMdsServer(data.shotNum))
    mdsopen('mst_tsmp', data.shotNum)

    # Put Bayesian temperature/density profiles.
    mdsput('\mst_tsmp::top.proc_tsmp.t_e_bayesian',
           'build_signal(build_with_error(build_with_units($,"eV"),$),*,build_with_units($,"s"),$)',
           (TeArray, TeErr, timePoints, roaArray))
    mdsput('\mst_tsmp::top.proc_tsmp.t_e',
           'build_signal(build_with_error(build_with_units($,"eV"),$),*,build_with_units($,"s"),$)',
           (TeArray, TeErr, timePoints, roaArray))

    mdsput('\mst_tsmp::top.proc_tsmp.n_e_bayesian',
           'build_signal(build_with_error(build_with_units($,"na"),$),*,build_with_units($,"s"),$)',
           (neArray, neErr, timePoints, roaArray))
    mdsput('\mst_tsmp::top.proc_tsmp.n_e',
           'build_signal(build_with_error(build_with_units($,"na"),$),*,build_with_units($,"s"),$)',
           (neArray, neErr, timePoints, roaArray))

    mdsput('\mst_tsmp::top.proc_tsmp.quality', 'build_signal($,*,$,$)',
           (qualArray, timePoints, roaArray))

    #mdsput('\mst_tsmp::top.proc_tsmp.teneprobgrid', 'build_signal($,*,*,*,$,$)',
    #       (ProbGrid, timePoints, roaArray))

    mdsput('\mst_tsmp::top.proc_tsmp.lastfitdate', '$', (date.today().isoformat(),))

    txt = 'Python fitting code. 1.0\nVersion: 1.0\n\n' + data.getReadme()
    mdsput('\mst_tsmp::top.proc_tsmp.readme', '$', (txt, ))

    mdsclose('mst_tsmp', data.shotNum)

    """
    # Update flags in the MST logbook
    mdsopen('mst_logbook', data.shotNum)
    # check that the quality array isn't just -1, and
    # identify the indices of good data
    if qualArray.size > 1:
	good = where(qualArray == 0)
	# check that there are temperatures, and
	# then determine the logbook flag value
	if TeArray.size > 1:
	    data_quality = len(good[0])/qualArray.size
	    if data_quality > 0.3:
		mdsput('\mst_logbook::top.discharge.diagnostics.ts','$', LOGBOOK_TRUE)
	    else:
		mdsput('\mst_logbook::top.discharge.diagnostics.ts','$', LOGBOOK_UNSURE)
    mdsclose('mst_logbook', data.shotNum)
    """

    mdsdisconnect()



def writeOutputFile(data):
    fn = util.getSaveFilePath(data.shotNum)
    with open(fn, 'w') as f:
        f.write(data.getReadme(False))

