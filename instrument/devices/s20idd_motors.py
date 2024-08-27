"""Contains motor devices defining 20-ID-D portion of instrument. 

TODO: For now, only contains rotation motor for aerotech stage stack. 
Obviously need to add other motors...
"""

__all__ = [
    "aero_roty",
]

import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#import from ophyd
from .generic_motors import MPEMotor


aero_roty = MPEMotor("20idhedmA:m1", name = "aero_roty")

