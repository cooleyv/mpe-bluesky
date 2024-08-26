""" 
Uses `make_det()` from .ad_make_dets module to create PIXIRAD device. 
Selects plugin versions based on version of ADCore the IOC is using.

`make_det()` requires detector-specific inputs, which are contained here. 
These include:
    - blueprint for cam class specific to the PIXIRAD detector
    - `default_plugin_control` dictionary, which enables/disables 
        plugins in default setup
    - detector-specific Mixin class, which contains methods and 
        extra attributes specific to PIXIRAD. These include
        configuration for fastsweep. 

`make_det()` returns a detector object to control PIXIRAD. 

FIXME: Size is not set and max size is read-only (would like to set in `default_setup()`)
"""

__all__ = [
    "pixirad"
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
from ophyd import PixiradDetectorCam

#import other stuff
from .s1id_FPGAs import hem_info
import bluesky.plan_stubs as bps


#define blueprint for making PIXIRAD cam class
def make_pixirad_cam(Det_CamBase):
    class Pixirad_CamPlugin(Det_CamBase, PixiradDetectorCam): 
        count_mode = ADComponent(EpicsSignalWithRBV, "CountMode")
    
    return Pixirad_CamPlugin


#define default plugin config
pixirad_plugin_control = {
    "use_image1" : True,
    "use_pva1" : False,
    "use_proc1" : False,
    "use_trans1" : True,
    "use_over1" : False, 
    "use_roi1" : False, 
    "use_tiff1" : True, 
    "use_hdf1" : False, 
    "ndport_image1" : "TRANS1",
    "ndport_pva1" : "",
    "ndport_proc1" : "TRANS1",
    "ndport_trans1" : "PIXI",
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "TRANS1",
    "ndport_hdf1" : "TRANS1"
}

#define PIXIRAD Mixin class for extra attributes/methods
class PixiradMixin(object):

    def fastsweep_config(self, nframes):
        #unstage so that changes are permanent
        yield from bps.unstage(self)
        #set HV params
        
        #calculating thresholds -- used for fastsweep setting
        low_limit = hem_info.energy_keV.get()/2
        high_limit = hem_info.energy_keV.get()*1.5
        
        yield from bps.mv(
            self.cam.hv_mode, "Auto",
            self.cam.hv_state, "Off",
            self.cam.hv_value, 400,
            self.cam.temperature, -30
        )
        #set thresholds
        yield from bps.mv(
            self.cam.threshold_1, low_limit, 
            self.cam.threshold_2, high_limit, 
            self.cam.threshold_3, low_limit, 
            self.cam.threshold_4, high_limit
        )

        yield from bps.mv(self.cam.auto_calibrate, "Calibrate")

        yield from bps.mv(
            self.cam.sync_in_polarity, "Pos.",
            self.cam.sync_out_polarity, "Pos.",
            self.cam.sync_out_function, "Shutter",
            self.cam.frame_type, "1 color low"
        )
        
        #configure plugin stage_sigs implemented in `fastsweep()`
        self.cam.stage_sigs["num_images"] = nframes
        self.cam.stage_sigs["trigger_mode"] = "External"
        
        print("Pixirad is configured for fastsweep.")
        
    
    def default_setup(self):
        """
        Method for restoring default plugin
        settings specific to PIXIRAD. 
        
        Useful for resetting PIXIRAD detector.
        
        Usage: `pixirad.default_setup()`
        """  
        
        #default settings for cam plugin
        yield from bps.mv(
            self.cam.shutter_mode, "None",
            self.cam.shutter_open_delay, 0.00,
            self.cam.acquire_time, 1.0,
            self.cam.acquire_period, 1.0,
            self.cam.color_mode, "Mono",
            self.cam.frame_type, "1 color low",
            self.cam.trigger_mode, "Internal",
            self.cam.count_mode, "Normal",
            self.cam.min_x, 0, 
            self.cam.min_y, 0,
            # self.cam.max_size.max_size_x, 402,    #FIXME: these are read-only
            # self.cam.max_size.max_size_y, 1024    #FIXME: these are read-only
        )      
        
        #default settings for tiff1 plugin
        yield from bps.mv(
            self.tiff1.auto_increment, "Yes",
            self.tiff1.file_write_mode, "Single",
            self.tiff1.auto_save, "Yes",
            self.tiff1.create_directory, -3,
            self.tiff1.file_template, "%s%s_%6.6d.tiff",
            self.tiff1.lazy_open, "No",
            self.tiff1.temp_suffix, ""
        )
        
    def config_with_waxs(self, nframes):
        yield from bps.mv(

            #adjust cam plugin PVs
            self.cam.sync_out_function, "Shutter",
            self.cam_frame_type, "1 color low",
            self.cam.trigger_mode, "Bulb",  
            self.cam.trigger_mode, "External"
        )

        #override stage_sigs entered before
        self.cam.stage_sigs["num_images"] = nframes/4  
            
               
#create PIXIRAD object
pixirad = make_det(
    det_prefix = "s1_pixirad2:",
    device_name = "pixirad",
    local_drive = "",    #identical to controls path
    image_dir = "mpe_apr24/pixirad",
    make_cam_plugin = make_pixirad_cam,
    default_plugin_control = pixirad_plugin_control,
    det_mixin = PixiradMixin,
    ioc_WIN = False, 
    pva1_exists = False
)
