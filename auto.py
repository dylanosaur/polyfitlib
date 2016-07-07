# This script just generates code for tests
# Lots of variables to check, and rather tedious at that

from parser import ps_methods_dir, find_occ

# exists only in dreams
# def write_script():

def build_tests():
    dir = ps_methods_dir()
    occ = find_occ('./AmpOffset.py', dir)
    i = 0
    while i < len(occ):
        word_size = len(occ[i])
        indent = '    '
        method = occ[i][3:word_size]
        type = 'Sequence'
        if method == 'errNum' or method == 'STRUCK_MIN' or method == 'STRUCK_MAX': type = ''
        print indent+'def check_'+ method +'_values(self, n, m):'
        print indent+'    if n ==1 and m ==0:'
        print indent+"        print 'sequence assert starting for", method, "test'"
        print indent+"        a = self.new[n][m]."+method
        print indent+"        b = self.new[n][m]."+method
        print indent+"        self.assert"+type+"Equal(a, b)"
        print indent+"    if n == len(self.old)-1 and m == len(self.old[n])-1:"
        print indent+"        print 'sequence assert complete for", method, "test'"
        i += 1
    return None

def build_it_handler():
    dir = ps_methods_dir()
    occ = find_occ('./AmpOffset.py', dir)
    i = 0
    while i < len(occ):
        word_size = len(occ[i])
        method = occ[i][3:word_size]
        indent = '\t'
        print indent+"\t    if method == '"+method+"':"
        print indent+"\t        try: self.check_"+method+"_values(n, m)"
        print indent+"\t        except Exception, ex:"
        print indent+"\t            print method, 'test failed ex=', ex"
        print indent+"\t            break"
        i += 1

def build_runner():
    dir = ps_methods_dir()
    occ = find_occ('./AmpOffset.py', dir)
    i = 0
    while i < len(occ):
        word_size = len(occ[i])
        method = occ[i][3:word_size]
        print "\tvt.iterate_method(method='"+method+"')"
        i += 1