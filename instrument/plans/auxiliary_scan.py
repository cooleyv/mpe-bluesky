""" 
Plan stubs that are called in larger scanning plans. 

:see: /home/1-id/s1iduser/mpe_feb24/macros_PK/generic_useful.mac
"""

all = [
    "choose_motors",
    "check_shutter_a",
    "check_shutter_c",
]

import logging
import time 
logger = logging.getLogger(__name__)
logger.info(__file__)

from .. import iconfig
from ..devices import shutter_a, shutter_c
from ..devices.s1ide_motors import sms_aero
# def get_pv(input):
    
# def estimate_time():

# def is_beam_on():
#     #FIXME: output doesn't quite match input function
#     return aps.machine_status.get()


        

def choose_motors(use_iconfig =True, **kwargs):
    
    if use_iconfig:
        
        SMS = iconfig["EXPERIMENT"]["SMS"]
        IMG = iconfig["EXPERIMENT"]["DETECTORS"]["MOTOR_STACKS"]
        SCAT = iconfig["EXPERIMENT"]["DETECTORS"]["MOTOR_STACKS"]
        SAXS = iconfig["EXPERIMENT"]["DETECTORS"]["MOTOR_STACKS"]
        OTHER = iconfig["EXPERIMENT"]["DETECTORS"][""]
        
    #Select SMS motors
    if SMS == "sms_aero":
        sample_stack = sms_aero        
        #samplex_out = 10 call this from pickled dataframe
    elif SMS == "mts":
        sample_stack = mts
    elif SMS == "sms_lab":
        sample_stack = sms_lab
    elif SMS == "owis":
        sample_stack = owis
    elif SMS == "rams3":
        sample_stack = rams3
    else:
        raise NameError("SMS is not defined in iconfig or not recognized.") 

    #Select tomo motors
    if IMG:
        #if IMG == "tomo_b":
        if IMG == "tomo_c":
            imaging_stack = tomo_c
        elif IMG == "tomo_us_e":
            imaging_stack = tomo_us_e
        elif IMG == "tomo_ds_e":
            imaging_stack = tomo_ds_e
        else:
            raise NameError("Imaging motor stack is not recognized.")
    else:
        logger.warning("Imaging motor stack not used.")
    
    #Select scattering motors    
    if SCAT:
        if SCAT == "hydra":
            scattering_stack = hydra
        elif SCAT == "det2_c":
            scattering_stack = det2_c
        elif SCAT == "det2_e":
            scattering_stack = det2_e
        elif SCAT == "nearfield":
            scattering_stack = nearfield
        elif SCAT == "vff":
            scattering_stack = vff
        else:
            raise NameError("Scattering motor stack is not recognized.")
    else:
        logger.warning("Scattering motor stack is not used.")
        
    #Select saxs motors
    if SAXS:
        if SAXS == "saxs":
            saxs_stack = saxs 
        else:
            raise NameError("SAXS motor stack is not recognized.")
    else:
        logger.warning("SAXS motor stack is not used.")
        
    #Select other motors
    if OTHER:
        if OTHER == "four_circle":
            other_stack = fourc
        else: 
            raise NameError("Other motor stack is not recognized.")
    else:
        logger.warning("Other motor stack is not used.")
                        
                        
    return sample_stack, imaging_stack, scattering_stack, saxs_stack, other_stack
    

def check_shutter_a():
    """For use in plans. To simply see if the shutter is open, use `shutter_a.IsOpen`"""
    
    if shutter_a.isClosed:
        print("WARNING! Shutter A is closed. Do you want to request to open it? y/n")
        
        choice = input().lower()
        if choice == 'y':
            yield from(shutter_a.open())

def check_shutter_c():
    if shutter_c.isClosed:
        print("WARNING! Shutter C is closed. Do you want to request to open it? y/n")
        
        choice = input().lower()
        if choice == 'y':
            yield from(shutter_a.open())
            