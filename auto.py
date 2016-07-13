# This script just generates code for tests
# Lots of variables to check, and rather tedious at that

from parser import ps_methods_dir, find_occ

# exists only in dreams
# def write_script():

path = './NeTeWithErrors.py'
def it_handler_v2():
    dir = ps_methods_dir()
    indent = "    "+"    " # 8 spaces
    for i in xrange(0,len(dir)):
        type = 'Sequence'
        word_size = len(dir[i])
        method = dir[i][3:word_size]

        if method == 'errNum' or method == 'STRUCK_MIN' or method == 'STRUCK_MAX': type = ''
        if method == 't0_dc' or method == 't0_ac': type = ''

        print indent+"if method == '"+method+"': self.assert"+type+"Equal(old."+method+", new."+method+")"



def build_tests():
    dir = ps_methods_dir()
    occ = find_occ(path, dir)
    i = 0
    while i < len(occ):
        word_size = len(occ[i])
        indent = '    '
        method = occ[i][3:word_size]
        type = 'Sequence'
        if method == 'errNum' or method == 'STRUCK_MIN' or method == 'STRUCK_MAX': type = ''
        if method == 't0_dc' or method == 't0_ac': type = ''
        print indent+'def check_'+ method +'_values(self, n, m):'
        print indent+'    if n ==1 and m ==0:'
        print indent+"        print 'sequence assert starting for", method, "test'"
        print indent+"        a = self.old[n][m]."+method
        print indent+"        b = self.new[n][m]."+method
        print indent+"        self.assert"+type+"Equal(a, b)"
        print indent+"    if n == len(self.old)-1 and m == len(self.old[n])-1:"
        print indent+"        print 'sequence assert complete for", method, "test'"
        i += 1
    return None

def suite():
    list_out = build_it_handler()
    return list_out

def build_it_handler():
    dir = ps_methods_dir()
    occ = find_occ(path, dir)
    i = 0
    list = []
    while i < len(occ):
        word_size = len(occ[i])
        method = occ[i][3:word_size]

        indent = '    ' # 4 spaces
        print indent+"if method == '"+method+"':"
        print indent+"    self.check_"+method+"_values(n, m)"
        list.append(method)
        #print indent+"    except Exception, ex:"
        #print indent+"        print method, 'test failed ex=', ex"
        #print indent+"        break"
        i += 1
    return list

def build_runner():
    dir = ps_methods_dir()
    occ = find_occ(path, dir)
    i = 0
    while i < len(occ):
        word_size = len(occ[i])
        method = occ[i][3:word_size]
        print "        vt.iterate_method(method='"+method+"')"
        i += 1