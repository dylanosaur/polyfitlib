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

# Create model cache
import UserDict
_modelCache = UserDict.UserDict()

LOOP_INDICATOR = 0

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
        ampOffset(ps)
        voltsFromData(ps)
        calc_t0(ps)
        transMask(ps)
        numPhotons(ps)
        filterChans(ps)
	    #calcACPhotons(ps)
        calcScatAngle(ps)
        lambdaArray(ps)
        NeTeInitVals(ps, 10.0, 'tsc')
        mostProbableNeTe(ps, 'tsc')
        calcNeTeWithErrors(ps, 'tsc')

    return ps



def fitPolySeg(ps, specFlag = "tsc"):
    """Fit a single poly and segment.

    Parameters:
    polySegData -- A PolySegData object.

    Returns: The polySegData object
    """

    # clear the cache frequently, or it's likely the cache will
    # become clogged for bigger data shots (>30 segments)
    _modelCache.data.clear()
    ps._modelCache = _modelCache

    try:
        ampOffset(ps)
        voltsFromData(ps)
        calc_t0(ps)
        transMask(ps)
        numPhotons(ps)
        filterChans(ps)
	    #calcACPhotons(ps) #removed from analysis: PRE 06/01/16
        calcScatAngle(ps)
        lambdaArray(ps)
        NeTeInitVals(ps, 10.0, specFlag)
        mostProbableNeTe(ps, specFlag)
        calcNeTeWithErrors(ps, specFlag)
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
from TransMask import transMask

from numpy import ndarray, any, average
from AmpOffset import ampOffset

from numpy import ndarray, any
from VoltageFromRawData import voltsFromData

from numpy import zeros_like, min
from scipy import polyfit, polyval
from numpy import arange, sum, where, floor
from T0 import calc_t0

from numpy import arange, square

from numpy import where, min
from numpy import array, average, sum, max, min, ndarray, abs, sqrt, absolute
from scipy.optimize import leastsq

from NumPhotons import numPhotons, _polyPulseFitFn, _calcCharPulseBeginAndEnd

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


from FilterChans import filterChans

from ScatteringAngle import calcScatAngle
from numpy import pi, arctan


from numpy import arange
from LambdaArray import lambdaArray

from numpy import logspace, log10, exp, linspace
from pylab import amap, where
from TeNeInitVals import NeTeInitVals

from MostProbable_NeTe import mostProbableNeTe

from numpy import e, linspace
from NeTeWithErrors import calcNeTeWithErrors

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

