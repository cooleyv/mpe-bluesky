"""
Contains motor devices defining 1-ID-C portion of instrument

#TODO: Confirm motor numbers once cabling/labeling is complete. 
#TODO: Update IOC information for AMCI units. 
#TODO: Update IOC information for mobile drivers. 
#FIXME: Troubleshooting/support needed to add ELMO and hexapod controllers to devices. 
#TODO: Update motor and IOC information when new Kohzu units are delivered/tested. 
#TODO: SWAP OUT MOBILE RACK LENSES
"""


#fmt: off

__all__ = [
    # "ic_us_c",
    #slits relocated to `s1id_slits.py`
    #fast shutter relocated to `s1id_shutters.py`
    # "fourc_table",
    "fourc",
    "fourc_sample",
    "atten_c",
    "lens1_c",
    "lens2_c", 
    "lens3_c", 
    "lens4_c",
    "lens5_c",
    "lens6_c",
    #"sms_lab",
    "hexapod",
    "tomo_c",
    "det2_c",
    # "lens7_c",
]

#fmt: on

import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

import sys, pathlib
sys.path.append(str(pathlib.Path.home() / "bluesky/instrument/devices"))
#sys.path.append("/home/beams/S1IDTEST/bluesky/instrument/devices")
from .generic_motors import * #generic_motors.py MUST be in devices folder

from ophyd import Component, Device, EpicsMotor
from hkl import E4CV, SimMixin

""" 
"""

class ICC(Device):
    y = Component(MPEMotor, "s1amci1:m6", kind = "hinted")    

# ic_us_c = ICC("", name = "ic_us_c")


class FourCTable(Device):
    x  = Component(MPEMotor, "1idc:m76")
    y1 = Component(MPEMotor, "s1amci1:m1")
    y2 = Component(MPEMotor, "s1amci1:m2")
    y3 = Component(MPEMotor, "s1amci1:m3")
    z1 = Component(MPEMotor, "s1amci1:m4")
    z2 = Component(MPEMotor, "s1amci1:m5")

# fourc_table = FourCTable("", name = "fourc_table")


class FourC(SimMixin, E4CV):    
   th  = Component(MPEMotor, "m74", kind = "hinted")
   tth = Component(MPEMotor, "m85", kind = "hinted")
   chi = Component(MPEMotor, "m88", kind = "hinted")
   phi = Component(MPEMotor, "m75", kind = "hinted")
   
fourc = FourC("1idc:", name = "fourc")


class FourCSample(Device):   
   x = Component(MPEMotor, "m39", kind = "hinted")
   z = Component(MPEMotor, "m40", kind = "hinted")

fourc_sample = FourCSample("1idc:", name = "fourc_sample")


class AttenuatorInC(Device):
    rotz = Component(MPEMotor, "m82")

atten_c = AttenuatorInC("1idc:", name = "attenuator_c")


lens1_c = Generic6DOFDevice("1idc:", name = "lens1_c",
    xpv = "m99",    ypv = "m100",    zpv = "m101", 
    rotxpv = "m102", rotypv = "m103", rotzpv = "m104")

lens2_c = Generic6DOFDevice("1idc:", name = "lens2_c",
    xpv = "m65",    ypv = "m66",    zpv = "m67", 
    rotxpv = "m68", rotypv = "m69", rotzpv = "m70")

#mobile IOC
lens3_c = Generic6DOFDevice("1idfoc:", name = "lens3_c",
    xpv = "m13",    ypv = "m14",    zpv = "m15", 
    rotxpv = "m16", rotypv = "m17", rotzpv = "m18")

#mobile IOC
lens4_c = Generic6DOFDevice("1idfoc:", name = "lens4_c",
    xpv = "m19",    ypv = "m20",    zpv = "m21", 
    rotxpv = "m22",     rotypv = "m23", rotzpv = "m24")

#mobile IOC
lens5_c = Generic6DOFDevice("1idfoc:", name = "lens5_c",
    xpv = "m1",    ypv = "m2",    zpv = "m3", 
    rotxpv = "m4",     rotypv = "m5", rotzpv = "m6")

#mobile IOC
lens6_c = Generic6DOFDevice("1idfoc:", name = "lens6_c",
    xpv = "m7",    ypv = "m8",    zpv = "m9", 
    rotxpv = "m10",     rotypv = "m11", rotzpv = "m12")


class SMSLabView(Device):
    """Top set for new Kohzu motors."""
    x    = Component(MPEMotor, "1idc:m25")
    y    = Component(MPEMotor, "1idc:m26")
    z    = Component(MPEMotor, "1idc:m27")
    rotx = Component(MPEMotor, "1idc:m28")
    # #roty = 
    rotz = Component(MPEMotor, "1idc:m29")    
    x2   = Component(MPEMotor, "1idc:m31")

    
# sms_lab = SMSLabView("", name = "sms_lab")


class Hexapod(Device):
    x = Component(MPEMotor, "1idc:m83")
    
hexapod = Hexapod("", name = "hexapod")


class TomoC(Device):
    x = Component(MPEMotor, "1idc:m79")
    y = Component(MPEMotor, "1idc:m84")
    z = Component(MPEMotor, "1idc:m77") 
    
tomo_c = TomoC("", name = "tomo_c")


class Det2C(Device):
    x = Component(MPEMotor, "1idc:m47")
    # y = Component(MPEMotor, "s1amci2:m1") 
    # z = Component(MPEMotor, "s1amci2:m2")
    #unclear if we will have a motorized beamstop; likely 2-phase
    # beamstop_x = Component(MPEMotor, "1idc:m35")
    # beamstop_y = Component(MPEMotor, "1idc:m34")
    
det2_c = Det2C("", name = "det2_c")

class Lens7C(Device):
    x    = Component(MPEMotor, "m42")
    y    = Component(MPEMotor, "m43")
    z    = Component(MPEMotor, "m45")
    rotx = Component(MPEMotor, "m41")
    roty = Component(MPEMotor, "m44")

lens7_c = Lens7C("1idc:", name = "lens7_c")





