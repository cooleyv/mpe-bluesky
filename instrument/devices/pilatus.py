"""
Uses `make_det()` from .ad_make_dets module to create PILATUS device. 
Selects plugin versions based on version of ADCore the IOC is using.

`make_det()` requires detector-specific inputs, which are contained here. 
These include:
    - blueprint for cam class specific to the PILATUS detector
    - `default_plugin_control` dictionary, which enables/disables 
        plugins in default setup
    - detector-specific Mixin class, which contains methods and 
        extra attributes specific to PILATUS. These include
        configuration for fastsweep. 

`make_det()` returns a detector object to control PILATUS. 

#TODO: Fill in IOC names and other details when made available 
    by Tejas (not available as of 8/27/24 VC).
#TODO: Assumed pilatus runs on linux, might need Windows file paths. 

"""


__all__ = [
    "s1idPil",
    "s20idPil",
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

#define global variables for file writing 
PI_FOLDER = iconfig["EXPERIMENT"]["PI_FOLDER"]

WRITE_PATH = {
    "s1idPil" : "/local/" + PI_FOLDER + "/",
    "s20idPil" : "/local/" + PI_FOLDER + "/"
}
READ_PATH = {
    "s1idPil" : "/home/beams/S1IDUSER/mnt/" + PI_FOLDER + "/",
    "s20idPil" : "/home/beams/S20HEDM/mnt" + PI_FOLDER + "/", 
}

#define paths to xml files for HDF writer
DEFAULT_XML_LAYOUT = {
    "s1idPil" : "",
    "s20idPil" : "",
    }

DEFAULT_XML_ATTRIBUITE = {
    "s1idPil" : "",
    "s20idPil" : "",
    }


#define blueprint for making PILATUS cam class
def make_pilatus_cam(Det_CamBase):
    
    class Pilatus_CamPlugin(Det_CamBase):
        """Custom PVs for Pilatus go here."""
    
    return Pilatus_CamPlugin

#define plugin config   
#TODO- fill in as needed
s1idPil_plugin_control = {
    "use_image1" : False,
    "use_pva1" : False,     #FIXME as needed
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

s20idPil_plugin_control = {
    "use_image1" : False,
    "use_pva1" : False,     #FIXME as needed
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


#define PILATUS Mixin class for extra attributes/methods
#TODO - development
class PilatusMixin(object): 
    
    def default_config(self):
        print("Development is needed to configure oryx for default setup.")
    
    def fastsweep_config(self):
        print("Development is needed to configure oryx for fastsweep.")
        
    def fastsweep_dark_config(self, ndarks):
        print("Development is needed to configure oryx for fastsweep.")
        
    def fastsweep_data_config(self, nframes, images_per_frame = 1):
        print("Development is needed to configure oryx for fastsweep.")

if "1-ID" in beamline: 
    
    #create PILATUS object for 1-ID IOC
    s1idPil = make_det(
        det_prefix = "1idPil:",
        device_name = "s1idPil",
        READ_PATH = READ_PATH["s1idPil"],
        WRITE_PATH = WRITE_PATH["s20idPil"],
        make_cam_plugin = make_pilatus_cam, 
        default_plugin_control = s1idPil_plugin_control,
        det_mixin = PilatusMixin, 
        ioc_WIN = False, 
        pva1_exists = False,    #FIXME as needed 
        use_hdf1 = True, 
        use_tiff1 = True
    )

if "20-ID" in beamline:
    #create PILATUS object for 20-ID IOC
    s20idPil = make_det(
        det_prefix = "20idPil", 
        device_name = "s20idPil",
        READ_PATH = READ_PATH["s20idPil"],
        WRITE_PATH = WRITE_PATH["s20idPil"],
        make_cam_plugin = make_pilatus_cam, 
        default_plugin_control= s20idPil_plugin_control,
        det_mixin = PilatusMixin,
        ion_WIN = False, 
        pva1_exists = False,    #FIXME as needed
        use_hdf1 = True, 
        use_tiff1 = True
    )


