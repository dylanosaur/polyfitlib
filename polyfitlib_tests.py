from __future__ import with_statement

# Grid search parameters - rough search
# Global constants Te_MIN, Te_MAX, NE_STEPS, TE_STEPS deprecated 07/19/16 -DTA
# Moved to an attribute of ps object (in ./DataOps/Data.py )

# Saturation levels
# ACQIRIS_MIN and MAX usage commented out in ./DataOps/ampOffset.py
ACQIRIS_MIN = -128
ACQIRIS_MAX = 127
# STRUCK_MIN, STRUCK_MAX moved to ps object attributes

# Laser wavelength
# LASER_LAM =1064.3 moved to ps object attribute

# Logbook quality
LOGBOOK_TRUE = 1
LOGBOOK_UNSURE = -1

# Create model cache
import UserDict
_modelCache = UserDict.UserDict()

#MPTS_LASERON = '\\mraw_ops::btdot_128_180'
#DIM_MPTS_LASERON = 'dim_of(\\mraw_ops::btdot_128_180)*1000.0'


# The chunk-size is the approximate number of poly-segments each processor
# should fit at one time. This affects the efficiency of the multiprocessing
# code. You would like to maximize the concurrent use of processors while 
# minimizing the overhead of fetching new jobs. After some testing, it looks
# like any small number (1 - 16) is fine. Even 1. This might change for larger 
# numbers of jobs, or for faster processors / more processors. 
MULTIPROC_CHUNK_SIZE = 8

import warnings
warnings.simplefilter("ignore")


from DataOps.GetLaserFireTimes import getLaserFireTimes
from DataOps.Data import Data
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
        calcInitVals(ps, 10.0, specFlag)
        calcMostProbable(ps, specFlag)
        calcWithErrors(ps, specFlag)
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

# the effect of transMask has been shifted to the makeCDF routine,
# so the calibration file already contains a masked transmission function.
# calcTransMask can be removed from PolyFitLib to save time

# these files have been moved to the DataOps package, a local directory
from DataOps.TransMask import transMask
from DataOps.AmpOffset import ampOffset
from DataOps.VoltsFromData import voltsFromData
from DataOps.Calc_t0 import calc_t0
from DataOps.NumPhotons import numPhotons
from DataOps.FilterChans import filterChans
from DataOps.CalcScatAngle import calcScatAngle
from DataOps.LambdaArray import lambdaArray
from DataOps.CalcInitVals import calcInitVals
from DataOps.CalcMostProbable import calcMostProbable
from DataOps.CalcWithErrors import calcWithErrors
