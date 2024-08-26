""" 
Contains devices controlling 1-ID shutters.

# TODO: Check wait time for shutter open/close. 
# TODO: Fast shutter devices?

"""

#fmt:off
__all__ = [
    "shutter_a",
    "shutter_c", 
    #"fs_c",
]

#fmt: on

import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

from ophyd import EpicsMotor, Device, Component
from apstools.devices import EpicsOnOffShutter, ApsPssShutterWithStatus
from generic_motors import * #generic_motors.py MUST be in devices folder

shutter_a = ApsPssShutterWithStatus("1id:shutterA:", "PA:01ID:STA_A_FES_OPEN_PL", name = "shutter_a")


class FastShutterB(Device): ...
    #stuff goes here
    

shutter_c = ApsPssShutterWithStatus("1id:shutterC:", "PA:01ID:STA_C_SCS_OPEN_PL", name = "shutter_c")

#Removed this shutter from hutch design 05/03/24 VC
# class FastShutterC(Device):
#     """Adding x and y translation motors to fast shutter device."""
#     x = Component(MPEMotor, "1idc:m86", kind = "hinted")
#     y = Component(MPEMotor, "1idc:m87", kind = "hinted") 
#     shutter = Component(EpicsOnOffShutter, "1id:9440:1:bo_3")
    
# fs_c = FastShutterC("", name = "fs_c")


