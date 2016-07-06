# Written by Dylan Adams on 07/01/16
# This program runs the testing scripts, currenlty just value tests

from test_values import MyValueTests


def main():

    try:
        value_tests = MyValueTests()
        value_tests.setUp()
        print '\nstarting testing suite'
        value_tests.test_time_values()
        value_tests.test_te_values()
        value_tests.test_mask_values()
    except Exception, ex:
        print 'test failed:', ex

    return value_tests
    
