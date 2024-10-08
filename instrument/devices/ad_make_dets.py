""" 
Exports `make_det()`, a blueprint for generating area detectors using plugins 
customized for MPE group. DOES NOT generate the detector
objects themselves; see `DETECTOR.py` files for generation. 

`find_det_version()` tries to automatically find the version of ADcore
that the det is running; starting up a different version of a det IOC
should therefore be accommodated without additional work by 
Bluesky user. 

Blueprints take into account whether dets run on WIN or LIN machines;
this changes the structure of the read and write paths. Paths generated
by `make_WIN_paths()` and `make_LIN_paths()`.
 
Custom plugin classes are generated by .ad_plugin_classes, and 
`ad_plugin_classes.py` must be contained in the same folder. 

Detector-specific cam classes, `plugin_control` dictionary (for 
enabling/disabling plugins as needed for the det), and any 
scan-specific mixin methods are located in `DETECTOR.py` file. 

TODO: Uncomment lines needed to make hdf1 plugin when it has been primed for all dets. 
FIXME: Change the root path for linux to something for 20ID
FIXME: Win/Lin path formulations don't work for all detectors
"""

__all__ = [
    "make_det",
]

#import for logging
import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#import custom plugin classes
from .ad_plugin_classes import *

#import from ophyd
from ophyd import EpicsSignal
from ophyd import SingleTrigger
from ophyd import DetectorBase
from ophyd import ADComponent

#import other stuff
import os
import bluesky.plan_stubs as bps

#try to find ADcore version of det
def find_det_version(
    det_prefix
):
    
    """ 
    Function to generate an ophyd signal of the detector ADCoreVersion PV, 
    then use this version number to select the corresponding
    versions of MPE-specific plugin classes.
    
    MPE-sepcific plugin classes are generated in .ad_plugin_classes module. 
    
    PARAMETERS 
    
    det_prefix *str* : 
        IOC prefix of the detector; must end with ":". (example : "s1_pixirad2:")
    """
    
    try:
        #first try to connect to ADCoreVersion PV
        adcore_pv = det_prefix + "cam1:ADCoreVersion_RBV"
        adcore_version = EpicsSignal(adcore_pv, name = "adcore_version")
        version = adcore_version.get() #returns something that looks like '3.2.1'
    
    except TimeoutError: #as exinfo: #TODO: add check if IOC is running to make error more specific
        version = '1.9.1'
        logger.warning(f"Finding {det_prefix} AD version timed out. Assuming mininum version 1.9.")
        
    
    finally: 
        #after trying and excepting, select the plugin versions needed
        version_bits = version.split('.')
        if version_bits[0] == '1' and version_bits[1] == '9':   #for v1.9
            Det_CamBase = MPE_CamBase
            Det_ImagePlugin = MPE_ImagePlugin
            Det_PvaPlugin = MPE_PvaPlugin
            Det_ProcessPlugin = MPE_ProcessPlugin
            Det_TransformPlugin = MPE_TransformPlugin
            Det_OverlayPlugin = MPE_OverlayPlugin
            Det_ROIPlugin = MPE_ROIPlugin
            Det_TIFFPlugin = MPE_TIFFPlugin
            Det_HDF5Plugin = MPE_HDF5Plugin
            #logger.info('Using vanilla plugins.')
            
        elif version_bits[0] == '3' and any(x == version_bits[1] for x in ['1', '2', '3']): #for versions '3.1','3.2','3.3'
            Det_CamBase = MPE_CamBase_V31
            Det_ImagePlugin = MPE_ImagePlugin_V31
            Det_PvaPlugin = MPE_PvaPlugin_V31
            Det_ProcessPlugin = MPE_ProcessPlugin_V31
            Det_TransformPlugin = MPE_TransformPlugin_V31
            Det_OverlayPlugin = MPE_OverlayPlugin_V31
            Det_ROIPlugin = MPE_ROIPlugin_V31
            Det_TIFFPlugin = MPE_TIFFPlugin_V31
            Det_HDF5Plugin = MPE_HDF5Plugin_V31
            #logger.info("Using V31 plugins.")
            
        elif version_bits[0] == '3' and not any(x == version_bits[1] for x in ['1','2','3']):  #for versions '3.4' and higher
            Det_CamBase = MPE_CamBase_V34
            Det_ImagePlugin = MPE_ImagePlugin_V34
            Det_PvaPlugin = MPE_PvaPlugin_V34
            Det_ProcessPlugin = MPE_ProcessPlugin_V34
            Det_TransformPlugin = MPE_TransformPlugin_V34
            Det_OverlayPlugin = MPE_OverlayPlugin_V34
            Det_ROIPlugin = MPE_ROIPlugin_V34
            Det_TIFFPlugin = MPE_TIFFPlugin_V34
            Det_HDF5Plugin = MPE_HDF5Plugin_V34
            #logger.info('Using V34 plugins.')    
                
        else:
            raise ValueError(f"""MPE custom plugins have not been generated for this version of ADcore = {version}. 
                             Are you running the correct IOC version for {det_prefix}?""")
        
        logger.info(f"Trying detector with prefix {det_prefix}, using ADcore v{version}.")  
    
    return [Det_CamBase, 
            Det_ImagePlugin, 
            Det_PvaPlugin, 
            Det_ProcessPlugin, 
            Det_TransformPlugin, 
            Det_OverlayPlugin,
            Det_ROIPlugin, 
            Det_TIFFPlugin,
            Det_HDF5Plugin]

# FIXME
# def make_WIN_paths(
#     det_prefix,
#     local_drive,
#     image_dir
# ):
    
#     """ 
#     Function to generate controls and local paths for a detector IOC that runs 
#     on Windows. 
    
#     Colloqial definitions:
    
#         Local path: location where the detector is writing data to. Can be local to 
#             machine where det IOC is running, or contained on the APS network. 
            
#         Controls path: pathway Bluesky will use to look at the data being written. 
#             Virtually always on the APS network. 
        
#     PARAMETERS
    
#     det_prefix *str* :
#         IOC prefix of the detector; must end with ":". (example : "s1_pixirad2:")
        
#     local_drive *str* : 
#         Windows drive where data is written; must end with ":". (example : "G:")
        
#     image_dir *str* : 
#         Experiment folder where data is written; must be common to both controls and local path. (example : "mpe_apr24/experiment1")
    
#     """
    
#     #clean up det name and Windows Drive 
#     det_id = det_prefix.strip(":")
#     linux_drive = local_drive.strip(":")
    
#     #define paths
#     CONTROLS_ROOT = os.path.join("/home/beams/S1IDUSER", det_id, linux_drive, '')   #Linux root for bluesky
#     LOCAL_ROOT = local_drive    #Windows root for det writing
#     IMAGE_DIR = image_dir  #TODO: pull this specifically from iconfig!!
    
#     return [CONTROLS_ROOT, LOCAL_ROOT, IMAGE_DIR]

# #FIXME
# def make_LIN_paths(
#     local_drive,
#     image_dir
# ):
#     """
#     Function to generate controls and local paths for a detector IOC that runs 
#     on Linux. 
    
#     Colloquial definitions:
    
#         Local path: location where the detector is writing data to. Can be local to 
#             machine where det IOC is running, or contained on the APS network. 
        
#         Controls path: pathway Bluesky will use to look at the data being written. 
#             Virtually always on the APS network. 
        
#     PARAMETERS
            
#     local_drive *str* : 
#         Full Linux pathway where data is written. (example : "/scratch/tmp")
        
#     image_dir *str* : 
#         Experiment folder where data is written; must be common to both controls and local path. (example : "mpe_apr24/experiment1")
#     """
    
#     #define paths
#     CONTROLS_ROOT = "/home/beams/S1IDUSER/mnt/s1c"
#     LOCAL_ROOT = local_drive    #Linux root for det writing
#     IMAGE_DIR = image_dir  #TODO: pull this specifically from iconfig!!
    
#     return [CONTROLS_ROOT, LOCAL_ROOT, IMAGE_DIR]


def make_det(
    det_prefix,
    device_name,
    #local_drive,
    READ_PATH,
    WRITE_PATH,
    make_cam_plugin,
    default_plugin_control, #needed for class method
    custom_plugin_control = {}, #needed for class method
    det_mixin = None, 
    ioc_WIN = False, 
    pva1_exists = False,
    use_tiff1 = True,
    use_hdf1 = True,
):
    """ 
    Function to generate detector object or assign it as `None` if timeout.
    
    PARAMETERS 
    
    det_prefix *str* : 
        IOC prefix of the detector; must end with ":". (example : "s1_pixirad2:")
    
    device_name *str* : 
        Name of the detector device. Should match the object name in python. 
    
    #FIXME
    local_drive *str* : 
        If on Linux, full Linux pathway where data is written. (example : "/scratch/tmp")
        If on Windows, drive location where data is written; must end with ":". (example : "G:")
    
    make_cam_plugin *class* : 
        Detector-specific cam plugin written in `DETECTOR.py` file. 
        
    default_plugin_control *dict* :
        Dictionary that logs which plugins are enabled and which are disabled in 
        default state for a given det.  Contained in `DETECTOR.py` file. 
        
    custom_plugin_control *dict* : 
        Dictionary containing enable/disable or ndarray port names for plugins that 
        are different from the default setup. Changeable by user. (default : {})
        
    det_mixin *Mixin class* : 
        Optional Mixin class specific to the detector for custom methods or 
        attributes. An example method would be configuration for a fastsweep scan.
        Contained in `DETECTOR.py` file. (default : None)
    
    ioc_WIN *Boolean* : 
        True/False whether det IOC runs on a Windows machine. Does not matter 
        what Windows OS version. (default : False)
        
    pva1_exists *Boolean* : 
        True/False whether `DETECTOR:Pva1` PVs exist. NOT the same as whether Pva1 
        plugin should be enabled. (default : False) 
        
    use_tiff1 *Boolean* : 
        True/False whether `DETECTOR:TIFF1` PVs should be used. NOT the same 
        as whether the plugin should be enabled. (defualt : True)
        
    use_hdf1 *Boolean* :
        True/False whether 'DETECTOR:HDF1` PVs should be used. NOT the same
        as whether the plugin should be enabled. For some dets, hdf1 isn't
        initialized with image dimensions and will throw and error. 
        (default : True)
            
    """
        
    #use `find_det_version()` to select plugin versions based on ADCore version
    [Det_CamBase, 
    Det_ImagePlugin, 
    Det_PvaPlugin, 
    Det_ProcessPlugin, 
    Det_TransformPlugin, 
    Det_OverlayPlugin,
    Det_ROIPlugin, 
    Det_TIFFPlugin,
    Det_HDF5Plugin] = find_det_version(det_prefix = det_prefix) 
    
    #generate detector-specific cam plugin (defined in `DETECTOR.py` file) using correct CamBase version
    Det_CamPlugin = make_cam_plugin(Det_CamBase = Det_CamBase) 
    
    #FIXME -- need standardized linux and windows paths/mounts
    # #generate read and write paths for WIN or LIN machines
    # #see `make_WIN_paths()` and `make_LIN_paths()`
    # if ioc_WIN:
    #     [CONTROLS_ROOT, LOCAL_ROOT, IMAGE_DIR] = make_WIN_paths(
    #         det_prefix = det_prefix, 
    #         local_drive = local_drive, 
    #         image_dir = image_dir)

    # else: 
    #     [CONTROLS_ROOT, LOCAL_ROOT, IMAGE_DIR] = make_LIN_paths(
    #         local_drive = local_drive, 
    #         image_dir = image_dir)     
    
    # #define complete read and write paths for file-writing plugins
    # WRITE_PATH = os.path.join(LOCAL_ROOT, IMAGE_DIR)
    # READ_PATH = os.path.join(CONTROLS_ROOT, IMAGE_DIR)
    
    #add protection in case det_mixin is not defined yet
    if not det_mixin:
        class EmptyFastsweepMixin(object):
            print(f"Custom configuration methods have not been configured for detector = {det_prefix}.")  
            
            #TODO: Can this be generalized for a detector??
            
        det_mixin = EmptyFastsweepMixin
    
    #create a general class for making an area detector using plugin and mixin inputs defined above
    class MPEAreaDetector(det_mixin, SingleTrigger, DetectorBase):
        
        #define plugins here
        cam = ADComponent(Det_CamPlugin, "cam1:")
        image1 = ADComponent(Det_ImagePlugin, "image1:")
        #caveat in case pva1 does not exist
        if pva1_exists:
            pva1 = ADComponent(Det_PvaPlugin, "Pva1:")
        proc1 = ADComponent(Det_ProcessPlugin, "Proc1:")
        trans1 = ADComponent(Det_TransformPlugin, "Trans1:")
        over1 = ADComponent(Det_OverlayPlugin, "Over1:")
        roi1 = ADComponent(Det_ROIPlugin, "ROI1:")
        
        #define file writing plugins
        if use_tiff1:
            tiff1 = ADComponent(Det_TIFFPlugin, "TIFF1:",
                            write_path_template = WRITE_PATH,
                            read_path_template = READ_PATH)
        
        if use_hdf1:
            hdf1 = ADComponent(Det_HDF5Plugin, "HDF1:",
                            write_path_template = WRITE_PATH, 
                            read_path_template = READ_PATH)
        
        #add a method to the object that will enable/disable plugins as desired
        def enable_plugins(
            self, 
            default_plugin_control = default_plugin_control, #plugin_control keys become defaults (det-specific)
            custom_plugin_control = custom_plugin_control   #non-default values 
        ):
            """ 
            Object method for enabling or disabling plugins as needed for a given det. 
            
            PARAMETERS 
            
            self : 
                Attaches method to objects belonging to the `MPEAreaDetector` class. 
                
            plugin_control *dict* : 
                Default options for enabling/disabling plugins and filling in `DETECTOR.nd_array_port` field.
                
            """
            
            #allow changes to dictionary from custom dictionary
            plugin_control = {**default_plugin_control, **custom_plugin_control}   #merges dictionaries so that input kwargs overrides defaults 
            
            #enabling/disabling
            if plugin_control["use_image1"]:
                yield from bps.mv(self.image1.enable, 1, self.image1.nd_array_port, plugin_control["ndport_image1"])
            else: 
                yield from bps.mv(self.image1.enable, 0)
        
            #extra caveats in case pva1 doesn't exist
            if pva1_exists and plugin_control["use_pva1"]:
                yield from bps.mv(self.pva1.enable, 1, self.pva1.nd_array_port, plugin_control["ndport_pva1"])
            elif pva1_exists and not plugin_control["use_pva1"]: 
                yield from bps.mv(self.pva1.enable, 0)
            elif not pva1_exists and plugin_control["use_pva1"]:
                raise ValueError("Warning! Request to enable Pva1 plugin, but it doesn't exist.")
                
            if plugin_control["use_proc1"]:
                yield from bps.mv(self.proc1.enable, 1, self.proc1.nd_array_port, plugin_control["ndport_proc1"])
            else:
                yield from bps.mv(self.proc1.enable, 0)
                
            if plugin_control["use_trans1"]:
                yield from bps.mv(self.trans1.enable, 1, self.trans1.nd_array_port, plugin_control["ndport_trans1"])
            else: 
                yield from bps.mv(self.trans1.enable, 0)
                
            if plugin_control["use_over1"]:
                yield from bps.mv(self.over1.enable, 1, self.over1.nd_array_port, plugin_control["ndport_over1"])
            else:
                yield from bps.mv(self.over1.enable, 0)
                
            if plugin_control["use_roi1"]:
                yield from bps.mv(self.roi1.enable, 1, self.roi1.nd_array_port, plugin_control["ndport_roi1"])
            else:
                yield from bps.mv(self.roi1.enable, 0)
            
            if use_tiff1 and plugin_control['use_tiff1']:
                yield from bps.mv(self.tiff1.enable, 1, self.tiff1.nd_array_port, plugin_control["ndport_tiff1"])
            elif use_tiff1 and not plugin_control["use_tiff1"]:
                yield from bps.mv(self.tiff1.enable, 0)
            elif not use_hdf1 and plugin_control["use_tiff1"]:
                raise ValueError("Warning! Request to enable TIFF1 plugin, but it doesn't exist. Check DET.py file.")
  
            if use_hdf1 and plugin_control['use_hdf1']:
                yield from bps.mv(self.hdf1.enable, 1, self.hdf1.nd_array_port, plugin_control["ndport_hdf1"])
            elif use_hdf1 and not plugin_control["use_hdf1"]:
                yield from bps.mv(self.hdf1.enable, 0)
            elif not use_hdf1 and plugin_control["use_hdf1"]:
                raise ValueError("Warning! Request to enable HDF1 plugin, but it doesn't exist. Check DET.py file.")
  
    
    #generate object using class defined above
    try: 
        area_detector = MPEAreaDetector(det_prefix, name = device_name, labels = ("Detector",))
        logger.info(f"SUCCESS. {device_name} created.")
        
    except TimeoutError as exinfo:
        area_detector = None
        logger.warning(f"FAILED: DETECTOR NOT CREATED. Could not create {device_name} with prefix {det_prefix}. Is the IOC running?")


    return area_detector    
    
    
    
   