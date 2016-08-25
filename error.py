# This file defines errors and warnings. 

# Warnings are bitwise ored because we can have more than one warning.
WARNING = {
    1   : 'Fatal error.',
    2   : 'Negative background photons.',
    4   : 'Saturation in raw data.',
    8   : 'Saturation in amplifier offset data.',
    16  : 'Failed to find AC t0 value.',
    32  : 'Failed to fit poly-pulse.',
    64  : 'One or more channels skipped in the Bayesian analysis.',
    128 : 'Undefined.'
    256 : 'Uncertainties from ne or Te fits are larger than reported'
}

# Errors are fatal, so are not bitwise ored. 
ERROR = {
    100  : 'Unknown error.',
    400  : 'Saturation in raw data during laser pulse.',	# Deprecated
    500  : 'Failed to find t0 value.',
    600  : 'Failed to fit poly-pulse.',				# Deprecated
    650  : 'Not enough channels to perform Bayesian analysis.',
    700  : 'Grid search failed.',
    800  : 'Failed to find most probable temperature/density combination.',
    900  : 'Temperature or density error bars are too large.',
}

