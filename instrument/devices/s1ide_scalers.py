""" 
Contains scaler channels from ioc1ide.
"""

# fmt: off

__all__ = [
    "scaler1",
    "scaler3",
    "scaler2",
]

# fmt: on

import logging 
logger = logging.getLogger(__name__)
logger.info(__file__)

from ophyd.scaler import ScalerCH
from ophyd import Component, EpicsSignal

scaler1 = ScalerCH("1ide:S1:scaler1", name = "scaler1")
scaler3 = ScalerCH("1ide:S3:scaler3", name = "scaler3")

#make a special class for scaler2 in E hutch 
class EHutchScaler2(ScalerCH):
    normalized_counts = Component(EpicsSignal, "_calc_ctrl.VAL", kind = "config")
    enable_calcs = Component(EpicsSignal, "_calcEnable.VAL", kind = "config")

scaler2 = EHutchScaler2("1ide:S2:scaler2", name = "scaler2")

