""" 
Uses `make_det()` from .ad_make_dets module to create SIM device. 
Selects plugin versions based on version of ADCore the IOC is using.

`make_det()` requires detector-specific inputs, which are contained here. 
These include:
    - blueprint for cam class specific to the SIM detector
    - `default_plugin_control` dictionary, which enables/disables 
        plugins in default setup
    - detector-specific Mixin class, which contains methods and 
        extra attributes specific to SIM. These include
        configuration for fastsweep. 

`make_det()` returns a detector object to control SIM. 

"""

__all__ = [
    "sim_det",
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

#define global variables 
#DEFAULT_XML_LAYOUT = "/home/beams/S20HEDM/bluesky/user/Sim_detector/Sim_layout.xml"
#DEFAULT_XML_ATTRIBUTE = "/home/beams/S20HEDM/bluesky/user/Sim_detector/Sim_attributes.xml"
DEFAULT_XML_LAYOUT = '/net/s6iddata/export/hedm_sata/Varex_detector/Varex_layout.xml'
DEFAULT_XML_ATTRIBUTE = '/net/s6iddata/export/hedm_sata/Varex_detector/Varex_attributes.xml'


#WRITE_PATH_STEM = "/net/s6iddata/export/hedm_sata/"
#READ_PATH_STEM = "/net/s6iddata/export/hedm_sata/"
WRITE_PATH_STEM = "/home/beams/S20HEDM/bluesky/user/bdp_demo_0724_simdet/"
READ_PATH_STEM = "/home/beams/S20HEDM/bluesky/user/bdp_demo_0724_simdet/"

PI_FOLDER = iconfig["EXPERIMENT"]["PI_FOLDER"]
WRITE_PATH = WRITE_PATH_STEM + PI_FOLDER + "/"
READ_PATH = READ_PATH_STEM + PI_FOLDER + '/'


#define blueprint for making SIM cam class
def make_sim_cam(Det_CamBase):

    class Sim_CamPlugin(Det_CamBase):
        wait_for_plugins = ADComponent(EpicsSignal, "WaitForPlugins")
        #frame_type = ADComponent(EpicsSignal, "FrameType")
        frame_type_zero = ADComponent(EpicsSignal, "FrameType.ZRST")
        frame_type_one = ADComponent(EpicsSignal, "FrameType.ONST")
        frame_type_two = ADComponent(EpicsSignal, "FrameType.TWST")

    return Sim_CamPlugin

#define default plugin config
#NOTE: plugins control designed to look liek varex20idff
sim_plugin_control = {
    "use_image1" : False,
    "use_pva1" : True,
    "use_proc1" : True,
    "use_trans1" : True,
    "use_over1" : False, 
    "use_roi1" : False, 
    "use_tiff1" : False, 
    "use_hdf1" : True, 
    "ndport_image1" : "",
    "ndport_pva1" : "PROC1",
    "ndport_proc1" : "TRANS1",
    "ndport_trans1" : "cam1",
    "ndport_over1" : "",
    "ndport_roi1" : "",
    "ndport_tiff1" : "",
    "ndport_hdf1" : "TRANS1"
}

#define SIM Mixin class for extra attributes/methods
class SimMixin(object):

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
            self.cam.nd_attributes_file, DEFAULT_XML_ATTRIBUTE
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
            self.hdf1.xml_file_name, DEFAULT_XML_LAYOUT
        )

    def fastsweep_config(
        self, 
        exposure_time,
        mode = "Multiple",
    ):

        """Method for configuring SIM for hardware-triggered fastsweeps.
        Intended to apply to PVs that stay the same throughout the fastsweep
        (e.g., same for collecting both dark fields and data frames).
        
        PARAMETERS

        exposure_time *float* : 
            Exposure time per frame. NOTE: Plugging this into the cam.exposure_time PV doesn't
            actually inform the exposure time. Exposure time is controlled by the scan/trigger
            speed, which should match the number here if calculated correctly. This value is 
            plugged into the PV just for checking in GUIs. 

        mode *str* : 
            Image mode. Select from "Continuous", "Multiple", "Single". (default : "Multiple")
        
        """

        #first, make sure default settings are used
        yield from self.default_setup()

        #enable default plugins
        yield from self.enable_plugins()

        #set cam PVs
        yield from bps.mv(
            #set cam plugin
            #collection
            self.cam.wait_for_plugins, 'No',
            self.cam.image_mode, mode,  #default "Multiple"
            self.cam.gain, 2,
            self.cam.acquire_time, exposure_time, #NOTE: This doesn't determine exposure time, which is actually controlled by pulse rate
            #shutter
            self.cam.shutter_mode, 0,
        
            #set trans1 plugin
            self.trans1.array_callbacks, 'Enable',
            self.trans1.type_, 'Rot270',

            #set proc1 plugin
            self.proc1.array_callbacks, 'Enable',
            self.proc1.enable_flat_field, 'Disable',
            self.proc1.enable_offset_scale, 'Disable',
            self.proc1.enable_low_clip, 'Enable',
            #self.proc1.low_clip, 0, 
            self.proc1.enable_high_clip, 'Disable',
            self.proc1.enable_filter, 'Disable',
            self.proc1.data_type_out, 'Automatic',
            self.proc1.enable_background, 'Disable',
        )

    def fastsweep_dark_config(
            self, 
            ndark_frames,
    ):
        
        """Method for configuring SIM detector to collect
        dark frames during a fastsweep plan.
        
        Intended to follow DET.fastsweep_config(), which is 
        used for general fastsweep configuration PVs."""

        yield from bps.mv(
        #set cam plugin 
        self.cam.frame_type, 1, #1 = "dark"; must be given as integer, string won't work
        self.cam.num_images, ndark_frames, 
        self.cam.trigger_mode, "Internal",
        )

        print(f"""Detector configured for collecting dark frames 
              in {self.cam.trigger_mode.get(as_string = True)} mode.""")

    def fastsweep_data_config(
            self,
            nframes,
            images_per_frame = 1
    ):
        
        """Method for configuring SIM detector to collect
        data frames during a fastsweep plan. 
        
        Intended to follow DET.fastsweep_config(), which is
        used for general fastsweep configuration PVs. Can 
        follow/ be followed by DET.fastsweep_dark_config() if 
        collecting dark frames, but not required. 
        """

        yield from bps.mv(
            #set cam plugin 
            self.cam.frame_type, 0, #0 = "data", must be given as integer, string won't work
            self.cam.num_images, nframes,         
            self.cam.trigger_mode, "External",
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

            print(f"""Detector configured for data collection 
                  in {self.cam.trigger_mode.get(as_string = True)} mode.
                  Averaging {images_per_frame} images per frame.""")
            
sim_det = make_det(
    det_prefix = "20idsimAD:",
    device_name = "sim_det",
    READ_PATH = READ_PATH,
    WRITE_PATH = WRITE_PATH, 
    make_cam_plugin = make_sim_cam,
    default_plugin_control = sim_plugin_control,
    det_mixin = SimMixin,
    ioc_WIN = False, 
    pva1_exists = True,
    use_hdf1 = True
)


        

    
