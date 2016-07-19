# Program written 07/06/16 by Dylan Adams
# Will process file and find all occurrences of keywords


def help():
    print "occ= p.find_occ('./AmpOffset.py', dir)"
    print "new_kw = p.build_keywords(path)"
    print "dir = p.ps_methods_dir()"

def find_occ(path, kw):
    num_kw = len(kw)
    i = 0
    occ = []
    occ.append('ps.errNum')
    while i < num_kw:
        list = find_word(path, kw[i])
        if len(list[0]) > 0:
            occ.append(kw[i])
        i += 1
    # close while loop
    return occ

def ps_methods_dir():
    dir = build_keywords('./Data.py')
    return dir

def build_keywords(keyword_file_path):
    path = keyword_file_path
    keywords = find_word(path, 'self')
    new_kw = []
    i = 0
    while i < len(keywords[0]):
        if keywords[1][i] < 145:
            if keywords[1][i] > 38:
                new_kw.append(pull_name(keywords[0][i]))
                # print new_kw[-1]
        i += 1
    return new_kw

def pull_name(line):
    # find functions of the form: ***def func_name(***):**
    # star denotes characters can be anything
    i=0; name = []; index_start = 0; index_stop = 0;
    prefix = 'self.'
    while i<(len(line)):
        if (line[i:i+len(prefix)] == prefix):
            index_start = i+len(prefix)
        if index_start > 0:
            if (line[i] == ' ' ):
                index_stop = i
                break
            elif line[i] == '\t':
                index_stop = i
                break
        i = i+1
    name = 'ps.' + line[index_start:index_stop]
    return name

def find_word(file_path, word):
    list = [[], []]
    i = 0
    for line in open(file_path, 'r'):
        if word in line:
            list[0].append(line)
            list[1].append(i)
            # print line
        i += 1
    return list