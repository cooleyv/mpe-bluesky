"""
Devices specific to 1-ID only.
"""

# from ophyd.log import config_ophyd_logging
# config_ophyd_logging(level="DEBUG")
#     # 'ophyd' — the logger to which all ophyd log records propagate
#     # 'ophyd.objects' — logs records from all devices and signals (that is, OphydObject subclasses)
#     # 'ophyd.control_layer' — logs requests issued to the underlying control layer (e.g. pyepics, caproto)
#     # 'ophyd.event_dispatcher' — issues regular summaries of the backlog of updates from the control layer that are being processed on background threads

from .data_management import *

#import generic devices 
from .generic_motors import *
from .ad_plugin_classes import *
from .ad_make_dets import *
from .ad_make_dets import *

#import motor devices
from .s1idc_motors import *
from .s1ide_motors import *
#from .s1id_shutters import *
from .s1id_slits import *

#import soft devices
from .s1id_FPGAs import *
#from .pso_fly_device import *

#import measurement devices
# from .s1ide_scalers import *
# rom .flir_oryx import *   #currently only at 20-ID
from .ge_panels import *
from .retiga import *
from .pixiradv2 import *
from .pointgrey import grasshopper1, pointgrey5 #waiting for pointgrey1_win deployment
from .varex import s1varex1
from .pilatus import s1idPil      #waiting for deployment of IOC
# from .brillianse import *         #waitinf for deployment
# from .spectrumlogic import *      #waiting for deployment
# from .pimega import *     #waiting for deployment