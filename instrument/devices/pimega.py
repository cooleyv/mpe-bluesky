""" 
Uses `make_det()` from .ad_make_dets module to create PIMEGA device. 
Selects plugin versions based on version of ADCore the IOC is using.

`make_det()` requires detector-specific inputs, which are contained here. 
These include:
    - blueprint for cam class specific to the PIMEGA detector
    - `default_plugin_control` dictionary, which enables/disables 
        plugins in default setup
    - detector-specific Mixin class, which contains methods and 
        extra attributes specific to PIMEGA. These include
        configuration for fastsweep. 

`make_det()` returns a detector object to control PIMEGA. 

"""

__all__ = [
    "pimega",
]

#import for logging
import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#import plugin and det blueprints 
from .ad_plugin_classes import *
from .ad_make_dets import *

#import mod components from ophyd
from ophyd import ADComponent
from ophyd import EpicsSignal
from ophyd import EpicsSignalWithRBV
from ophyd import EpicsSignalRO

#import other stuff
import bluesky.plan_stubs as bps
import pathlib
from .. import iconfig

#pick which beamline we are operating at 
beamline = iconfig["RUNENGINE_METADATA"]["beamline_id"]

#define global variables for file saving
PI_FOLDER = iconfig["EXPERIMENT"]["PI_FOLDER"]

WRITE_PATH = {
    "pimega" : "",
}

READ_PATH = {
    "pimega" : "",
}

#define global variables for HDF writing
DEFAULT_XML_LAYOUT = {
    "pimega" : "",
}

DEFAULT_XML_ATTRIBUTE = {
    "pimega" : "",
}


#define blueprint for making cam class
def make_pimega_cam(Det_CamBase):
    
    class Pimega_CamPlugin(Det_CamBase):
        
        """Special attributes go here."""
        
    return Pimega_CamPlugin

#define default plugin configs - separate for each det
pimega_plugin_control = {
    "use_image1" : False,
    "use_pva1" : True,
    "use_proc1" : True,
    "use_trans1" : True,
    "use_over1" : False, 
    "use_roi1" : False, 
    "use_tiff1" : True, 
    "use_hdf1" : True, 
    "ndport_image1" : "",
    "ndport_pva1" : "PROC1",
    "ndport_proc1" : "TRANS1",
    "ndport_trans1" : "",    #NOTE: port name is diff for diff dets
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "TRANS1",
    "ndport_hdf1" : "TRANS1"
}





#define pimega Mixin class for extra attributes/methods 
class PimegaMixin(object):
    
    
    def default_setup(self):
        
        """Default stuff goes here."""
    

    
    def fastsweep_config(
        self, 
        exposure_time,
        ):
        
        """Fastsweep general stuff goes here."""
        

    def fastsweep_dark_config(
        self,
        ndarks
      
    ):
        
        """Fastsweep dark frame stuff goes here."""

    def fastsweep_data_config(
        self,
        nframes,
        images_per_frame = 1
    ):
        
        """Fastsweep data collection stuff goes here."""


if "20-ID" in beamline: 
    
    pimega = make_det(
        det_prefix = "",    #FIXME: add prefix
        device_name = "pimega",
        READ_PATH = READ_PATH["pimega"],
        WRITE_PATH = WRITE_PATH["pimega"],
        make_cam_plugin = make_pimega_cam,
        default_plugin_control = pimega_plugin_control,
        det_mixin = PimegaMixin, 
        ioc_WIN = False, 
        pva1_exists = True,
        use_hdf1= True,
        use_tiff1 = True
    )    

    
