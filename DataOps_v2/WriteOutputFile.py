import util

def writeOutputFile(data):
    fn = util.getSaveFilePath(data.shotNum)
    with open(fn, 'w') as f:
        f.write(data.getReadme(False))