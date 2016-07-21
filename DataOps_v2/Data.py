import pycdf
import util as util
from error import WARNING, ERROR
from numpy import ones, zeros
from calibration import Calibration, PolyCalibration


class PolySegData:
    """Class to hold data for a single poly and segment."""
    def __init__(self):
        """Constructor."""
        self.calib       = None # The associated PolyCalibration object.

        self.poly        = None # The poly number.
        self.segment     = None # The segment number.
        self.shotNum     = None
        #######################################################################
        # The following data comes from the NetCDF data file.                 #
        #######################################################################
        # These arrays of Struck (DC) data have one element per APD for this poly.
        self.str_rawData     = None # The raw data.
        self.str_offsetRaw   = None # Raw offset data.
        self.str_voltsPerBit = None # The volts per bit.
        self.str_deltat      = None # The sample rate.
        self.str_zeroBit     = None # Digitizer offset.

        # These arrays of Acqiris (AC) data have one element per APD for this poly.
        self.acq_rawData     = None # The raw data.
        self.acq_offsetRaw   = None # Raw offset data.
        self.acq_voltsPerBit = None # The volts per bit.
        self.acq_deltat      = None # The sample rate.
        self.acq_offset      = None # Digitizer offset.

        # These variables are a single number for the poly.
        self.roa         = None # Fractional radial position.

        #######################################################################
        # Keeping track of the warnings and errors generated during the fit   #
        # process.							      #
        #######################################################################
        self.errNum		= 0     # The error number.
        self.errMsg		= None  # An additional error message.
        self.warnNum		= 0     # The warnings (bitwise or'ed). This is stored
                	                # as the quality in MDSplus.
        self.warnMsg		= {}    # Map from warn number to additional text.

        self.chanFlagDC		= None	# List of usable DC channels (1 = usable, 0 = unusable)
        self.chanFlagAC		= None	# List of usable AC channels
        self.satChans		= None	# List of channels that saturated
        self.satChansDark	= None	# List of channels that saturated during the dark segment
        self.noPulseFitChans	= None  # List of channels that failed the PolyPulseFit routine

        #######################################################################
        # The following data is calculated during the fitting process.        #
        #######################################################################
        self.str_offsetVolt	= None  # Amplifier dark voltage data calculated from
                                        # self.offsetRaw data.
        self.str_ampOffset	= None  # Amplifier offset for each APD.
        self.acq_offsetVolt	= None  # Amplifier dark voltage data calculated from
                                        # self.offsetRaw data.
        self.acq_ampOffset	= None  # Amplifier offset for each APD.
        
        self.str_voltData	= None  # DC data trace in volts.
        self.acq_voltData	= None  # AC data trace in volts.
        self.t00_dc		= None  # The initial guess for t0.
        self.t0_dc		= None  # The time of the pulse within the segment.
        self.t00_ac		= None  # The initial guess for t0.
        self.t0_ac		= None  # The time of the pulse within the segment.

        self.scatAng		= None  # The scattering angle.

        # These are the coefficients needed to fit voltData at t0 with a
        # quadratic plus the characteristic pulse.
        # See PolyFitLib._polyPulseFitFn.
        self.t0DCBgCoeffs	= None  # the coefficients for the t0 background fit (DC)
        self.t0ACBgCoeffs	= None  # the coefficients for the t0 background fit (AC)
        self.polyPulseCoeffs0   = None  # The initial guess
        self.polyPulseCoeffsDC  = None  # The final coefficients
        self.polyPulseCoeffsAC  = None  # The final coefficients

        self.cPulseStart        = None  # The index of the beginning of the char pulse.
        self.cPulseEnd          = None  # The index of the end of the char pulse.

        self.scatPhotonsDC      = None  # The number of DC scattered photons.
        self.scatPhotonsAC      = None  # The number of AC scattered photons.
        self.bgPhotons          = None  # The number of background photons.
        self.errPhotons         = None  # The error in the photon measurement.
        self.residual           = None
        self.weight             = None
        self.weightSum          = None
        self.normalizedResidual = None

        self.chiRedMin          = None

        # The following arrays contain the filtered data to be used in the Bayesian fit
        self.scPhotons_Bayes	= None
        self.bgPhotons_Bayes	= None
        self.fqe_Bayes		= None
        self.trans_Bayes	= None

        # Lambda array is used to calculate the expected number of photons.
        # This is used by the selden equation.
        self.lam = None

        # Some other globals to be used in analysis added 07/06/16
        self.STRUCK_MIN = 0
        self.STRUCK_MAX = 65535
        self.Te_MIN = 10.0
        self.Te_MAX = 3498.0
        self.NE_STEPS = 51
        self.TE_STEPS = 101
        self._modelCache = {}

        # Initial guesses for temperature and density.
        self.Te0 = 0 # Temperature initial guess.
        self.ne0 = 0 # Density initial guess.

        # The most likely temperature/density combination. The temperature here
        # may differ from the most likely temperature. 
        self.Te1 = 0
        self.ne1 = 0

        # The following define a grid of points at which the probability 
        # will be calculated. 
        self.TeArray = None
        self.neArray = None
        self.probGrid = None

        # The following are the temperature and density probability curves.
        # TeProb will have the same shape (length) as TeArray above, and
        # neProb will have the same shape as neArray.
        self.TeProb = None
        self.neProb = None
        
        # Bayesian analysis produces a resulting temperature, density, and
        # uncertainties.
        self.Te       = 0 # The temperature.
        self.TeErrMin = 0 # The lower error bar value.
        self.TeErrMax = 0 # The upper error bar value.

        self.ne       = 0 # The density.
        self.neErrMin = 0 # The lower error bar value.
        self.neErrMax = 0 # The upper error bar value.



    def setError(self, errorNum, msg=None):
        """Set the fatal error condition. This function will raise an 
        exception.
        """
        self.errNum = errorNum
        self.errMsg = msg
        # Added random exception object because python complained with no object -Bill
        raise Exception("Fatal TS Error")



    def setWarning(self, warnNum, msg=None):
        self.warnNum = self.warnNum | warnNum
        if msg != None:
            self.warnMsg[warnNum] = msg
            
            
            
    def getErrWarnStr(self):
        """Get a string containing the errors and warning produced while
        fitting this poly-segment.
        """
        st = None
        prefix = '%04d %02d' % (self.segment, self.poly)
        if self.errNum != 0:
            st = '%s ERROR (%04d) %s \n' % (prefix, self.errNum, 
                                         ERROR[self.errNum])
            if self.errMsg is not None:
                st += '    %s \n' % (self.errMsg)
        elif self.warnNum != 0:
            st = ''
            a = 1
            for i in range(8):
                if self.warnNum & a:
                    st += '%s WARNING (%04d) %s \n' % (prefix, a, WARNING[a])
                    if a in self.warnMsg:
                        st += '    %s \n' % (self.warnMsg[a])
                a = a << 1

	    if len(self.satChans) != 0:
	        st += '    Saturation in Channels: %s \n' % (self.satChans)

	if st != None:
	    stripped = st.rstrip()
            st = stripped
        return st


    def getCompactErrWarnStr(self):
        """Get a more compact string containing the errors and warnings 
        produced while fitting this poly-segment.
        """
        st = None
        prefix = '%04d %02d' % (self.segment, self.poly)
        if self.errNum != 0:
            st = '%s ERROR: %04d' % (prefix, self.errNum)
        elif self.warnNum != 0:
            st = '%s WARNING: %04d' % (prefix, self.warnNum)
            
        return st



class Data:
    """Class providing an interface to the raw data NetCDF files."""
    def __init__(self):
        """Constructor."""
        self.filename    = None # The filename the data was loaded from.

        # Laser fire times come from the laser diode data in mdsplus. 
        self.laserFireTimes = None

        self.shotNum = None
        self.data = {}
        self.polyList = None
        self.segments = None
        self.prelasing = None
 

    def loadData(self, shotNum, skipAPD = 1):
        """Load all the data for the given shot.

        Parameters:
        shotNum -- The shot number to load.
        skipAPD -- Set to 1 to skip the first APD (because of saturation).
        """
        from numpy import arange
        self.shotNum = shotNum

        self.data = {} # Clear old data.

        self.filename = util.getDataFilePath(shotNum)

        nc = pycdf.CDF(self.filename)
        #print "Loading Raw Data\n"
        str_rawData = nc.var('str_rawdata').get()
        str_voltsPerBit = nc.var('str_voltsperbit').get()
        str_deltat = nc.var('str_deltat').get()
        str_zeroBit = nc.var('str_offset').get()

        acq_rawData = nc.var('rawdata').get()
        acq_voltsPerBit = nc.var('voltsperbit').get()
        acq_deltat = nc.var('deltat').get()
        acq_offset = nc.var('offset').get()

        roa = nc.var('roa').get()

        # take the poly list from the netCDF file (one entry for each channel) and unique-ify it
        # to have only one entry per poly
        plist_long = nc.var('poly').get()
        seen = {}
        for item in plist_long:
            seen[item] = 1
            plist_short = seen.keys()
            plist_short.sort()	# probably unnecessary, but just in case
            self.polyList = plist_short

        # load the calibration data after the file data, so that the poly list can be loaded for this shot
        self.calib = Calibration()
        self.calib.loadCalibration(shotNum, plist_short, skipAPD)

        # The number of data segments is one less than the total number of 
        # segments. The last segment in the data file is used for calculating
        # the amplifier offsets.
        self.segments = arange(str_rawData.shape[1] - 1)

        apdIndex = 0

        for poly in self.polyList:
            self.data[poly] = {}
            calib = self.calib.getPolyCalibration(poly)

            for segment in self.segments:
                numAPD = calib.numAPD
                ps = PolySegData()

                ps.calib = calib
                ps.poly = poly
                ps.segment = segment
                ps.shotNum=self.shotNum

                # If calib.skipAPD is 1, then we don't load the data for the
                # first APD.
                start = apdIndex + calib.skipAPD
                end = apdIndex + numAPD
                ps.str_voltsPerBit = str_voltsPerBit[start:end]
                ps.str_deltat = str_deltat[start:end]
                ps.str_zeroBit = str_zeroBit[start:end]

                ps.acq_voltsPerBit = acq_voltsPerBit[start:end]
                ps.acq_deltat = acq_deltat[start:end]
                ps.acq_offset = acq_offset[start:end]

                ps.roa = roa[start]
                # correction because p20 and p21 were flipped in the calib file
                # for Fall 2012 only, radial calib redone in December
                #if poly == 20:
                #    ps.roa = 0.6030
                #elif poly == 21:
                #    ps.roa = 0.5181

                ps.str_rawData = str_rawData[start:end, segment]
                ps.acq_rawData = acq_rawData[start:end, segment]

                # It's a bit inefficient to store the offset data with each 
                # PolySegData object, but it is simple.
                ps.str_offsetRaw = str_rawData[start:end, len(self.segments)]
                ps.acq_offsetRaw = acq_rawData[start:end, len(self.segments)]

                # Set the usability flags for the DC and AC channels
                # The AC channels are set to be unused until AC calib is figured out
                ps.chanFlagDC = ones(numAPD - calib.skipAPD)
                #ps.chanFlagAC = ones(numAPD - calib.skipAPD)
                ps.chanFlagAC = zeros(numAPD - calib.skipAPD)

                self.data[poly][segment] = ps
            apdIndex += numAPD


    
    
    def getSegments(self):
        """Return a list of available segment numbers."""
        return self.segments



    def getPolyList(self):
        """Return the list of polys to fit."""
        return self.polyList


    
    def getPolyListSortedROA(self):
        """Return the list of polys in order of increasing ROA."""
        def sortFn(p1, p2):
            ps1 = self.getPolySegData(p1, 0)
            ps2 = self.getPolySegData(p2, 0)
            if ps1.roa == ps2.roa:
                return 0
            elif ps1.roa > ps2.roa:
                return 1
            else:
                return -1

        tmpList = list(self.getPolyList())
        tmpList.sort(sortFn)
        return tmpList




    def getPolySegData(self, poly, segment):
        """Get the data for a given poly and segment combination.

        Parameters:
        poly    -- The poly number.
        segment -- The segment number.

        Returns: The data for the given poly and segment in the form of a
        PolySegData object.
        """
        return self.data[poly][segment]


    
    def setPolySegData(self, poly, segment, ps):
        """Set the data for a given poly and segment to the given PolySegData
        object.

        Parameters:
        poly    -- The poly number.
        segment -- The segment number.
        ps      -- The PolySegData object.
    
        Returns: Nothing.
        """
        self.data[poly][segment] = ps



    def getReadme(self, bCompact=True):
        """Return a string to save to the readme variable in mdsplus."""
        ret = ''
        for segment in self.getSegments():
            for poly in self.getPolyList():
                ps = self.getPolySegData(poly, segment)
                st = None
                if bCompact:
                    st = ps.getCompactErrWarnStr()
                else:
                    st = ps.getErrWarnStr()
                    
                if st != None:
                    ret += '%s\n' % st
        return ret


