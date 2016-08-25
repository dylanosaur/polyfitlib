# This program is part of the test suite
# It will perform statistical analysis on the test object
# Namely counting error rates and comparing data output
# from the two code versions

import numpy as np
import matplotlib.pyplot as plt
import UserDict


def plot_2d(test_obj, xlabel='old Te values', ylabel='new Te values', title='shot 1140726089', axis=[0,5000,0,5000]):

    # first extract information from test object
    old = test_obj.old
    new = test_obj.new
    num_bursts = len(old)
    num_segs = len(old[1])
    num_fits = num_bursts * num_segs

    # array to store old and new data
    Te_array = [range(num_fits), range(num_fits)]
    n = 0
    # bad is an error record
    error_dict = UserDict.UserDict()
    # error_dict['old', errNum] += 1 for each error instance

    # make sure arrays are zeroed properly
    for i in xrange(0, num_fits):
            Te_array[0][n] = 0
            Te_array[1][n] = 0

    # Initialize cache
    error_type = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256,
                  100, 200, 300, 400, 500, 600, 700, 800, 900]
    for i in range(len(error_type)):
        error_dict['old', error_type[i]] = 0;
        error_dict['new', error_type[i]] = 0;


    for i in xrange(1, num_bursts):
        if i ==16: continue #this polychromator is in Japan
        for j in xrange(0, num_segs):
            error_dict['old', old[i][j].errNum] += 1
            error_dict['new', new[i][j].errNum] += 1
            if old[i][j].errNum != 0 or new[i][j].errNum !=0:
                print i, j, old[i][j].errNum, new[i][j].errNum
            Te_array[0][n] = old[i][j].Te
            Te_array[1][n] = new[i][j].Te
            n += 1

    # write cache to array for simpler handling
    errors = (range(len(error_type)), range(len(error_type)) )
    for i in range(len(error_type)):
        errors[0][i] = error_dict['old', error_type[i]]
        errors[1][i] = error_dict['new', error_type[i]]
    print 'estimated', num_fits, 'fits, but found', n
    print 'error numbers and hits cache object:\n', error_dict

    x = Te_array[0]
    y = Te_array[1]




    # cute baby function to make lines shorter
    def cute(floating_point_num):
        return str(round(floating_point_num, 3))




    plt.figure(1)
    # Te mapping plot, Te old vs. Te new
    plt.subplot(221)
    plt.plot(x, y, 'ro')

    #title += '\n new bad Te fit fraction = ' + cute(1-(error_dict['new', 0]*1.0)/n)
    #title += '\n old bad Te fit fraction = ' + cute(1-(error_dict['old', 0]*1.0)/n)
    #title += '\n 0 = no error, 100 = unknown, 800 = Failed to find most probable temperature/density combination.'
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.axis(axis)

    # Error stats plot, counts vs error type
    # Example data

    y_pos = np.arange(len(error_type))

    plt.subplot(223)
    plt.barh(y_pos, errors[0], align='center', alpha=0.4)
    plt.yticks(y_pos, error_type)
    plt.xlabel('error codes')
    plt.title('Old error distribution')

    plt.subplot(224)
    plt.barh(y_pos, errors[1], align='center', alpha=0.4)
    plt.yticks(y_pos, error_type)
    plt.xlabel('error codes')
    plt.title('New error distribution')

    plt.show()

    return error_dict

def help():
    print "x.plot_2d(out, xlabel='Te current', ylabel='Te with some cache clearing', title='shot 1140726089')"