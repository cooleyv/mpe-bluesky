"""
Contains motor devices defining 1-ID-E portion of instrument. 

#TODO: Anticipated updates:
-- Addition of new near field stages/detector 
-- Switching out tomo systems (unclear impact on motor stacks)
-- Swapping AM chamber x and sample_y to AMCI from StepPak
-- Adding motors for D2 table/detector
    
#TODO: update mts when finished routing/reconnecting signal cables
#TODO: update OWIS system information
    
"""

#fmt: off

__all__ = [
    #BCS table ----------------
    "split_ic_e",
    #slits moved to `s1id_slits.py`
    #fast shutter moved to 's1id_shutters.py`
    "lens1_e", 
    "lens2_e", 
    "lens3_e", 
    "lens4_e",
    #Aero table SMS -----------
    "aero_table",
    "sms_aero",
    "sam_wheel",
    #in situ ------------------
    "cmu_furnace", 
    "rf_tube",
    "am",
    #load frames --------------
    # "mts", 
    #"rams3",
    "owis",
    #detectors ----------------
    "nf",  
    "tomo_us_e", 
    "det2_e",
    "hydra_positioner",
    "hydra_table", 
    "saxs",
    "tomo_ds_e",
    "vff",
]
#fmt: on

import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

import sys, pathlib
sys.path.append(str(pathlib.Path.home() / "bluesky/instrument/devices"))
#sys.path.append("/home/beams/S1IDTEST/bluesky/instrument/devices")
from generic_motors import * #generic_motors.py MUST be in devices folder

from ophyd import Component, Device, EpicsMotor


""" 
BCS table devices ---------------------------------------------------------------------
"""

class SplitICE(Device):
    y = Component(MPEMotor, "m19")

split_ic_e = SplitICE("1ide1:", name = "split_ic_e")


lens1_e = Generic5DOFDevice(
    #inverted
    "1ide1:", 
    name   = "lens1_e",
    xpv    = "m117", 
    ypv    = "m28",
    rotxpv = "m30",  
    rotypv = "m119", 
    rotzpv = "m31"
)

lens2_e = Generic5DOFDevice(
    #upright
    "1ide1:", 
    name   = "lens2_e",
    xpv    = "m118",    
    ypv    = "m29",
    rotxpv = "m32",    
    rotypv = "m120",    
    rotzpv = "m33"
)

lens3_e = Generic6DOFDevice(
    #inboard
    "1ide1:", 
    name   = "lens3_e",
    xpv    = "m82",    
    ypv    = "m89",    
    zpv    = "m81",
    rotxpv = "m44", 
    rotypv = "m83", 
    rotzpv = "m45"
)

lens4_e = Generic6DOFDevice(
    #outboard
    "1ide1:", 
    name   = "lens4_e",
    xpv    = "m85",        
    ypv    = "m114",       
    zpv    = "m115",
    rotxpv = "m116",    
    rotypv = "m88",     
    rotzpv = "m84"
)

""" 
Aero table SMS devices ----------------------------------------------------- 
"""

class AeroTable(Device):
    y1 = Component(MPEMotor, "m69")   #inboard, downstream
    y2 = Component(MPEMotor, "m70")   #outboard, upstream
    y3 = Component(MPEMotor, "m71")   #outboard, downstream

aero_table = AeroTable("1ide1:", name = "aero_table")


sms_aero = Generic8DOFDevice(
    "", 
    name   = "sms_aero",
    xpv    = "1ide1:m34",    
    ypv    = "1ide1:m35",    
    zpv    = "1ide1:m36",
    rotxpv = "1ide1:m87",    
    rotypv = "1ide:m9",      
    rotzpv = "1ide1:m86",
    x2pv   = "1ide1:m101",   
    y2pv   = "1ide1:m102"
)


class SamWheel(Device):
    x    = Component(MPEMotor, "m58")
    rotz = Component(MPEMotor, "m55")
    
sam_wheel = SamWheel("1ide1:", name = "sam_wheel") #motor cables not connected

""" 
In situ devices -----------------------------------------------------------
"""

class CMUFurnace(Device):
    x  = Component(MPEMotor, "m17")
    y  = Component(MPEMotor, "m94")   
    z  = Component(MPEMotor, "m18")
    #x2 = Component(MPEMotor, "m92")   #May be a duplicate of m17
    #z2 = Component(MPEMotor, "m100")   #May be a duplicate of m18
    
cmu_furnace = CMUFurnace("1ide1:", name = "cmu_furnace")


class RFTube(Device):
    tube_x    = Component(MPEMotor, "m37") #historically also used for GE shield X
    tube_y    = Component(MPEMotor, "m67")
    sam_x     = Component(MPEMotor, "m48")
    coil_y    = Component(MPEMotor, "m56")
    coil_z    = Component(MPEMotor, "m61")
    coil_roty = Component(MPEMotor, "m60")
    
rf_tube = RFTube("1ide1:", name = "rf_tube")   #motor cables not connected


class AM(Device):
    sam_x     = Component(MPEMotor, "m95")
    sam_y     = Component(MPEMotor, "m79") 
    sam_z     = Component(MPEMotor, "m96")
    chamber_x = Component(MPEMotor, "m68")
    chamber_y = Component(MPEMotor, "m76")
    
am = AM("1ide1:", name = "am")     #motor cables not connected

""" 
Load frames -------------------------------------------------------------------
"""

class MTS(Device):
    table_y1    = Component(MPEMotor, "m1",   kind = "hinted")
    table_y2    = Component(MPEMotor, "m2",   kind = "hinted")
    table_y3    = Component(MPEMotor, "m3",   kind = "hinted")
    x           = Component(MPEMotor, "m13",  kind = "hinted")    
    y           = Component(MPEMotor, "m16",  kind = "hinted")    #autodesktop says m10, which is BAD-- replaced with m16
    z           = Component(MPEMotor, "m14",  kind = "hinted")    
    x2          = Component(MPEMotor, "m9",   kind = "hinted")
    roty        = Component(MPEMotor, "m4",   kind = "hinted")

mts = MTS("1ide1:", name = "mts")  #motor and signal cables not connected


class RAMS3(Device):
    x           = Component(MPEMotor, "1idc:m2",     kind = "hinted")
    y           = Component(MPEMotor, "1idc:m6",     kind = "hinted")
    tiltx       = Component(MPEMotor, "1idc:m4",     kind = "hinted")
    tiltz       = Component(MPEMotor, "1idc:m3",     kind = "hinted")
    table_y     = Component(MPEMotor, "1idc:m5")
    top_rot     = Component(MPEMotor, "1idrams3:m1")
    bot_rot     = Component(MPEMotor, "1idrams3:m2")
    tension_z   = Component(MPEMotor, "1idrams3:m3")
    cen         = Component(MPEMotor, "1idrams3:m4")
    offset      = Component(MPEMotor, "1idrams3:m5") 
    
rams3 = RAMS3("", name = "rams3")  #motor cables not connected


class OWIS(Device):
    axis = Component(MPEMotor, "m43")
    
owis = OWIS("1ide1:", name = "owis")

""" 
Detector stacks ---------------------------------------------------------------------------
"""

class NearField(Device):
    x          = Component(MPEMotor, "1ide:m6",      kind = "hinted")
    y          = Component(MPEMotor, "1ide1:m59",    kind = "hinted")
    z          = Component(MPEMotor, "1ide:m7",      kind = "hinted")    
    x2         = Component(MPEMotor, "1ide1:m104",   kind = "hinted")
    focus      = Component(MPEMotor, "1ide1:m12",    kind = "hinted")
    tiltx      = Component(MPEMotor, "1ide1:m5",     kind = "hinted")
    tilty      = Component(MPEMotor, "1ide1:m6",     kind = "hinted")
    block_roty = Component(MPEMotor, "1ide1:m57",    kind = "hinted")
    block_y    = Component(MPEMotor, "1ide1:m39",    kind = "hinted")

nf = NearField("", name = "nf")


class TomoUSE(Device):
    x    = Component(MPEMotor, "m63")
    y    = Component(MPEMotor, "m40")   
    z    = Component(MPEMotor, "m62")
    rotz = Component(MPEMotor, "m38")

tomo_us_e = TomoUSE("1ide1:", name = "tomo_us_e")


class Det2E(Device):
    shield = Component(MPEMotor, "m42")
    
det2_e = Det2E("1ide1:", name = "det2_e")


class HydraTable(Device):
    table_x1 = Component(MPEMotor, "m109") #upstream
    table_x2 = Component(MPEMotor, "m106") #downstream
    table_y1 = Component(MPEMotor, "m105") #inboard, upstream
    table_y2 = Component(MPEMotor, "m107") #outboard, upstream
    table_y3 = Component(MPEMotor, "m108") #downstream
    
hydra_table = HydraTable("1ide1:", name = "hydra_table")
    
    
class Hydra(Device):
    z = Component(MPEMotor, "m7")

hydra_positioner = Hydra("1ide1:", name = "hydra_positioner")


class SAXS(Device):
    #FIXME: autodesktop motor numbers are different than current PV.DESCs/physical labels
    x            = Component(MPEMotor, "m52")
    y            = Component(MPEMotor, "m53")
    #shield      = Component(MPEMotor, "m66")  #could also be m46, m72
    shield_x     = Component(MPEMotor, "m49")  #autodesktop says m51
    shield_y     = Component(MPEMotor, "m50")  #autodesktop says m54
    diode_x      = Component(MPEMotor, "m51")
    diode_y      = Component(MPEMotor, "m54")
    
saxs = SAXS("1ide1:", name = "saxs")


class TomoDSE(Device):
    x = Component(MPEMotor, "m111")
    y = Component(MPEMotor, "m112")

tomo_ds_e = TomoDSE("1ide1:", name = "tomo_ds_e")


class VeryFarField(Device):
    r   = Component(MPEMotor, "m41")  
    eta = Component(MPEMotor, "m73") 

vff = VeryFarField("1ide1:", name = "vff")











  



