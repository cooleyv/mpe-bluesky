""" 
Slits for the 1-ID beamline. 

#TODO: Need to configure C-hutch Kohzu slit hardware with db names to put here. 
#FIXME: Determine if C hutch slits need x and y translation stages.
"""


#fmt: off

__all__ = [
    "slits_b",
    # "slits_c_us",
    "slits_c_ds",
    "slits_e_us",
    "slits_e_ds",
]
#fmt:off

import logging 
logger = logging.getLogger(__name__)
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor
from apstools.devices import PVPositionerSoftDone
from apstools.synApps import Optics2Slit2D_InbOutBotTop
from .generic_motors import * #generic_motors.py MUST be in devices folder

"""Slit classes below."""
#FIXME: Not sure that the setpoint and readback PVs are correct. 
class MPE4Slits(Optics2Slit2D_InbOutBotTop):
    """Generic 4-slit device for multiple hutches here.
    Subclass is used to rename horizontal blades to 'ib' and 'ob'."""
    ib = Component(PVPositionerSoftDone, "H", setpoint_pv = "xn", readback_pv = "t2.A")
    ob = Component(PVPositionerSoftDone, "H", setpoint_pv = "xp", readback_pv = "t2.B")
    
    #Remove old names from the parent class
    inb = None
    out = None

#FIXME: Need to configure Kohzu slits with PV name. Subclass created to include x and y translation. 
# class CHutchKohzuUS(Device):
#     """Custom subclass for US Kohzu slits to add in translation motors."""
#     x = Component(MPEMotor, "m85")
#     y = Component(MPEMotor, "m88")
#     top = Component(PVPositionerSoftDone, "Kohzu_C_upV", setpoint_pv = "xp", readback_pv = "")
#     bot = Component(PVPositionerSoftDone, "Kohzu_C_upV", setpoint_pv = "xn", readback_pv = "")
#     ib =  Component(PVPositionerSoftDone, "Kohzu_C_H", setpoint_pv = "xn", readback_pv = "")
#     ob =  Component(PVPositionerSoftDone, "Kohzu_C_upH", setpoint_pv = "xp", readback_pv = "")
    
    
class BHutchSlits(Device):
    #B-hutch slits only use two motors, will configure as two motor-components
    blade1 = Component(MPEMotor, "m61")
    blade2 = Component(MPEMotor, "m58")
    
"""Generating devices for export below."""
slits_b    = BHutchSlits("1idb:", name= "slits_b")
#slits_c_us = MPE4Slits("1idc:", )
slits_c_ds = MPE4Slits("1idc:Kohzu", name = "slits_c_ds")
slits_e_us = MPE4Slits("1ide1:Kohzu_E_up", name = "slits_e_us")
slits_e_ds = MPE4Slits("1ide1:Kohzu_E_dn", name = "slits_e_ds")