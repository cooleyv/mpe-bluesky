"""
Contains motor devices defining 1-ID-B portion of instrument

#TODO: Populate with motors. 

"""


#fmt: off

__all__ = [

]

#fmt: on

import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor
from generic_motors import * #generic_motors.py MUST be in devices folder


class FastShutterB(Device):
    x = Component(MPEMotor, "m27")
    y = Component(MPEMotor, "m28")
    
fast_shutter_b = FastShutterB("1idb:", name = "fast_shutter_b")


class AttenuatorB(Device):
    #Motors here are from autodesktop but do not match .DESC        
    #atten_1 = Component(MPEMotor, "1idb:m24")   #"L4B Th (Rx)" 
    #atten_2 = Component(MPEMotor, "1idc:m16")
    #foil    = Component(MPEMotor, "1idb:m55")   #"old foil wheel"

    #Motors here are chosen based on .DESC
    #FIXME: check that these are correct
    wheel   = Component(MPEMotor, "m50")    #Check location of this motor- is it in b?
    foil    = Component(MPEMotor, "m18")
    
    

    
    