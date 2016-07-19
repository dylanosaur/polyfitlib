from __future__ import with_statement

import os
import os.path
import cPickle
from datetime import date
import glob


DATA_PATH = '/x/tsfit/data'
CALIB_PATH = '/x/tsfit/python_calib'
SAVE_PATH = '/x/tsfit/python_output'



def getShotsForDate(shotDate):
    """Given a date, return a list of shots that have TS data files."""
    #folder = shotDate.strftime('%Y%m%d')
    #path = os.path.join(DATA_PATH, folder)
    path = os.path.join(DATA_PATH, shotDate)
    globExp = os.path.join(path, '*.nc')
    fileList = glob.glob(globExp)
    shotList = []
    for fPath in fileList:
        try:
            fName = os.path.split(fPath)[1]
            shotList.append(int(fName[7:17]))
        except:
            pass
    return sorted(shotList)



def getSaveFilePath(shotNum):
    dateNum = shotNum/1000 - 1000000 + 20000000
    path = '%s/%s' % (SAVE_PATH, dateNum)
    if not os.path.exists(path):
        os.makedirs(path)
    return '%s/%s/%s.txt' % (SAVE_PATH, dateNum, shotNum)



def getDataFilePath(shotNum):
    """Given a shot number, return the path to the netCDF data file."""
    dateNum = shotNum/1000 - 1000000 + 20000000
    return '%s/%s/tsdata_%s.nc' % (DATA_PATH, dateNum, shotNum)



def getCalibrationFilePath(shotNum):
    """Given a shot number, return the path to the matching calibration 
    file.
    """
    from os.path import splitext
    from os import listdir

    calibList = [int(splitext(item)[0]) for item in listdir(CALIB_PATH)]
    calibList.sort()

    calibShot = None

    for shot in calibList:
        if shot <= shotNum:
            calibShot = shot
        else:
            break;

    if not calibShot:
        raise Exception('No calibration file found for shot %s.' % shotNum)

    return '%s/%s.nc' % (CALIB_PATH, calibShot)



def getMdsServer(shot):
    year = int(shot/1e7) + 1900
    month = int(shot%1e7/1e5)
    day = int(shot%1e5/1e3)
    
    shotDate = date(year, month, day)

    if shotDate == date.today():
        return 'aurora'
    else:
        return 'dave'
    
    
    
    

