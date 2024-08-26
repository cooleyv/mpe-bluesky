"""
Uses `make_det()` from .ad_make_dets module to create POINT GREY device. 
Selects plugin versions based on version of ADCore the IOC is using.

`make_det()` requires detector-specific inputs, which are contained here. 
These include:
    - blueprint for cam class specific to the POINT GREY detector
    - `default_plugin_control` dictionary, which enables/disables 
        plugins in default setup
    - detector-specific Mixin class, which contains methods and 
        extra attributes specific to POINT GREY. These include
        configuration for fastsweep. 

`make_det()` returns a detector object to control POINT GREY. 

TODO: When AD is updated for 1-ID-C and old 1-ID-E cameras, update here. 
TODO: fastsweep_config needs to be redone for new aravis PVs/ new model

FIXME: cam.acquire_period is not writable

"""


__all__ = [
    "grasshopper1",
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
from bluesky import plan_stubs as bps

#define paths
LINUX_ROOT = "/home/beams/S1IDUSER/mnt/s1c"  #Path root for both bluesky and detectors on linux
IMAGE_DIR = "mpe_apr24/pointgrey/"  #TODO: pull this specifically from iconfig!!

#define blueprint for making POINT GREY cam class
def make_pointgrey_cam(Det_CamBase):   
     
    class PointGrey_CamPlugin(Det_CamBase): 
        """Make a custom Point Grey cam class to capture all of the ADaravis v3.12.1 PVs.
        Instead of using PointGreyDetectorCam from ophyd, need to make from base class.
        (PointGreyDetectorCam contains different PV names.)"""
        
        pixel_format = ADComponent(EpicsSignalWithRBV, "PixelFormat")
        frame_rate = ADComponent(EpicsSignalWithRBV, "FrameRate")
        read_status = ADComponent(EpicsSignal, "ReadStatus")
        trigger_source = ADComponent(EpicsSignalWithRBV, "TriggerSource")
        trigger_overlap = ADComponent(EpicsSignal, "TriggerOverlap")
        exposure_mode = ADComponent(EpicsSignal, "ExposureMode")
        empty_free_list = ADComponent(EpicsSignal, "EmptyFreeList")
        exposure_auto = ADComponent(EpicsSignal, "ExposureAuto")
        frame_rate_enable = ADComponent(EpicsSignal, "FrameRateEnable")
        wait_for_plugins = ADComponent(EpicsSignal, "WaitForPlugins")
        num_queued_arrays = ADComponent(EpicsSignalRO, "NumQueuedArrays")
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
        convert_pixel_format = ADComponent(EpicsSignalWithRBV, "ARConvertPixelFormat")
        shift_dir = ADComponent(EpicsSignalWithRBV, "ARShiftDir")
        shift_bits = ADComponent(EpicsSignalWithRBV, "ARShiftBits")

    return PointGrey_CamPlugin

#define default plugin config
pointgrey_plugin_control = {
    "use_image1" : True,
    "use_pva1" : True,
    "use_proc1" : False,
    "use_trans1" : False,
    "use_over1" : False, 
    "use_roi1" : False, 
    "use_tiff1" : True, 
    "use_hdf1" : False, 
    "ndport_image1" : "ARV1",
    "ndport_pva1" : "ARV1",
    "ndport_proc1" : "",
    "ndport_trans1" : "",
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "ARV1",
    "ndport_hdf1" : ""
}

#define POINT GREY Mixin class for extra attributes/methods
class PointGreyMixin(object):
    
    def fastsweep_config(self, nframes):
        print("More development is needed to add fastsweep config to POINT GREY")


    def default_setup(self):
        """ 
        Method for restoring default plugin settings specific 
        to POINT GREY. 
        
        Useful for resetting POINT GREY detector. 
        
        NOTE: Defaults are set for ARAVIS v3.12.1 PVs; 
        does not match with defaults set in `ccd_ad_PointGrey.mac`
        
        Usage: `POINTGREYDET.default_setup()`
        """
        
        #default settings for cam plugin
        yield from bps.mv(
            self.cam.num_images, 1,
            self.cam.num_exposures, 1, 
            self.cam.trigger_mode, "Off",
            self.cam.trigger_source, "Software",
            self.cam.exposure_auto, "Off",
            self.cam.gain_auto, "Off",
            self.cam.gain, 1.0, 
            self.cam.bin_x, 1, 
            self.cam.bin_y, 1,
            self.cam.pixel_format, "Mono16",
            self.cam.convert_pixel_format, "Mono16Low",
            self.cam.acquire_time, 0.01,
            #self.cam.acquire_period, 0.05, #FIXME: Not writeable in EPICS       
            self.cam.min_x, 0, 
            self.cam.min_y, 0
        )
        
        #sizes are dependent on model
        model_id = self.cam.model.get()
        if model_id.endswith('123S6M'):
            yield from bps.mv(
                self.cam.size.size_x, 4096,
                self.cam.size.size_y, 3000
            )
        else:
            yield from bps.mv(
                self.cam.size.size_x, 1920,
                self.cam.size.size_y, 1200
            )


#create POINT GREY objects
grasshopper1 = make_det(
    det_prefix = "1idGH1:",
    device_name = "grasshopper1",
    local_drive = "",
    image_dir = "mpe_apr24/pointgrey/",
    make_cam_plugin = make_pointgrey_cam,
    default_plugin_control = pointgrey_plugin_control,
    det_mixin = PointGreyMixin,
    ioc_WIN = False,
    pva1_exists = True
)

pg5 = make_det(
    det_prefix = "1idPG5:",
    device_name = "pg5",
    local_drive = "",
    image_dir = "/home/beams/S1IDUSER/mpe_apr24/pointgrey/",
    make_cam_plugin = make_pointgrey_cam,
    default_plugin_control = pointgrey_plugin_control,
    det_mixin = PointGreyMixin,
    ioc_WIN = False,
    pva1_exists = True
)

