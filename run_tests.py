# Written by Dylan Adams on 07/01/16
# This program runs the testing scripts, currenlty just value tests

from test_values import My_AmpOffset_Tests


def main():

    try:
        
        vt = My_AmpOffset_Tests()
        print '\nstarting testing suite'
        if (len(vt.new) != len(vt.old)):
            print 'ps objects not of same size'
            
        psNum = len(vt.new)
        i = 0
        while i<psNum:
            vt.test_errNum_values(i)
            j = 0
            while j<len(vt.new[i].str_offsetRaw):
                vt.test_str_offsetRaw_values(i, j)
                j += 1
            i += 1
        # end while loop
        print 'presumably tests were passed'
    except Exception, ex:
        print 'test failed:', ex

    return vt
    
