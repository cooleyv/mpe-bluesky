"""
Uses `make_det()` from .ad_make_dets module to create FLIR ORYX device. 
Selects plugin versions based on version of ADCore the IOC is using.

`make_det()` requires detector-specific inputs, which are contained here. 
These include:
    - blueprint for cam class specific to the FLIR ORYX detector
    - `default_plugin_control` dictionary, which enables/disables 
        plugins in default setup
    - detector-specific Mixin class, which contains methods and 
        extra attributes specific to FLIR ORYX. These include
        configuration for fastsweep. 

`make_det()` returns a detector object to control FLIR ORYX. 

Note: Cannot connect to this device as-is while logged into a 1-ID controls 
computer since the device machine runs on 20-ID subnet, not 1-ID. 

FIXME: fix file read/write paths
FIXME: add xml file paths as needed
TODO: add prefix for 1-ID camera when it arrives.

"""

__all__ = [
    "oryx20idd",
]

#import for logging
import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#import plugin and det blueprints 
from .ad_plugin_classes import *
from .ad_make_dets import *

#import mod components from ophyd
from ophyd import DetectorBase
from ophyd import SingleTrigger 
from ophyd import ADComponent
from ophyd import EpicsSignal
from ophyd import EpicsSignalWithRBV
from ophyd import EpicsSignalRO

#import other stuff
import os
#from .. import iconfig 
from bluesky import plan_stubs as bps
from .. import iconfig

#pick which beamline we are operating at 
beamline = iconfig["RUNENGINE_METADATA"]["beamline_id"]

#define global variables from the iconfig file
PI_FOLDER = iconfig["EXPERIMENT"]["PI_FOLDER"]

WRITE_PATH = {
    "oryx20idd" : '/scratch/tmp/' + PI_FOLDER + '/',
}

READ_PATH = {
    "oryx20idd" : '/home/beams/S20HEDM/mnt/',   #FIXME
}

#define xml files for the HDF writer
DEFAULT_XML_LAYOUT = {
    "oryx20idd" : "",
}

DEFAULT_XML_ATTRIBUTE = {
    "oryx20idd" : "",
}

#define blueprint for making FLIR ORYX cam class
def make_oryx_cam(Det_CamBase):
    
    class Oryx_CamPlugin(Det_CamBase): 
        """Add attributes used by oryx but not included in cam_base."""
        trigger_source = ADComponent(EpicsSignalWithRBV, "TriggerSource")
        trigger_overlap = ADComponent(EpicsSignalWithRBV, "TriggerOverlap")
        exposure_mode = ADComponent(EpicsSignalWithRBV, "ExposureMode")
        trigger_software = ADComponent(EpicsSignal, "TriggerSoftware")
        empty_free_list = ADComponent(EpicsSignal, "EmptyFreeList")
        exposue_auto = ADComponent(EpicsSignalWithRBV, "ExposureAuto")
        frame_rate = ADComponent(EpicsSignalWithRBV, "FrameRate")
        frame_rate_enable = ADComponent(EpicsSignalWithRBV, "FrameRateEnable")
        num_queued_arrays = ADComponent(EpicsSignalRO, "NumQueuedArrays")
        wait_for_plugins = ADComponent(EpicsSignal, "WaitForPlugins")
        acquire_busy = ADComponent(EpicsSignalRO, "AcquireBusy")
        frames_completed = ADComponent(EpicsSignalRO, "ARFramesCompleted")
        frame_failures = ADComponent(EpicsSignalRO, "ARFrameFailures")
        frame_underruns = ADComponent(EpicsSignalRO, "ARFrameUnderruns")
        missing_packets = ADComponent(EpicsSignalRO, "ARMissingPackets")
        resent_packets = ADComponent(EpicsSignalRO, "ARResentPackets")
        packet_resend_enable = ADComponent(EpicsSignal, "ARPacketResendEnable")
        packet_timeout = ADComponent(EpicsSignal, "ARPacketTimeout")
        frame_retention = ADComponent(EpicsSignal, "ARFrameRetention")
        reset_camera = ADComponent(EpicsSignal, "ARResetCamera")
        gain_auto = ADComponent(EpicsSignalWithRBV, "GainAuto")
        pixel_format = ADComponent(EpicsSignalWithRBV, "PixelFormat")
        convert_pixel_format = ADComponent(EpicsSignalWithRBV, "ARConvertPixelFormat")
        shift_dir = ADComponent(EpicsSignalWithRBV, "ARShiftDir")
        shift_bits = ADComponent(EpicsSignalWithRBV, "ARShiftBits")

    return Oryx_CamPlugin


#define default plugin config
oryx20idd_plugin_control = {
    "use_image1" : True,
    "use_pva1" : True,
    "use_proc1" : False,
    "use_trans1" : False,
    "use_over1" : False, 
    "use_roi1" : False, 
    "use_tiff1" : False, 
    "use_hdf1" : True, 
    "ndport_image1" : "ARV1",
    "ndport_pva1" : "ARV1",
    "ndport_proc1" : "",
    "ndport_trans1" : "",
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "ARV1",
    "ndport_hdf1" : "ARV1"
}

#define ORYX Mixin class for extra attributes/methods
class OryxMixin(object):
    
    def default_config(self):
        print("Development is needed to configure oryx for default setup.")
    
    def fastsweep_config(self):
        print("Development is needed to configure oryx for fastsweep.")
        
    def fastsweep_dark_config(self, ndarks):
        print("Development is needed to configure oryx for fastsweep.")
        
    def fastsweep_data_config(self, nframes, images_per_frame = 1):
        print("Development is needed to configure oryx for fastsweep.")


        
if "20-ID" in beamline:    

    #create ORYX object
    oryx20idd = make_det(
        det_prefix = "20iddOR1:",
        device_name = "oryx20idd",
        READ_PATH = READ_PATH["oryx20idd"],
        WRITE_PATH = WRITE_PATH["oryx20idd"],
        make_cam_plugin = make_oryx_cam,
        default_plugin_control = oryx20idd_plugin_control,
        det_mixin = OryxMixin,
        ioc_WIN = False,
        pva1_exists = True,
        use_tiff1 = True,
        use_hdf1 = True
    )