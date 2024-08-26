""" 
Basic plans for continuously acquiring images or exposing detector(s).

TODO: Modify `expose()` to open/close shutters and add status object for multiple dets. 
TODO: Add bluesky suspenders to check on beam status
FIXME: Check code for detectors that have frame averaging
"""

__all__ = [
    "cont_acq",
    "stop_cont_acq",
    "expose",
]

import logging 
logger = logging.getLogger(__name__)
logger.info(__file__)

from bluesky import plan_stubs as bps
from bluesky import plans as bp


from ..devices import sms_aero, softglue, pixirad
import numpy as np
import matplotlib.pyplot as plt
import functools
import math
from matplotlib.path import Path
from collections import OrderedDict

#import other stuff
import os

  
def cont_acq(
    det,
    exposure_time,
    acquire_period,
    **kwargs
):
    
    """Plan stub to acquire images continuously on SINGLE chosen detector. The default is not to save images. 
    Based on spec macro `cont_acq` in `/home/1-id/s1iduser/mpe_feb24/macros_PK/TomoScans_2016Nov11/continuous_acq.mac`.

    PARAMETERS

    det *area detector object*:
        Detector that will capture images continuously. 

    exposure_time *float*:
        Duration of each exposure in seconds. 

    acquire_period *float*:
        Time in seconds between the beginning of each exposure.
    """

    #Clear out detector stage_sigs in case there are unwanted options. 
    det.tiff1.stage_sigs = {}
    det.cam.stage_sigs = {}

    #make sure everything is unstaged
    yield from bps.unstage(det)
    
    #make sure default plugins are enabled 
    yield from det.enable_plugins()
    
    #

    #Check that another continuous acquisition is not running.
    #FIXME: Print to log instead, prompt input for quitting or continuing

    #case 1: not pilatus or pixirad
    if det.name != "pilatus" and det.name != "pixirad":
        if det.cam.image_mode.get(as_string = True) == 'Continuous' and det.cam.acquire == 1:
            print("A continuous acquisition is already running. Stopping now.")
            yield from bps.mv(det.cam.acquire, 0)
    #case 2: pilatus is still running
    elif det.name == "pilatus":
        if det.cam.trig_mode == "Alignment":
            print(f"{det.name} is already acquiring continuously. Stopping now.")
            #TODO: stop pilatus
    #case 3: pixirad is still running
    elif det.name == "pixirad":
        if det.cam.acquire.get(as_string = True) == "Acquire":
            print(f"{det.name} is still acquiring. Please wait for it to finish before starting again.") 
    
    
    #After stopping ongoing acquisition (if ongoing), set standard plugin settings
    yield from det.default_setup()
    
    #Check to make sure acquire_period is long enough for det
    #FIXME: print to log instead
    if det.name == 'dexela' and acquire_period > 0.5: 
        print(f"Acquire_period of {acquire_period} s exceeds maximum for {det}, so we set it to the max (0.5 s).")
        acquire_period = 0.5
    elif det.name == 'pointgrey' and acquire_period > 1:
        print(f"Acquire_period of {acquire_period} s exceeds maximum for {det}, so we set it to the max (1.0 s).")
        acquire_period = 1.0
    elif det.name == 'grasshopper1' and acquire_period != 0.06675:
        print(f"Acquire_period for {det.name} is not writeable. Leaving as-is at {det.cam.acquire_period} s.")
        acquire_period = 0.06675
    elif det.name == 'pilatus':
        print(f"{det} works on a fixed frame rate, will set the period to 0.5 s.")
        
    
    #Turn on/off automatic saving; if you would like automatic saving, needs kwargs (save_img, scan_folder, file_name)
    if "save_img" in kwargs:
        save_img = save_img 
        
        #to save with a named file, require both folder and file name
        if "scan_folder" and "file_name" in kwargs:
            scan_folder = scan_folder 
            file_name = file_name
        else:
            scan_folder = ""
            file_name = ""
    #if save_img is not given as kwarg, assume not saving images
    else:
        save_img = False  
        
    #set up stage_sigs depending on if images are being saved or not
    if not save_img: 
        det.tiff1.stage_sigs["auto_save"] = 0
        # det.hdf1.stage_sigs["auto_save"] = 0
    else: 
        #tiff1 plugin
        det.tiff1.stage_sigs["auto_save"] = 1
        scan_folder = ""
        file_name = ""
        det.tiff1.stage_sigs["file_path"] = os.path.join(det.WRITE_PATH,scan_folder,'')
        det.tiff1.stage_sigs["file_name"] = file_name
        
        #hdf1 plugin
        # det.hdf1.stage_sigs["auto_save"] = 1
        # scan_folder = ""
        # file_name = ""
        # det.hdf1.stage_sigs["file_path"] = os.path.join(det.WRITE_PATH,scan_folder,'')
        # det.hdf1.stage_sigs["file_name"] = file_name
    
   
    
    #Set up cam plugin 
    #special provision for pixirad
    if "pixirad_num_images" in kwargs:
        pixirad_num_images = pixirad_num_images
    else:
        #set default number of pixirad images to 10 if not specified in kwargs
        pixirad_num_images = 10
    
    if det.name == "pixirad":
        det.cam.stage_sigs["trigger_mode"] = "Internal"
        det.cam.stage_sigs["num_images"] = pixirad_num_images
    elif det.name == "pilatus":  
        #special provision for pilatus
        det.cam.stage_sigs["trigger_mode"] = "Alignment"
    else:
        det.cam.stage_sigs["image_mode"] = "Continuous"

    #acquisition settings here
    det.cam.stage_sigs["acquire_time"] = exposure_time
    det.cam.stage_sigs["acquire_period"] = acquire_period
    #det.cam.stage_sigs["acquire"] = 1   #sets acquire to 1 instead of triggering
    
    print(f"Stage sigs are {det.stage_sigs}")
    
    #stage cam plugin
    yield from det.stage()

    print(f"Beginning continuous acquisition with expsorue time = {exposure_time} s, acquire_period = {acquire_period} s.")
    print("Use `stop_acq()` to stop.")
    
    #trigger image collection
    yield from bps.mv(det.cam.acquire, 1)
       



def stop_cont_acq(det):

    """Plan stub to stop continuously acquiring. 
    Pairs with `cont_acq()`.

    PARAMETERS

    det *area detector object*:
        Detector that is capturing images continuously. 
    """

    #special provision for pixirad
    if det.name == "pixirad":
        print(f"Waiting for {det.name} to finish acquiring. It cannot be stopped early.")
        return
    
    #all other dets
    else:   
        yield from bps.mv(
            det.cam.acquire, "Done",
            det.tiff1.capture, "Done",
            det.tiff1.file_write_mode
        )
        
        #unstage detector after stopping acquisition
        yield from bps.unstage(det)
        
    print("Continuous acquisition stopping complete.")
    
    
def expose(
        num_images,
        exposure_time,
        acquire_period,
        scan_folder,
        file_name,
        dets,
        **kwargs
):
    #TODO: modify for detectors that use multiple exposures per image
    """ 
    Plan stub to expose and collect images with chosen detector(s). 
    Based on spec macro `mpe_feb24_pixirad_expose` in 
    `/home/1-id/user/mpe_feb24/macros_PK/waxs_macros_201506/waxs_saxs_perframe.mac`.
    
    Uses plugin config functions `configure_cam_plugin`, `configure tiff1_plugin1`,
    etc., which are defined in cells above.
    
    PARAMETERS

    num_images *int*:
        Number of images to be collected.

    exposure_time *float*:
        Duration of each exposure in seconds. 

    acquire_period *float*:
        Time in seconds between the beginning of each exposure.

    scan_folder *str*:
        Last folder in path where files are written. Does not need to end with "/".

    file_name *str*:
        Base name given to each output file. 
        Does not include temporary suffix or suffix file number. 
        
    dets *list*:
        List of one or more detectors that will collect images in an exposure. 
        
    """
       
    #check that dets is list 
    if type(dets) != list:
        return TypeError("`dets` must be a list of detector(s). Be sure to use brackets [] and separate detectors with commas.")
        
    #starting from green field
    for det in dets: 
        
        #clear out stage_sigs
        det.stage_sigs = {}
        
        #set plugin values to defaults
        yield from det.default_setup()
    
    
    
        

#     #TODO: Check A shutter, leave option to keep closed

#     def check_beam_shutterA '{
#     # checks shutterA status, if closed waits until it is open
#     # if autoopen is not selected, this selects it
#     # JA 20May2009
#     # PUT IN HERE PARKJS 2016-02

#     epics_put("1id:AShtr:Enable",1); #enable auto-shutter
#     while(epics_get("PA:01ID:STA_A_FES_OPEN_PL.VAL")== "OFF") {
#         print "sleeping until shutter A opens, auto-shutter is enabled"
#         sleep(5)
#         epics_put("1id:shutterA:Open.PROC", 1)
#         sleep(5)
#     }
# }'

    #set up default detector gap times
    gaps = {
        "pixirad" : 0.015,
        "pilatus" : 0.01
    }
    
    for det in dets:
        #stage sigs for cam plugin
        det.cam.stage_sigs["trigger_mode"] = "Internal"  
        det.cam.stage_sigs["acquire_time"] = exposure_time
        det.cam.stage_sigs["acquire_period"] = acquire_period + gaps[det.name]
        det.cam.stage_sigs["num_images"] = num_images
        #stage sigs for tiff1 plugin
        det.tiff1.stage_sigs["num_capture"] = num_images
        det.tiff1.stage_sigs["file_path"] = os.path.join(det.WRITE_PATH,scan_folder,'')   #'' at end ensures path ends with `/`-- leave in for quality control!
        det.tiff1.stage_sigs["file_name"] = file_name
        det.tiff1.stage_sigs["auto_save"] = "Yes"       
        det.tiff1.stage_sigs["file_write_mode"] = "Single"
        
        yield from bps.stage(det)
       
    #special provision if using pixirad as a follower
    if len(dets) > 1 and pixirad in dets:
        #move some special PVs for pixirad to make it a follower
        yield from pixirad.setup_with_hydra()
        #start pixirad acquire early
        yield from bps.trigger(pixirad)

    #open shutters here
    
    
    for det in dets:
        yield from bps.trigger(det)
        
    #close shutters once collection complete here
    #unstage dets here
        
    #TODO: incorporate suspender bluesky processes to check that files are complete and beam is up 



    #open shutters
    yield from bps.mv(softglue.fs1_control, 1)
    yield from bps.mv(softglue.fs1_mask, 1)


    #close fast shutter again 
    yield from bps.mv(softglue.fs1_control,0)



    #TODO: Do we want a .par file?
   

        


 
    

     
   