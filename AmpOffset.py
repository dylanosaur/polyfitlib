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
    STRUCK_MIN = ps.STRUCK_MIN
    STRUCK_MAX = ps.STRUCK_MAX

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