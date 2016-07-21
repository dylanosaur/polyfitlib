import pycdf
import util
from numpy import sum

__all__ = ['PolyCalibration', 'Calibration']


class PolyCalibration:
    """Class to hold calibration information for a single poly. The class
    contains the following variables.

    The following are a single number per poly:
        fiberPos  -- The fiber position number.
        fiberSN   -- The fiber serial number.
        numAPD    -- The number of APDs in the poly.
        skipAPD   -- Equals 1 if the first APD is ignored. 0 otherwise.

    The following are arrays per poly. Each array has a number of elements
    equal to the number of APDs in the poly.
        APDfqe    -- f/qe for each APD.
        APDgain   -- Gain for each APD.
        ampOffset -- Amplifier offset for each APD.
        ampSN     -- Amplifier serial number.
        charPulse -- The characteristic pulse for each APD.
        
    The following are needed to interpret the transmission data (called trans)
    above:
        deltaLam  -- Wavelength time step for transmission.
        lam0      -- First wavelength value for transmission.
        trans     -- The measured transmission for each APD.
    """
    # Per-Poly data.
    fiberPos  = None
    fiberSN   = None
    numAPD    = None
    skipAPD   = None

    # Per-APD data.
    APDfqeDC      = None
    APDgainDC     = None
    APDfqeAC      = None
    APDgainAC     = None
    ampOffset     = None
    ampSN         = None
    charPulseDC   = None
    charPulseAC   = None
    
    # Information needed to interpret trans.
    deltaLam  = None
    lam0      = None
    trans     = None
    lam       = None



from numpy import pi
class Calibration:
    """This class provides an interface to the TS calibration file.
    Currently it only allows loading the file and reading the values, but in the
    future it may also allow modifying and saving the calibration file.
    """

    def __init__(self):
        """Constructor."""
        self.filename = None # The filename loaded.
        self.polyList  = None # The list of poly's in use.
        self.polyCalib = {} # Calibration data per poly.



    def loadCalibration(self, shotNum, data_plist, skipAPD = 1):
        """Locate and load the calibrations appropriate for the given shot
        number. If an error occurs, and exception will be raised.

        Parameters:
        shotNum    -- the MST shot number
        data_plist -- the list of polys used in shot
        skipAPD    -- If this is equal to one, skip the first APD in each poly.
        """
        # Clear data.
        self.polyList = None
        self.polyCalib = {}

        # Load the correct calibration file
        self.filename = util.getCalibrationFilePath(shotNum)
        print self.filename
        nc = pycdf.CDF(self.filename)

        # Fetch the list of polys and cast as integers.
        self.polyList = data_plist
        #print "Loading Calib Data\n"
        for poly in self.polyList:
            # The NetCDF arrays are zero-indexed
            i = poly - 1

            # Load the information from the file.
            calib = PolyCalibration()
            # determine which APDs to skip
            calib.skipAPD = skipAPD

            # Per poly
            calib.numAPD = int(nc.var('numAPD').get()[i])

            numAPD = calib.numAPD

            # Per APD
            calib.APDfqeDC = nc.var('APDfqe').get()[i][calib.skipAPD : numAPD]
            calib.APDgainDC = nc.var('APDgain').get()[i][calib.skipAPD : numAPD]
            #calib.APDfqeAC = nc.var('APDfqeAC').get()[i][calib.skipAPD : numAPD]
            #calib.APDgainAC = nc.var('APDgainAC').get()[i][calib.skipAPD : numAPD]
            #calib.ampOffset = nc.var('ampOffset').get()[i][skipAPD : numAPD] 
            # the characteristic pulse may be too long?  trim it just a bit to 64 samples
            cp = nc.var('charPulse').get()[i][calib.skipAPD : numAPD]
            for q in range(cp.shape[0]):#make char pulse negative-going to match the data for fitting purposes. LAM 4/29/2014
                cp[q] = -1.0 * cp[q] / sum(cp[q])
            calib.charPulseDC = cp[:,10:74]
            #calib.charPulseDC = nc.var('charPulse').get()[i][calib.skipAPD : numAPD]
            #calib.charPulseAC = nc.var('charPulseAC').get()[i][calib.skipAPD : numAPD]
            calib.trans = nc.var('instFunc').get()[i][calib.skipAPD : numAPD]

            # Transmission function related.
            if shotNum< 1140327000:
                calib.lam0 = nc.var('lam0').get()
                calib.deltaLam = nc.var('deltaLam').get()
                
            else:
                calib.lam = nc.var('instFuncLambdas').get()

            self.polyCalib[poly] = calib

        

    def getPolyList(self):
        """Return the list of polys that have calibration data."""
        return self.polyList



    def getPolyCalibration(self, poly):
        """Return a PolyCalibration object for the given poly."""
        return self.polyCalib[poly]
