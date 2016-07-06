#Program written by Dylan Adams on 06/30/16
#This function is a prototype for a future unit test of PFL versions

import sys
sys.path.append("/x/tsfit/ts/current/ts")
import PolyFitLib as pfl_old
sys.path.append("/x/tsfit/code/adams")
import PolyFitLib_v1 as pfl_new
sys.path.append("/x/tsfit/code/adams/MSTdataAccess")
import readTStree as rts

def loader():
    
    output = pfl_old.fitShot(1140726089, burstLen = 25)
    shot_old = rts.Shot(1140726089)
    print 'old shot te data:'
    print shot_old.ts.te
    
    
    output = pfl_new.fitShot(1140726089, burstLen = 25)
    shot_new = rts.Shot(1140726089)
    print 'new shot te data:'
    print shot_new.ts.te
    
    return shot_old, shot_new

def help_me():
    print 'import load_from_arb_dir as l'
    print 'old, new = l.main()'
    return None
