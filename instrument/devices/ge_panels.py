""" 
Uses `make_det()` from .ad_make_dets module to create GE device. 
Selects plugin versions based on version of ADCore the IOC is using.

`make_det()` requires detector-specific inputs, which are contained here. 
These include:
    - blueprint for cam class specific to the GE detector
    - `default_plugin_control` dictionary, which enables/disables 
        plugins in default setup
    - detector-specific Mixin class, which contains methods and 
        extra attributes specific to GE. These include
        configuration for fastsweep. 

`make_det()` returns a detector object to control GE panel. 


TODO: Confirm local drives for each panel
TODO: Do we need EDF1 plugin for each panel??
    - need to set min header to 8192
    - need to change create dir depth to -1
"""

__all__ = [
    "ge1",
    "ge2",
    "ge3",
    "ge4",
    "ge5"
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
from .. import iconfig

#pick which beamline we are operating at 
beamline = iconfig["RUNENGINE_METADATA"]["beamline_id"]

#define global variables for file saving 
PI_FOLDER = iconfig["EXPERIMENT"]["PI_FOLDER"]

WRITE_PATH = {
    "ge1" : "G:\\" + PI_FOLDER + "\\",
    "ge2" : "C:\\" + PI_FOLDER + "\\",
    "ge3" : "G:\\" + PI_FOLDER + "\\",
    "ge4" : "C:\\" + PI_FOLDER + "\\",
    "ge5" : "V:\\" + PI_FOLDER + "\\",
}

READ_PATH = {
    "ge1" : "/home/beams/S1IDUSER/mnt/s1c/" + PI_FOLDER + "/ge1/",
    "ge2" : "/home/beams/S1IDUSER/mnt/s1c/" + PI_FOLDER + "/ge2/",
    "ge3" : "/home/beams/S1IDUSER/mnt/s1c/" + PI_FOLDER + "/ge3/",
    "ge4" : "/home/beams/S1IDUSER/mnt/s1c/" + PI_FOLDER + "/ge4/",
    "ge5" : "/home/beams/S1IDUSER/mnt/s1c/" + PI_FOLDER + "/ge5/",
}


#define xml files for HDF writing (for now)
#FIXME: need separate files for separate dets
DEFAULT_XML_LAYOUT = {
    "ge1" : "/home/beams/S1IDUSER/mnt/s1b/bluesky_dev/hdf5_layout/GE3_layout.xml",
    "ge2" : "/home/beams/S1IDUSER/mnt/s1b/bluesky_dev/hdf5_layout/GE3_layout.xml",
    "ge3" : "/home/beams/S1IDUSER/mnt/s1b/bluesky_dev/hdf5_layout/GE3_layout.xml",
    "ge4" : "/home/beams/S1IDUSER/mnt/s1b/bluesky_dev/hdf5_layout/GE3_layout.xml",
    "ge5" : "/home/beams/S1IDUSER/mnt/s1b/bluesky_dev/hdf5_layout/GE3_layout.xml",
}

DEFAULT_XML_ATTRIBUTE = {
    "ge1" : "/home/beams/S1IDUSER/mnt/s1b/bluesky_dev/hdf5_layout/GE3_attributes.xml",
    "ge2" : "/home/beams/S1IDUSER/mnt/s1b/bluesky_dev/hdf5_layout/GE3_attributes.xml",
    "ge3" : "/home/beams/S1IDUSER/mnt/s1b/bluesky_dev/hdf5_layout/GE3_attributes.xml",
    "ge4" : "/home/beams/S1IDUSER/mnt/s1b/bluesky_dev/hdf5_layout/GE3_attributes.xml",
    "ge5" : "/home/beams/S1IDUSER/mnt/s1b/bluesky_dev/hdf5_layout/GE3_attributes.xml",
}

#define blueprint for making GE cam class
def make_GE_cam(Det_CamBase): 
    
    class GE_CamPlugin(Det_CamBase):
        pool_used_mem_polling = ADComponent(EpicsSignal, "PoolUsedMem.SCAN")
        empty_free_list = ADComponent(EpicsSignal, "EmptyFreeList")

        #acquisition config
        frames_before_expose = ADComponent(EpicsSignalWithRBV, "FramesBeforeExpose")
        frames_after_expose = ADComponent(EpicsSignalWithRBV, "FramesAfterExpose")
        frames_to_skip_expose = ADComponent(EpicsSignalWithRBV, "FramesToSkipExpose")
        interval_between_frames = ADComponent(EpicsSignalWithRBV, "IntervalBetweenFrames")
        expose_time_delay = ADComponent(EpicsSignalWithRBV, "ExposeTimeDelayInMicrosecs")
        num_capture = ADComponent(EpicsSignalWithRBV, "NumCapture")

        #coff file config
        user_single_acquisition_coff_filename1 = ADComponent(EpicsSignal, "UserSingleAcquisitionCoffFileName1")
        user_multi_det_acquisition_coff_filename1 = ADComponent(EpicsSignal, "UserMultiDetAcquisitionCoffFileName1")
        buffer_size1 = ADComponent(EpicsSignalWithRBV, "BufferSize1")
        number_rows_user_seq1 = ADComponent(EpicsSignalWithRBV, "NumberOfRowsForUserSeq1")
        number_columns_user_seq1 = ADComponent(EpicsSignalWithRBV, "NumberOfColumnsForUserSeq1")
        wrap_mode1 = ADComponent(EpicsSignalWithRBV, "WrapMode1")

        #det config
        enable_stretch = ADComponent(EpicsSignalWithRBV, "EnableStretch")
        comp_stretch = ADComponent(EpicsSignalWithRBV, "CompStretch")
        arc_integrator = ADComponent(EpicsSignalWithRBV, "ARCIntegrator")
        comp_enable = ADComponent(EpicsSignalWithRBV, "CompEnable")
        row_enable = ADComponent(EpicsSignalWithRBV, "RowEnable")
        left_even_tristate = ADComponent(EpicsSignalWithRBV, "LeftEvenTristate")
        right_odd_tristate = ADComponent(EpicsSignalWithRBV, "RightOddTristate")
        bandwidth = ADComponent(EpicsSignalWithRBV, "Bandwidth")
        fov_select = ADComponent(EpicsSignalWithRBV, "FOVSelect")
        display_during_acquisition = ADComponent(EpicsSignalWithRBV, "DisplayDuringAcquisition")
        drc_column_sum = ADComponent(EpicsSignalWithRBV, "DRCColumnSum")
        v_common_select = ADComponent(EpicsSignalWithRBV, "VCommonSelect")
        mapping_during_acquisition = ADComponent(EpicsSignalWithRBV, "MappingDuringAcquisition")
        timing_mode = ADComponent(EpicsSignalWithRBV, "TimingMode")
        ramp_selection = ADComponent(EpicsSignalWithRBV, "RampSelection")
        dfn_autoscrub_on_off = ADComponent(EpicsSignalWithRBV, "DFNAutoScrubOnOff")
        sync_autoscrub_with_sys_acq = ADComponent(EpicsSignalWithRBV, "SyncAutoscrubWithSysAcq")
        test_mode_select = ADComponent(EpicsSignalWithRBV, "TestModeSelect")
        set_v_common1 = ADComponent(EpicsSignalWithRBV, "SetVCommon1")
        set_v_common2 = ADComponent(EpicsSignalWithRBV, "SetVCommon2")
        set_row_on_voltage = ADComponent(EpicsSignalWithRBV, "SetRowOnVoltage")
        set_row_off_voltage = ADComponent(EpicsSignalWithRBV, "SetRowOffVoltage")
        set_aref = ADComponent(EpicsSignalWithRBV, "SetAREF")
        set_aref_trim = ADComponent(EpicsSignalWithRBV, "SetAREFTrim")
        set_compensation_voltage = ADComponent(EpicsSignalWithRBV, "SetCompensationVoltage")
        set_spare_voltage_source = ADComponent(EpicsSignalWithRBV, "SetSpareVoltageSource")
        analog_test_source = ADComponent(EpicsSignalWithRBV, "AnalogTestSource")
        fiber_channel_timeout = ADComponent(EpicsSignalWithRBV, "FiberChannelTimeOutInMicrosecs")
        
    return GE_CamPlugin
        
#define default plugin config
ge1_plugin_control = {
    "use_image1" : True,
    "use_pva1" : False,
    "use_proc1" : False,
    "use_trans1" : False,
    "use_over1" : False, 
    "use_roi1" : False, 
    "use_tiff1" : True, 
    "use_hdf1" : False, 
    "ndport_image1" : "ANGIO",
    "ndport_pva1" : "",
    "ndport_proc1" : "",
    "ndport_trans1" : "",
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "ANGIO",
    "ndport_hdf1" : "ANGIO"
}

ge2_plugin_control = {
    "use_image1" : True,
    "use_pva1" : False,
    "use_proc1" : False,
    "use_trans1" : False,
    "use_over1" : False, 
    "use_roi1" : False, 
    "use_tiff1" : True, 
    "use_hdf1" : False, 
    "ndport_image1" : "ANGIO",
    "ndport_pva1" : "",
    "ndport_proc1" : "",
    "ndport_trans1" : "",
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "ANGIO",
    "ndport_hdf1" : "ANGIO"
}

ge3_plugin_control = {
    "use_image1" : True,
    "use_pva1" : False,
    "use_proc1" : False,
    "use_trans1" : False,
    "use_over1" : False, 
    "use_roi1" : False, 
    "use_tiff1" : True, 
    "use_hdf1" : False, 
    "ndport_image1" : "ANGIO",
    "ndport_pva1" : "",
    "ndport_proc1" : "",
    "ndport_trans1" : "",
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "ANGIO",
    "ndport_hdf1" : "ANGIO"
}

ge4_plugin_control = {
    "use_image1" : True,
    "use_pva1" : False,
    "use_proc1" : False,
    "use_trans1" : False,
    "use_over1" : False, 
    "use_roi1" : False, 
    "use_tiff1" : True, 
    "use_hdf1" : False, 
    "ndport_image1" : "ANGIO",
    "ndport_pva1" : "",
    "ndport_proc1" : "",
    "ndport_trans1" : "",
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "ANGIO",
    "ndport_hdf1" : "ANGIO"
}

ge5_plugin_control = {
    "use_image1" : True,
    "use_pva1" : False,
    "use_proc1" : False,
    "use_trans1" : False,
    "use_over1" : False, 
    "use_roi1" : False, 
    "use_tiff1" : True, 
    "use_hdf1" : False, 
    "ndport_image1" : "ANGIO",
    "ndport_pva1" : "",
    "ndport_proc1" : "",
    "ndport_trans1" : "",
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "ANGIO",
    "ndport_hdf1" : "ANGIO"
}

#define GE Mixin class for extra attributes/methods
class GEMixin(object):
    
    def fastsweep_config(
        self,
        exposure_time
    ):
        """Method for configuring panels during fastsweep."""
        
        yield from self.default_setup()

       
        


        
    def default_setup(self, initialize = True):
        """ 
        Method for restoring default plugin 
        settings specific to GE panels. 
        
        Useful for resetting detectors. 
        
        Usage: `ge1.default_setup()`
        """
        
        #default settings for cam plugin 
        yield from bps.mv(
            self.cam.acquire_time, 0.1,
            self.cam.num_images, 1,
            self.cam.num_capture, 1,
            self.cam.number_rows_user_seq1, 2048, 
            self.cam.number_columns_user_seq1, 2048,
            self.cam.array_callbacks, "Disable",
            self.cam.buffer_size, 20,
            self.cam.wrap_mode1, "Enabled"
        )
        
        #default settings for image1 plugin
        yield from bps.mv(
            self.image1.array_callbacks, "Enabled"
        )
        
        #default settings for tiff1 plugin
        yield from bps.mv(
            self.tiff1.auto_increment, "Yes",
            self.tiff1.array_callbacks, "Enable",
            self.tiff1.file_write_mode, "Stream",
            self.tiff1.auto_save, "Yes",
            self.tiff1.num_capture, 1
        )
        
        if initialize:
            """Initialize file writer after startup."""
            
            print(f"Initializing file writer for {self.name}.")
            yield from bps.trigger(self, wait = True)     
            
    def fastsweep_dark_config(
        self, 
        ndarks
    ):
        
        print("Development is needed for GE dark frames during fastsweep.")
        
        
        
    def fastsweep_data_config(
        self,
        nframes
    ):
        
        yield from bps.mv(
            self.cam.num_images, nframes
        )
       

if "1-ID" in beamline:       
       
    #create GE objects
    ge1 = make_det(
        det_prefix = "GE1:",
        device_name = "ge1",
        READ_PATH = READ_PATH["ge1"],
        WRITE_PATH = WRITE_PATH["ge1"],
        make_cam_plugin = make_GE_cam,
        default_plugin_control = ge1_plugin_control,
        det_mixin = GEMixin,
        ioc_WIN = True, 
        pva1_exists = True,
        use_hdf1 = True,
        use_tiff1 = False   #FIXME as needed
    )       

    ge2 = make_det(
        det_prefix = "GE2:",
        device_name = "ge2",
        READ_PATH = READ_PATH["ge2"],
        WRITE_PATH = WRITE_PATH["ge2"],
        make_cam_plugin = make_GE_cam,
        default_plugin_control = ge2_plugin_control,
        det_mixin = GEMixin,
        ioc_WIN = True, 
        pva1_exists = True,
        use_hdf1 = True,
        use_tiff1 = False
    )  

    ge3 = make_det(
        det_prefix = "GE3:",
        device_name = "ge3",
        READ_PATH = READ_PATH["ge3"],
        WRITE_PATH = WRITE_PATH["ge3"],
        make_cam_plugin = make_GE_cam,
        default_plugin_control = ge3_plugin_control,
        det_mixin = GEMixin,
        ioc_WIN = True, 
        pva1_exists = True,
        use_hdf1 = True,
        use_tiff1 = False
    )  

    ge4 = make_det(
        det_prefix = "GE4:",
        device_name = "ge4",
        READ_PATH = READ_PATH["ge4"],
        WRITE_PATH = WRITE_PATH["ge4"],
        make_cam_plugin = make_GE_cam,
        default_plugin_control = ge4_plugin_control,
        det_mixin = GEMixin,
        ioc_WIN = True, 
        pva1_exists = True,
        use_hdf1 = True, 
        use_tiff1 = False
    )  

    ge5 = make_det(
        det_prefix = "GE5:",
        device_name = "ge5",
        READ_PATH = READ_PATH["ge5"],
        WRITE_PATH = WRITE_PATH["ge5"],
        make_cam_plugin = make_GE_cam,
        default_plugin_control = ge5_plugin_control,
        det_mixin = GEMixin,
        ioc_WIN = True, 
        pva1_exists = True,
        use_hdf1 = True,
        use_tiff1 = False
    )  
     
