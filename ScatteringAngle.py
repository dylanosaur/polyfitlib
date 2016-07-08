from numpy import pi, arctan
def calcScatteringAngle(ps):
    """Calculates the scattering angle for the given roa value of the poly."""
    a     = 0.5200 # The radius.
    alpha = 0.1733 # Height of detector above r = 0.
    beta  = 0.5163 # Perpendicular distance from laser to detector.
    r = ps.roa * a
    ps.scatAng = pi - arctan(beta / (alpha + r))