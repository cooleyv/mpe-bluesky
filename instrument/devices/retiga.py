""" 
Uses `make_det()` from .ad_make_dets module to create RETIGA device. 
Selects plugin versions based on version of ADCore the IOC is using.

`make_det()` requires detector-specific inputs, which are contained here. 
These include:
    - blueprint for cam class specific to the RETIGA detector
    - `default_plugin_control` dictionary, which enables/disables 
        plugins in default setup
    - detector-specific Mixin class, which contains methods and 
        extra attributes specific to RETIGA. These include
        configuration for fastsweep. 

`make_det()` returns a detector object to control RETIGA. 

NOTE: 2024-05-21 VC: Descoped TIFF1 save functionality (outdated ADcore, WIN write path issues)
TODO: Maybe fix TIFF1 functionality??
TODO: Add Retiga NF when the IOC is restarted. 
"""

__all__ = [
    "retiga_tomo",
]

#import for logging
import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#import mod components from ophyd
from ophyd import ADComponent
from ophyd import EpicsSignal
from ophyd import EpicsSignalWithRBV
from ophyd import EpicsSignalRO

#import plugin and det blueprints 
from .ad_plugin_classes import *
from .ad_make_dets import *

#import other stuff
import os
#from .. import iconfig 
from bluesky import plan_stubs as bps
from .s1id_FPGAs import det_pulse_to_ad
from .s1id_FPGAs import time_counter



#define blueprint for making RETIGA cam class
def make_retiga_cam(Det_CamBase):

    class Retiga_CamPlugin(Det_CamBase):   
        """Make a custom Retiga cam class.
        Need to make from base, then add PVs not included."""
        gain_max = ADComponent(EpicsSignalRO, "GainMax_RBV")
        gain_mix = ADComponent(EpicsSignalRO, "GainMin_RBV")
        abs_offset = ADComponent(EpicsSignal, "qOffset")
        image_format = ADComponent(EpicsSignalWithRBV, "qImageFormat")
        readout_speed = ADComponent(EpicsSignalWithRBV, "qReadoutSpeed")
        cooler_active = ADComponent(EpicsSignal, "qCoolerActive")
        auto_exposure = ADComponent(EpicsSignal, "qAutoExposure")
        exposure_max = ADComponent(EpicsSignalRO, "ExposureMax_RBV")
        exposure_min = ADComponent(EpicsSignalRO, "ExposureMin_RBV")
        
    return Retiga_CamPlugin

#define default plugin config
retiga_plugin_control = {
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
    "ndport_trans1" : "RETIGA",
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "TRANS1",
    "ndport_hdf1" : ""
}

#define RETIGA Mixin class for extra attributes/methods
class RetigaMixin(object): 
    
    def fastsweep_config(self, nframes):
        
        print("WARNING! Retiga is only set up to collect with TIFF plugin.")
        
        
        #Set up RETIGA triggering tool, which is unique to det
        #uses attrs of det_pulse_to_ad object no other det uses
        
        #define string values used below
        in_link_a_value = "1id:9440:1:bi_0.VAL CP NMS"
        out_link_value = self.cam.prefix + "Acquire PP NMS"
        
        #sends det pulse to acromag and AD start button
        yield from bps.mv(
            det_pulse_to_ad.description, "DetPulseToAD",
            det_pulse_to_ad.scan, "Passive",
            det_pulse_to_ad.a_value, 0,
            det_pulse_to_ad.in_link_a, in_link_a_value,
            det_pulse_to_ad.in_link_b, "",
            det_pulse_to_ad.b_value, 0,
            det_pulse_to_ad.c_value, 0,
            det_pulse_to_ad.aa_value, "Acquire",
            det_pulse_to_ad.bb_value, "NOP",
            det_pulse_to_ad.calc_record, "(A&B)&C",
            det_pulse_to_ad.out_calc, "AA",
            det_pulse_to_ad.out_execute_option, "Transition To Non-zero",
            det_pulse_to_ad.out_data_option, "Use OCAL",
            det_pulse_to_ad.out_link, out_link_value, 
            det_pulse_to_ad.wait, "NoWait"
        )
        
        #specific to aero with PSO control below 
        #configure plugin stage_sigs implemented in `fastweep()`
        
        self.tiff1.stage_sigs["file_write_mode"] = "Stream"
        self.tiff1.stage_sigs["num_capture"] = nframes
        self.tiff1.capture.stage_sigs["capture"] = "Capture"
        
        self.cam.stage_sigs["image_mode"] = "Multiple"
        self.cam.stage_sigs["trigger_mode"] = "StrobeHi"
        self.cam.stage_sigs["num_exposures"] = nframes
        
        
        
    def default_setup(self):
        """
        Method for restoring default plugin 
        settings specific to RETIGA
        
        Useful for resetting RETIGA detector. 
        
        Usage: `RETIGA_DET.default_setup()`
        """
        
        #default settings for cam plugin
        yield from bps.mv(
            self.cam.trigger_mode, "Software",
            self.cam.readout_speed, "20 Mhz",
            self.cam.image_format, "Mono 16",
            self.cam.cooler_active, "On", 
            self.cam.acquire_time, 1.0, 
            self.cam.acquire_period, 0,
            self.cam.gain, 1.0,
            self.cam.abs_offset, 0,
            self.cam.temperature, -45.0,
            self.cam.min_x, 0,
            self.cam.min_y, 0, 
            self.cam.size.size_x, 2048, 
            self.cam.size.size_y, 2048, 
            self.cam.reverse.reverse_x, "No", 
            self.cam.reverse.reverse_y, "No",
            self.cam.array_callbacks, "Enable",
            self.cam.image_mode, "Single"
        )
        
        #default settings for tiff1 plugin
        yield from bps.mv(
            self.tiff1.auto_increment, "Yes",
            self.tiff1.file_write_mode, "Single",
            self.tiff1.auto_save, "Yes"
        )
        
        

#create RETIGA object
retiga_tomo = make_det(
    det_prefix = "QIMAGE2:",
    device_name = "retiga_tomo",
    local_drive = "D:",
    image_dir = "",
    make_cam_plugin = make_retiga_cam,
    default_plugin_control = retiga_plugin_control,
    det_mixin = RetigaMixin,
    ioc_WIN = True, 
    pva1_exists = False
)
