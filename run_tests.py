# Written by Dylan Adams on 07/01/16
# This program runs the testing scripts, currenlty just value tests

from AmpOffset_tests import AmpOffsetTests


def main():

    try:
        # function returns list of ps objects
        # vt for value tests
        vt = AmpOffsetTests()
        if len(vt.new) != len(vt.old):
            print 'ps objects not of same size'
        else:
            pass
    except Exception, ex:
        print 'load test object failed:', ex

        # run main tests
    vt.test_errNum_values()
    vt.test_str_offsetRaw_values()
    vt.test_shapes_values()

    return vt
