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

    try:
        vt.iterate_method(method='errNum')
        vt.iterate_method(method='chanFlagDC')
        vt.iterate_method(method='chanFlagAC')
        vt.iterate_method(method='satChans')
        vt.iterate_method(method='satChansDark')
        vt.iterate_method(method='str_offsetVolt')
        vt.iterate_method(method='str_ampOffset')
        vt.iterate_method(method='acq_offsetVolt')
        vt.iterate_method(method='acq_ampOffset')
        vt.iterate_method(method='STRUCK_MIN')
        vt.iterate_method(method='STRUCK_MAX')
    except Exception, ex:
        print 'test failed, ex=', ex

    return vt