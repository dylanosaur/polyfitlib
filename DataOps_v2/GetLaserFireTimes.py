from util import getMdsServer
from numpy import mean, max, where, array, diff, median, arange
from numpy import concatenate, absolute, roll, logical_and

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
    try:
        from pmds import mdsconnect, mdsopen, mdsvalue, mdsclose, mdsdisconnect
        from pmds import mdsput
    except:
        print "MDSPlus module missing: some functionality will be unavailable."


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
