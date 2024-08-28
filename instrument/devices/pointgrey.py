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

TODO: Add/update methods for pointgrey1 windows IOC (vanilla AD)

FIXME: update read/write paths for different dets
FIXME: change plugin enabling/port names as well
FIXME: cam.acquire_period is not writable


NOTE: REQUIRED that detectors using a specific driver (vanilla or aravis)
    are the same version!!
"""


__all__ = [
    "grasshopper1",
    "pointgrey5",
    #"pointgrey5_win",  #comment out if not using
    #"pointgrey1",  #comment out if using Windows version 
    #"pointgrey1_win",
    "pointgrey4",   #FIXME: potentially renaming IOC
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
from ophyd.areadetector import PointGreyDetectorCam

#import other stuff
import os
from bluesky import plan_stubs as bps
from .. import iconfig

#pick which beamline we are operating at 
beamline = iconfig["RUNENGINE_METADATA"]["beamline_id"]

#define global variables for file saving
PI_FOLDER = iconfig["EXPERIMENT"]["PI_FOLDER"]

WRITE_PATH = {
    "grasshopper1" : "/home/beams/S1IDUSER/mnt/s1c/" + PI_FOLDER + "/",
    "pointgrey5" : "/tmp/" + PI_FOLDER + "/",
    "pointgrey5_win" : "",  #FIXME
    "pointgrey1" : "",  #FIXME
    "pointgrey1_win" : "V:\\" + PI_FOLDER + "\\",
    "pointgrey4" : "",   #FIXME
}

READ_PATH = {
    "grasshopper1" : "/home/beams/S1IDUSER/mnt/s1c/" + PI_FOLDER + "/",
    "pointgrey5" : "/home/beams/S1IDUSER/mnt/s1c/" + PI_FOLDER + "/",  #FIXME
    "pointgrey5_win" : "",
    "pointgrey1" : "/home/beams/S1IDUSER/mnt/s1c/" + PI_FOLDER + "/",
    "pointgrey1_win" : "/home/beams/S1IDUSER/mnt/s1c/" + PI_FOLDER + "/",
    "pointgrey4" : "",
}


#define default xml files for hdf writing (for now)
#FIXME
DEFAULT_XML_LAYOUT = {
    "grasshopper1" : "",
    "pointgrey5" : "",
    "pointgrey5_win" : "",
    "pointgrey1" : "",
    "pointgrey1_win" : "",
    "pointgrey4" : "",
}

#FIXME
DEFAULT_XML_ATTRIBUTE = {
    "grasshopper1" : "",
    "pointgrey5" : "", 
    "pointgrey5_win"
    "pointgrey1" : "", 
    "pointgrey1_win" : "",
    "pointgrey4" : "",
}



"""Point greys are special compared to other detectors because we have 
different drivers that haven't been unified yet. Therefore, there are 
both aravis and vanilla versions to make the cam class."""

#define blueprint for making POINT GREY cam class
def make_aravisPG_cam(Det_CamBase):   
     
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



def make_vanillaPG_cam(PointGreyDetectorCam):
    
    class PointGrey_CamPlugin(PointGrey_CamPlugin):
         """Make a vanilla Point Grey cam class using the ophyd-supported 
         class. (Contains different PVs than ADaravis)."""
         
         #TODO: custom attributes go here
         
    return PointGrey_CamPlugin



#define default plugin config
grasshopper1_plugin_control = {
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

pointgrey5_plugin_control = {
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

pointgrey5_win_plugin_control = {
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

pointgrey1_plugin_control = {
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

pointgrey1_win_plugin_control = {
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

pointgrey4_plugin_control = {
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
class PointGreyARVMixin(object):
    
    """PVs specific to ADaravis cam driver."""
    
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
             
    def fastsweep_config(self, exposure_time):
        print("More development is needed to add fastsweep config to pg.")

    def fastsweep_dark_config(self,ndarks):
        print("More development is needed to add fastsweep_dark_config to pg.")
        
    def fastsweep_data_config(self, nframes):
        print("More development is needed to add fastsweep_data_config to pg.")
        

class PointGreyVanillaMixin(object):
    
    """PVs specific to vanilla cam driver."""  
    
    def default_setup(self):
        """See `ccd_ad_PointGrey.mac` for more info."""
        print("More development is needed to add default_setup to pg.")
    
    def fastsweep_config(self, exposure_time):
        print("More development is needed to add fastsweep_config to pg.")
        
    def fastsweep_dark_config(self,ndarks):
        print("More development is needed to add fastsweep_dark_config to pg.")
        
    def fastsweep_data_config(self, nframes):
        print("More development is needed to add fastsweep_data_config to pg.")
    
if "1-ID" in beamline:    

    #create pointgrey objects on linux machine using ADaravis drivers
    grasshopper1 = make_det(
        det_prefix = "1idGH1:",
        device_name = "grasshopper1",
        READ_PATH = READ_PATH["grasshopper1"],
        WRITE_PATH = WRITE_PATH["grasshopper1"],
        make_cam_plugin = make_aravisPG_cam,
        default_plugin_control = grasshopper1_plugin_control,
        det_mixin = PointGreyARVMixin,
        ioc_WIN = False,
        pva1_exists = True,
        use_hdf1 = True,
        use_tiff1 = True
    )

    pointgrey5 = make_det(
        det_prefix = "1idPG5:",
        device_name = "pointgrey5",
        READ_PATH = READ_PATH["pointgrey5"],
        WRITE_PATH = WRITE_PATH["pointgrey5"],
        make_cam_plugin = make_aravisPG_cam,
        default_plugin_control = pointgrey5_plugin_control,
        det_mixin = PointGreyARVMixin,
        ioc_WIN = False,
        pva1_exists = True,
        use_hdf1 = True,
        use_tiff1 = True
    )

#     pointgrey1 = make_det(
#         det_prefix = "1idPG1:",
#         device_name = "pointgrey1",
#         READ_PATH = READ_PATH["pointgrey1"],
#         WRITE_PATH = WRITE_PATH["pointgrey1"],
#         make_cam_plugin = make_aravisPG_cam,
#         default_plugin_control = pointgrey1_plugin_control,
#         det_mixin = PointGreyARVMixin,
#         ioc_WIN = False,
#         pva1_exists = True,
#         use_hdf1 = True,
#         use_tiff1 = True
# )
    
    #create pointgrey objects on Windows machine using Vanilla AD driver
    # pointgrey5_win = make_det(
    #     det_prefix = "1idPG5:",
    #     device_name = "pointgrey5_win",
    #     READ_PATH = READ_PATH["pointgrey5_win"],
    #     WRITE_PATH= WRITE_PATH["pointgrey5_win"],
    #     make_cam_plugin = make_vanillaPG_cam,
    #     default_plugin_control = pointgrey5_win_plugin_control,
    #     det_mixin = PointGreyVanillaMixin,
    #     ioc_WIN = True,
    #     pva1_exists = False,    #FIXME as needed
    #     use_hdf1 = False,   #FIXME: as needed
    #     use_tiff1 = True
    # )

    # pointgrey1_win = make_det(
    #     det_prefix = "1idPG1:",
    #     device_name = "pointgrey1_win",
    #     READ_PATH = READ_PATH["pointgrey1_win"],
    #     WRITE_PATH= WRITE_PATH["pointgrey1_win"],
    #     make_cam_plugin = make_vanillaPG_cam,
    #     default_plugin_control = pointgrey1_win_plugin_control,
    #     det_mixin = PointGreyVanillaMixin,
    #     ioc_WIN = True,
    #     pva1_exists = False,    #FIXME as needed
    #     use_hdf1 = False,   #FIXME: as needed
    #     use_tiff1 = True
    # )


if "20-ID" in beamline:

    pointgrey4 = make_det(
        det_prefix = "1idPG4:",     #FIXME: used at 20ID, changing IOC name
        device_name = "pointgrey4",
        READ_PATH = READ_PATH["pointgrey4"],
        WRITE_PATH = WRITE_PATH["pointgrey4"],
        make_cam_plugin = make_aravisPG_cam,
        default_plugin_control = pointgrey4_plugin_control,
        det_mixin = PointGreyARVMixin,
        ioc_WIN = False,
        pva1_exists = True,
        use_hdf1 = True,
        use_tiff1 = True
    )




