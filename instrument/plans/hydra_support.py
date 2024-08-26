""" 
Plan stubs for supporting the hydra/ collection of GE area detectors.

:see: /home/1-id/s1iduser/mpe_feb24/macros_PK/hydra_2022Jan26/use_hydra_newer.mac


FIXME: do we need to set exposure time, etc. in `hydra_capture()`?
FIXME: hydra_setup requires us to close the C shutter, but this hardware doesn't exist

TODO: Do we want to use EDF1 plugin? -- useful for testing
TODO: add support for something other than tiff1
TODO: add try except statement in hydra_abort-- generate messages as needed
TODO: put trig_mode in iconfig?
"""

__all__ = [
    "hydra_setup",
    "hydra_capture",
    "hydra_stop_capture",
    "hydra_abort",
]

#import and set up logging
import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#import from devices
from ..devices.ge_panels import *
from ..devices.hydra import *
from ..devices.s1id_FPGAs import softglue   #for fast shutter

#import other stuff
from .. import iconfig
from bluesky import plan_stubs as bps
import os
import time


#user configurations 
def select_panel_config():
    """Plan stub for selecting user configuration.
    Returns list of detector objects.
    
    NOTE: Does not require arguments because it automatically
    imports information about the panels from iconfig.
    
    Called in `hydra_setup()`.
    """
   
    #import selected panels from iconfig
    dets_str = iconfig["HYDRA_PANELS"]   #this is a list of str
   
   
    #default is to use all four panels
    dets = [ge1, ge2, ge3, ge4] #list of devices (panels)
    
    #remove those not using
    if 'ge1' not in dets_str: dets.remove(ge1)
    if 'ge2' not in dets_str: dets.remove(ge2)
    if 'ge3' not in dets_str: dets.remove(ge3)
    if 'ge4' not in dets_str: dets.remove(ge4)

    return dets
    
    
def sseq_trig_initialization(
    dets,
    use_full_initialization
):
    """Plan stub for initializing user string sequence records
    used to control the panel triggering.
    
    PARAMETERS
    
    dets *list of AD objects* :
        List of GE panels used for hydra configuration. Can be in any order.
    
    use_full_initialization  *Boolean*:
        True/False value that determines whether full initialization 
        protocol is needed. 
    
    """

    if type(dets) != list:
        return TypeError("`dets` must be a list of detector(s). Be sure to use brackets [] and separate detectors with commas.")
    
    
    #collect all htrig devices (all hmodes)
    htrigs = [
        htrig_rad,
        htrig_multi_det_sw,
        htrig_multi_det_edge,
        htrig_multi_det_pulse
    ]
    
    htrig_mode = {
        htrig_rad.name : "RAD",
        htrig_multi_det_sw.name : "MULTI_DET SW",
        htrig_multi_det_edge.name : "MULTI_DET Edge",
        htrig_multi_det_pulse.name : "MULTI_DET Pulse"
    }
    
    #enable calc record block 
    yield from bps.mv(sseq_enable, 1)
    
    for htrig in htrigs:
        yield from bps.mv(htrig.abort, 1)
                
    if use_full_initialization:
        #Full initialization not required if fields don't change.
        #Only dynamic PVs will be initialized.
                
        for htrig in htrigs:
            yield from bps.mv(
                htrig.scan, "Passive",
                htrig.precision, 5
            )
            
            #clear all input/delay/string value/numeric values
            yield from bps.mv(htrig.reset_all_records)
            
            #set wait modes
            yield from bps.mv(
                htrig.ss1.wait_completion, "After6",
                htrig.ss2.wait_completion, "After6",
                htrig.ss3.wait_completion, "After6",
                htrig.ss4.wait_completion, "After6",
                htrig.ss5.wait_completion, "After6"
            )
            
            #set captions and forward link
            yield from bps.mv(
                htrig.ss6.string_value, f"Hydra {htrig.name} WAITING...",    #TODO: check name
                htrig.ssA.string_value, f"Hydra {htrig.name} Ready", #TODO: check name
                htrig.forward_link, "0"
            )
            
            #set string_value fields 1-5 with detector modes
            string_value = htrig_mode[htrig.name]
            
            yield from bps.mv(
                htrig.ss1.string_value, string_value,
                htrig.ss2.string_value, string_value,
                htrig.ss3.string_value, string_value,
                htrig.ss4.string_value, string_value,
                htrig.ss5.string_value, string_value
            )
            
            #set output PVs-- static
            out_prefix = htrig.prefix
            out_link_value = out_prefix + ".DESC NPP NMS"
            
            yield from bps.mv(
                htrig.ss6.out_link, out_link_value,
                htrig.ssA.out_link, out_link_value
            )
     
    #below happens for both fast initialization and full initialization 
    #these PVs are dynamics and must always be initialized
    for htrig in htrigs: 
            
        #set output PVs-- dynamic, based on which panels are used (3 options)
        #option 1: only one panel used 
        if len(dets) == 1:
            yield from bps.mv(htrig.ss2.out_link, "GE2:cam1:TriggerMode PP NMS")
            
        elif len(dets) == 3:
            #option 2: GE1, GE3, GE4 are used
            option_2 = [ge1, ge3, ge4]
            
            if all(x in dets for x in option_2): 
                yield from bps.mv(
                    htrig.ss1.out_link, "GE1:cam1:TriggerMode PP NMS",
                    htrig.ss3.out_link, "GE1:cam1:TriggerMode PP NMS",
                    htrig.ss4.out_link, "GE4:cam1:TriggerMode PP NMS",
                )
            else: 
                raise ValueError("Three panels used, but not standard configuraiton. Sseq out_links will be incorrect.")
            
        elif len(dets) == 4:
            #option 3: all four panels are used  
            yield from bps.mv(
                htrig.ss1.out_link, "GE1:cam1:TriggerMode PP NMS",
                htrig.ss2.out_link, "GE2:cam1:TriggerMode PP NMS",
                htrig.ss3.out_link, "GE3:cam1:TriggerMode PP NMS",
                htrig.ss4.out_link, "GE4:cam1:TriggerMode PP NMS",
            )
        
        else: 
            raise ValueError("Requested panel configuration is not recognized.")



def select_trig_mode(
    dets,
    trig_mode
):
    """Plan stub to select and configure the trig mode of the DTH module.
    
    PARAMETERS
    
    dets *list of AD objects*:
        List of GE panels used for hydra configuration. Can be in any order.
    
    trig_mode *str* : 
        Triggering mode for DTH module. Must be one of four options: 
        "Rad", "MultiDet SW", "MultiDet Edge", or "MultiDet Pulse". 
    """
    
    #check that input values for arguments are reasonable
    if type(dets) != list:
        raise TypeError("`dets` must be a list of detector(s). Be sure to use brackets [] and separate detectors with commas.")

    trig_options = ["Rad", "MultiDet SW", "MultiDet Edge", "MultiDet Pulse"]
    if trig_mode not in trig_options: 
        raise ValueError(f"trig_mode not recognized. Must be one of the following: {trig_options}. Received {trig_mode}")


    #set HW signal-controlled trigger 
    if trig_mode == "Rad": 
        #RAD is the only one where dth_mode doesn't match trig_mode
        dth_mode = "MultiDet SW" 
    else:dth_mode = trig_mode   #all others match


    #reset DTH module
    yield from hydra.dth.initialize()    

    #change default set in hydra.dth.initialize()
    yield from bps.mv(hydra.dth.mode_mbbo, dth_mode)  
    
    #change panels to used if they are selected (default unused in initialize)
    if ge1 in dets: yield from bps.mv(hydra.dth.ge1_used_bo, "0")
    if ge2 in dets: yield from bps.mv(hydra.dth.ge2_used_bo, "0")
    if ge3 in dets: yield from bps.mv(hydra.dth.ge3_used_bo, "0")
    if ge4 in dets: yield from bps.mv(hydra.dth.ge4_used_bo, "0")


    #choose device based on trig_mode input
    choose_htrig_device = {
       "MultiDet SW" :  htrig_multi_det_sw,
       "MultiDet Edge" : htrig_multi_det_edge, 
       "MultiDet Pulse" : htrig_multi_det_pulse,
       "Rad" : htrig_rad
    }
    htrig = choose_htrig_device[trig_mode]  #choose device using dictionary
    
    #close fast shutters
    yield from bps.mv(
        softglue.fs1_mask, '0',
        softglue.fs2_mask, '0'
    )
    
    #switch trig if needed
    yield from bps.trigger(htrig.switch_trigger)    #presses button on .PROC field
    
    #open fast shutters
    yield from bps.mv(
        softglue.fs1_mask, '1',
        softglue.fs2_mask, '1'
    )


def select_image_mode(
    dets,
    trig_mode,
    ):
    """Plan stub to select image mode and set num images per trigger.
    
    PARAMETERS
    
    dets *list of AD objects*:
        List of GE panels used for hydra configuration. Can be in any order.
    
    trig_mode *str* : 
        Triggering mode for DTH module. Must be one of four options: 
        "Rad", "MultiDet SW", "MultiDet Edge", or "MultiDet Pulse"."""
    
   #check that input values for arguments are reasonable
    if type(dets) != list:
        raise TypeError("`dets` must be a list of detector(s). Be sure to use brackets [] and separate detectors with commas.")

    trig_options = ["Rad", "MultiDet SW", "MultiDet Edge", "MultiDet Pulse"]
    if trig_mode not in trig_options: 
        raise ValueError(f"trig_mode not recognized. Must be one of the following: {trig_options}. Received {trig_mode}")
    
    if trig_mode == "Rad":
        for det in dets: 
            yield from bps.mv(det.cam1.image_mode, "First")
    else: 
        for det in dets: 
            yield from bps.mv(det.cam1.image_mode, "Last")
    
  
def hydra_setup(
    trig_mode,
    use_full_initialization = True,

):
    """ 
    PARAMETERS 
      
    trig_mode *str* : 
        Triggering mode for DTH module. Must be one of four options: 
        "Rad", "MultiDet SW", "MultiDet Edge", or "MultiDet Pulse".
        
    use_full_initialization *Boolean* :
        True/False value that determines whether full initialization 
        protocol is needed. 
    """
    
    #check input values for arguments are reasonable
    if type(use_full_initialization) != bool:
        raise TypeError(f"use_full_initialization must be either True or False. Received {use_full_initialization}.")

    trig_options = ["Rad", "MultiDet SW", "MultiDet Edge", "MultiDet Pulse"]
    if trig_mode not in trig_options: 
        raise ValueError(f"trig_mode not recognized. Must be one of the following: {trig_options}. Received {trig_mode}")
    
    
    #TODO: close C fast shutter -- doesn't exist??
    
    dets = yield from select_panel_config()
    
    #initialize user Sseq records
    yield from sseq_trig_initialization(
        dets = dets, 
        use_full_initialization = use_full_initialization
        )
    
    #reset and configure DTH module for selected trigger mode
    yield from select_trig_mode(trig_mode=trig_mode)

    #change image mode on panels depending on trigger mode        
    yield from select_image_mode(
        trig_mode = trig_mode,
        dets = dets
    )
    
    #for each GE panel, set default settings and initialize
    #NOTE: initialize presses Acquire button on each GE panel
    for det in dets:
        yield from det.default_setup(initialize = True) 
        #Acquire trigger will wait for completion for each panel
        
    
    
def hydra_capture(
    file_name, 
    scan_folder, 
):
    """"Plan stub to start capturing data with hydra configuration.
    
    PARAMETERS
    
    file_name *str* : 
        Base name given to each output file. 
        Does not include temporary suffix or suffix file number. 
        
    scan_folder *str* : 
        Last folder in path where files are written. Does not need to end with
        "/".
    """

    #fetch which GE panels are used in hydra configuration    
    dets = yield from select_panel_config()
    
    for det in dets:
        yield from bps.mv(
            det.tiff1.file_name, file_name,
            det.tiff1.file_path, scan_folder,
            det.tiff1.file_write_mode, "Stream" #should be set, just to make sure
        )
        
    for det in dets:
        yield from bps.mv(
            det.tiff1.capture, "Capture"
        )
        
def hydra_stop_capture():
    """Plan stub to stop the capture in progress on the hydra."""

    dets = yield from select_panel_config()
    
    for det in dets: 
        yield from bps.mv(
            det.tiff1.capture, "Done",
            #det.tiff1.file_write_mode, "Single"    #I don't like resetting this
        )
        

def hydra_abort():
    """Plan stub to abort the hydra acquisition in progress."""

    dets = yield from select_panel_config()
    
    for det in dets:
        yield from bps.mv(
            det.cam.acquire, "Done",
            det.cam.capture, "Done"
        )
    
        