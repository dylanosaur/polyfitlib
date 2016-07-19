from numpy import ndarray

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
