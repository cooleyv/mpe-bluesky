"""
Consolidating FPGA channels into devices for fly scan support. 
Not exclusively FPGAs; some will have to move to other device documents, 
but these are all devices besides fly_motor and flyer needed for flyscan.

FIXME: adjust IOC prefixes as needed
"""

__all__ = [
    "softglue",
    #"c_shutter"
]

#import for logging
import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#import mod components from ophyd
from ophyd import DeviceStatus
from ophyd import Component
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsMotor
from ophyd import Device
from ophyd import Signal

#import other stuff
from bluesky import plan_stubs as bps
import time
from apstools.synApps import BusyRecord

class SoftGlue(Device):
    pso_signal_enable = Component(EpicsSignal, "AND-1_IN1_Signal")
    
softglue = SoftGlue("20iddMZ1:SG:", name = "softglue")

c_shutter = EpicsMotor("6idhedm:m7", name = "c_shutter")