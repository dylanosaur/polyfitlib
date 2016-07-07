from numpy import where, zeros_like, max, min

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