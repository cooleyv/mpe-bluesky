""" 
Uses `make_det()` from .ad_make_dets module to create VAREX device. 
Selects plugin versions based on version of ADCore the IOC is using.

`make_det()` requires detector-specific inputs, which are contained here. 
These include:
    - blueprint for cam class specific to the VAREX detector
    - `default_plugin_control` dictionary, which enables/disables 
        plugins in default setup
    - detector-specific Mixin class, which contains methods and 
        extra attributes specific to VAREX. These include
        configuration for fastsweep. 

`make_det()` returns a detector object to control VAREX. 



FIXME: READ_PATH_STEM is exported for flyscan/bdp demo but won't 
    work when multiple detectors are used
    
FIXME: get XML file paths from iconfig when ready

TODO: add information for s1varex1
"""

__all__ = [
    "varex20idff",
    "s20varex2",
    "s1varex1",
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

#define global variables 
DEFAULT_XML_LAYOUT = {
    "varex20idff" : "M:\Varex_detector\Varex_layout.xml",
    "s20varex2" : "M:\\bluesky_dev\hdf5_layout\Varex_layout_20IDD.xml",
    "s1varex1" : "",
    }

DEFAULT_XML_ATTRIBUTE = {
    "varex20idff" : 'M:\Varex_detector\Varex_attributes.xml',
    "s20varex2" : "M:\\bluesky_dev\hdf5_layout\Varex_attributes_20IDD.xml",
    "s1varex1" : ""
    }

PI_FOLDER = iconfig["EXPERIMENT"]["PI_FOLDER"]

WRITE_PATH = {
    "varex20idff" : "M:\\" + PI_FOLDER + "\\",
    "s20varex2" : "V:\\" + PI_FOLDER + "\\",
    "s1varex1" : ""
}
READ_PATH = {
    "varex20idff" : "/net/s6iddata/export/hedm_sata/" + PI_FOLDER + "/",
    "s20varex2" : "" + PI_FOLDER + '/',
    "s1varex1" : "",
}


# WRITE_PATH = WRITE_PATH_STEM + PI_FOLDER + "\\"
# READ_PATH = READ_PATH_STEM + PI_FOLDER + '/'


#define blueprint for making VAREX cam class
def make_varex_cam(Det_CamBase):
    
    class Varex_CamPlugin(Det_CamBase):
        wait_for_plugins = ADComponent(EpicsSignal, "WaitForPlugins")
        #buffers
        empty_free_list = ADComponent(EpicsSignal, "EmptyFreeList")
        #corrections
        corrections_dir = ADComponent(EpicsSignal, "PECorrectionsDir")
        #offset
        num_offset_frames = ADComponent(EpicsSignal, "PENumOffsetFrames")
        offset_constant = ADComponent(EpicsSignalWithRBV, "PEOffsetConstant")
        acquire_offset = ADComponent(EpicsSignal, "PEAcquireOffset")    #might have RBV
        use_offset = ADComponent(EpicsSignal, "PEUseOffset")    #might have RBV
        #gain
        num_gain_frames = ADComponent(EpicsSignal, "PENumGainFrames")
        acquire_gain = ADComponent(EpicsSignal, "PEAcquireGain")
        use_gain = ADComponent(EpicsSignal, "PEUseGain")
        gain_file = ADComponent(EpicsSignal, "PEGainFile")
        load_gain_file = ADComponent(EpicsSignal, "PELoadGainFile")
        save_gain_file = ADComponent(EpicsSignal, "PESaveGainFile")
        #bad pixel file
        pixel_correction_file = ADComponent(EpicsSignal, "PEPixelCorrectionFile")
        use_pixel_correction = ADComponent(EpicsSignal, "PEUsePixelCorrection")
        load_pixel_correction = ADComponent(EpicsSignal, "PELoadPixelCorrection")
        #setup
        num_frame_buffers = ADComponent(EpicsSignalWithRBV, "PENumFrameBuffers")
        frame_buff_index = ADComponent(EpicsSignalRO, "PEFrameBuffIndex")
        image_number = ADComponent(EpicsSignalRO, "PEImageNumber")
        initialize = ADComponent(EpicsSignal, "PEInitialize")
        #trigger out
        trigger_out_signal = ADComponent(EpicsSignal, "PETrigOutSignal")
        EP_length = ADComponent(EpicsSignal, "PETrigOutEPLength")
        EP_first_frame = ADComponent(EpicsSignal, "PETrigOutEPFirstFrame")
        EP_last_frame = ADComponent(EpicsSignal, "PETrigOutEPLastFrame")
        EP_delay1 = ADComponent(EpicsSignal, "PETrigOutEPDelay1")
        EP_delay2 = ADComponent(EpicsSignal, "PETrigOutEPDelay2")
        DDD_delay = ADComponent(EpicsSignal, "PETrigOutDDDDelay")
        trigger_out_edge = ADComponent(EpicsSignal, "PETrigOutEdge")
        #collect 
        gain = ADComponent(EpicsSignalWithRBV, "PEGain")
        skip_frames = ADComponent(EpicsSignalWithRBV, "PESkipFrames")
        num_frames_skip = ADComponent(EpicsSignalWithRBV, "PENumFramesToSkip")
        sync_mode = ADComponent(EpicsSignalWithRBV, "PESyncMode")
        pe_trigger = ADComponent(EpicsSignal, "PETrigger")
        
        frame_type = ADComponent(EpicsSignal, "FrameType")
        frame_type_zero = ADComponent(EpicsSignal, "FrameType.ZRST")
        frame_type_one = ADComponent(EpicsSignal, "FrameType.ONST")
        frame_type_two = ADComponent(EpicsSignal, "FrameType.TWST")
        
    return Varex_CamPlugin

#define default plugin configs - separate for each det
varex20idff_plugin_control = {
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
    "ndport_trans1" : "4343CT1",    #NOTE: port name is diff for diff dets
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "TRANS1",
    "ndport_hdf1" : "TRANS1"
}

s20varex2_plugin_control = {
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
    "ndport_trans1" : "VAREX2", #NOTE: port name is diff for diff dets
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "TRANS1",
    "ndport_hdf1" : "TRANS1"
}

s1varex1_plugin_control = {
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
    "ndport_trans1" : "VAREX1", #NOTE: port name is diff for diff dets
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "TRANS1",
    "ndport_hdf1" : "TRANS1"
}


#define VAREX Mixin class for extra attributes/methods 
class VarexMixin(object):
    
    
    def default_setup(self):
        """Method for setting up default params. 
        Especially important for setting up HDF5 format."""
        
        #Define the HDF5 save path (up to 16 paths). 
        #Paths must be explicitly defined in `layout.xml` file.
        yield from bps.mv(
            self.cam.frame_type_zero, "/exchange/data",
            self.cam.frame_type_one, "/exchange/dark",
            self.cam.frame_type_two, "/exchange/bright"
        )

        #attribute file
        yield from bps.mv(
            self.cam.nd_attributes_file, DEFAULT_XML_ATTRIBUTE[self.name]  #FIXME
        )

        #default values for hdf1 plugin
        yield from bps.mv(
            self.hdf1.create_directory, -3,
            self.hdf1.auto_increment, 'Yes',
            self.hdf1.file_template, '%s%s_%06d.h5',
            self.hdf1.compression, 'None',
            self.hdf1.num_data_bits, 8,
            self.hdf1.data_bits_offset, 0,
            self.hdf1.szip_num_pixels, 16,
            #self.hdf1.jpeg_quality, 90,
            self.hdf1.store_perform, 'Yes',
            self.hdf1.store_attr, 'Yes',
            self.hdf1.swmr_mode, 'Off',
            self.hdf1.blosc_shuffle, 'Byte',
            self.hdf1.blosc_compressor, 'BloscLZ',
            self.hdf1.blosc_level, 5,
            self.hdf1.xml_file_name, DEFAULT_XML_LAYOUT[self.name]
        )
    

    
    def fastsweep_config(
        self, 
        exposure_time,
        mode = "Multiple"
        ):
        """Method for configuring varex for hardware-triggered fastsweeps.
        Intended to apply to PVs that stay the same throughout the fastsweep
        (e.g., same for collecting both dark fields and data frames).

        See `FFD_initialize` in `varex.mac` for spec macro.
        
        PARAMETERS 
        
        exposure_time *float* : 
            Exposure time per frame. NOTE: Plugging this into the cam.exposure_time PV doesn't
            actually inform the exposure time. Exposure time is controlled by the scan/trigger
            speed, which should match the number here if calculated correctly. This value is 
            plugged into the PV just for checking in GUIs. 

        mode *str* : 
            Image mode. Select from "Continuous", "Multiple", "Single". (default : "Multiple")
        

        """
        
        #first, make sure default settings are used. 
        yield from self.default_setup()
        
        #enable default plugins
        yield from self.enable_plugins()
        
        #set cam PVs
        yield from bps.mv(
            #set cam plugin
            #collection
            self.cam.wait_for_plugins, 'No',
            self.cam.sync_mode, "Framewise",
            self.cam.image_mode, mode,  #default "Multiple"
            self.cam.gain, 2,
            self.cam.acquire_time, exposure_time, #NOTE: This doesn't determine exposure time, which is actually controlled by pulse rate
            #shutter
            self.cam.shutter_mode, 0,
            #trigger
            self.cam.trigger_out_signal, 0,
            self.cam.trigger_out_edge, 1,
            #corrections
            self.cam.use_offset, 0, 
            self.cam.use_gain, 0, 
            self.cam.use_pixel_correction, 0,

            #if self.name == "varex20idff"

            #set trans1 plugin
            self.trans1.array_callbacks, 'Enable',
            self.trans1.type_, 'Rot270',

            #set proc1 plugin
            self.proc1.array_callbacks, 'Enable',
            self.proc1.enable_flat_field, 'Disable',
            self.proc1.enable_offset_scale, 'Disable',
            self.proc1.enable_low_clip, 'Enable',
            self.proc1.low_clip, 0, 
            self.proc1.enable_high_clip, 'Disable',
            self.proc1.enable_filter, 'Disable',
            self.proc1.data_type_out, 'Automatic',
            self.proc1.enable_background, 'Disable',
        )
        

        

        
    def fastsweep_dark_config(
        self,
        ndarks
      
    ):
        
        """Method for configuring varex detector to collect
        dark frames during a fastsweep plan. 
        
        Intended to follow `DET.fastsweep_config()`, which is 
        used for general fastsweep configuration PVs."""

        
        yield from bps.mv(
            #set cam plugin 
            self.cam.frame_type, 1, #1 = "dark"; must be given as integer, string won't work
            self.cam.num_images, ndarks, 
            self.cam.trigger_mode, "Internal",
            self.cam.skip_frames, 1, #enable
            self.cam.num_frames_skip, 1,

           

        )

        print(f"""Detector configured for collecting dark frames in {self.cam.trigger_mode.get(as_string = True)} mode.""")


    def fastsweep_data_config(
        self,
        nframes,
        images_per_frame = 1
    ):
        """Method for configuring varex detector to collect
        data frames during a fastsweep plan.
        
        Intended to follow `DET.fastsweep_config()`, which is
        used for general fastsweep configuration PVs. Can 
        follow/ be followed by `DET.fastsweep_dark_config()` if 
        collecting dark frames, but not required.
        
        TODO: Modify if needed to use more than one image per frame"""

        yield from bps.mv(
            #set cam plugin 
            self.cam.frame_type, 0, #0 = "data", must be given as integer, string won't work
            self.cam.num_images, nframes,         
            self.cam.trigger_mode, "External",
            self.cam.skip_frames, 0,     #disable
        )

        #set up recursive filter
        if images_per_frame < 2:
            yield from bps.mv(
                self.proc1.num_filter, 1,
                self.proc1.enable_filter, 'Disable'
            )
        else: 
            yield from bps.mv(
                self.proc1.num_filter, images_per_frame, 
                self.proc1.enable_filter, 'Enable',
                self.proc1.filter_type, "Average",
                self.proc1.auto_reset_filter, "Yes:",
                self.proc1.filter_callbacks, "Array N Only"
            )

        print(f"""Detector configured for data collection in {self.cam.trigger_mode.get(as_string = True)} mode.
              Averaging {images_per_frame} images per frame.""")


if "20-ID" in beamline: 
    #create VAREX object for 20-ID-D detector
    varex20idff = make_det(
        det_prefix = "20IDFF:",
        device_name = "varex20idff",
        #local_drive = "M:",
        READ_PATH = READ_PATH["varex20idff"],
        WRITE_PATH = WRITE_PATH["varex20idff"],
        make_cam_plugin = make_varex_cam,
        default_plugin_control = varex20idff_plugin_control,
        det_mixin = VarexMixin, 
        ioc_WIN = True, 
        pva1_exists = True,
        use_hdf1= True,
        use_tiff1 = True
    )    

    #create VAREX object for 20-ID-E detector
    s20varex2 = make_det(
        det_prefix = "20idVarex2:",
        device_name = "s20varex2",
        #local_drive = "M:",
        READ_PATH = READ_PATH["s20varex2"],
        WRITE_PATH = WRITE_PATH["s20varex2"],
        make_cam_plugin = make_varex_cam,
        default_plugin_control = s20varex2_plugin_control,
        det_mixin = VarexMixin, 
        ioc_WIN = True, 
        pva1_exists = True,
        use_hdf1= True,
        use_tiff1 = True
    )    

if "1-ID" in beamline: 
    #create VAREX object for 1-ID detector
    s1varex1 = make_det(
        det_prefix = "1idVarex1:",
        device_name = "s1varex1",
        READ_PATH = READ_PATH["s1varex1"],
        WRITE_PATH = WRITE_PATH["s1varex1"],
        make_cam_plugin = make_varex_cam,
        default_plugin_control = s1varex1_plugin_control,
        det_mixin = VarexMixin,
        ioc_WIN = True, 
        pva1_exists = True, 
        use_hdf1 = True, 
        use_tiff1 = True
    )   