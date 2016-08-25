# This program written on Aug 24, 2016 by Dylan Adams
# It provides the functions for determing if the error returned
# is reasonable or defaulting (errors  = endpoints is bad)

def assertNotEqual(reported_errors, probability_array):
    # reported errors is a 2-ple of err_lower, err_upper
    # probability array is the array from which the errors were determined
    lower = reported_errors[0]
    upper = reported_errors[1]
    # rename array for cleanliness
    a = probability_array
    if lower == a[0] or lower == a[-1]:
        print 'lower error bound is likely bad'
        return 0
    elif upper == a[0] or upper == a[-1]:
        print 'upper error bound is likely bad'
        return 0
    else: return 1

def checkFitErrors(ps):
    # return 1 for good errors, 0 for problematic errors
    # feed ps object data into error checking method
    reported_errors = ps.TeErrMin, ps.TeErrMax
    Te_result = assertNotEqual(reported_errors, ps.TeArray)
    reported_errors_ne = ps.neErrMin, ps.neErrMax
    ne_result = assertNotEqual(reported_errors_ne, ps.neArray)
    if Te_result ==0 or ne_result ==0:
        print 'found a problem child: poly: segment:', ps.poly, ps.segment
        return 0
    else: return 1
