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