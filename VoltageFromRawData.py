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