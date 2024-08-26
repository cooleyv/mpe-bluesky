""" 
Plans for aligning devices at 1-ID. 
"""

__all__ = [
    "diode_align",
    "sample_align",
]

import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#Import from other folders
from .. import iconfig 
from ..devices import scaler1, saxs, sms_aero, det2_c, tomo_us_e, tomo_ds_e, tomo_c
from ..devices.instrument_in_out import device_info

#Import from other plans
from .utils import choose_motors, check_shutter_a, check_shutter_c

from apstools.plans import lineup2
from bluesky import plans as bp
from bluesky import plan_stubs as bps



#TODO: Update default arguments
#TODO: Update source code to add axis names to plots
def diode_align(
    diode_id: str = "",
    initpos_x: float = 0,
    initpos_y: float = 0,       
    rel_start_x: float = -10,        
    rel_end_x: float = 10, 
    rel_start_y: float = -10,
    rel_end_y: float = 10,         
    points: float = 51,            
    peak_factor: float = 2.5,    
    width_factor: float = 0.8,   
    nscans: float = 3               
):
    
    """ 
    Lineup and center diode in x and y where beam is most intense.  
    At a minimum, caller must specify which diode to use (`diode_id`).
    
    PARAMETERS

    diode_id "str":
        Specifies which diode to align. Choices: "saxs_in_e", "stop_in_c", "no_beam_sim". (default: "")

    initpos_x (initpos_y) *float*:
        Initial position of diode on x (y) axis. Lineup2 scan will run relative to this position. 
        (default : 0)
        
    rel_start_x (rel_start_y) *float*:
        Starting point for the scan on the x (y) axis, relative to the ``initpos``. (default: -10)
        
    rel_end_x (rel_start_y) *float*:
        Ending point for the scan on the x (y) axis, relative to the ``initpos``. (default: 10)
        
    points "int":
        Number of steps in scan. (default: 51)
        
    peak_factor *float*:
        Threshold for detected peak amplitude for ``lineup2`` to detect a peak. 
        Peak maximum must be greater than ``peak_factor*minimum``. (default: 2.5)
        
    width_factor "float":
        FWHM must be less than ``width_factor*plot_range`` (default: 0.8)
        
    nscans *int*:
        Number of scans; scanning will stop if any scan cannot find a peak. (default: 3)
        
    
    """
    
    #Specify which diode, then move nearby tomo(s) out and detector shield in
    
    if diode_id == "saxs_in_e":
        det = scaler1.channels.chan10
        motor_x = saxs.diode_x
        motor_y = saxs.diode_y
        
        yield from bps.mov(
            tomo_ds_e.x, device_info["tomo_ds_e"]["out"],
            tomo_us_e.x, device_info["tomo_us_e"]["out"],
            saxs.shield_x, device_info["saxs_shield"]["out"])
        
        #Check that shutters are open
        yield from check_shutter_a
        yield from check_shutter_c
        #yield from check_shutter_e
         
    elif diode_id == "d2_in_c":
        #TODO: specify scaler here, update det shield
        det = None
        motor_x = det2_c.beamstop_x
        motor_y = det2_c.beamstop_y
        
        yield from bps.mov(
            tomo_c.x, device_info["tomo_c"]["out"])
        
        #Check that shutters are open
        yield from check_shutter_a
        yield from check_shutter_c
        
    elif diode_id == "no_beam_sim":
        from ophyd.sim import noisy_det
        from ophyd.sim import motor as dummy_x
        from ophyd.sim import motor3 as dummy_y
        det = noisy_det
        motor_x = dummy_x
        motor_y = dummy_y
        
    elif not diode_id:
        raise ValueError("Diode (`diode_id`) is not specified. Try `diode_align??` for options.")
    
    else: raise NameError("Diode name (`diode_id`) is not recognized. Try `diode_align??` for options.")


    #Define SMS, move out of beam
    sample_stack = choose_motors()
    yield from bps.mov(sample_stack.x2, device_info[iconfig["SMS"]]["out"])
    
    input("Nearby devices moved in/out of beam. Press Enter to continue...")
    
    #Move diode to initial position
    yield from bps.mov(
        motor_x, initpos_x,
        motor_y, initpos_y)
    
    #Perform lineup scans in x and y 
    yield from lineup2(
        detectors = det,              mover = motor_x,
        rel_start = rel_start_x,      rel_end = rel_end_x, 
        points = points,              peak_factor = peak_factor, 
        width_factor = width_factor,  nscans = nscans,
        md = {"title":"Diode lineup in X"}
    )
    
    yield from lineup2(
        detectors = det,              mover = motor_y,
        rel_start = rel_start_y,      rel_end = rel_end_y, 
        points = points,              peak_factor = peak_factor, 
        width_factor = width_factor,  nscans = nscans,
        md = {"title":"Diode lineup in Y"}
    )
    
    diode_aligned_x = motor_x.position
    diode_aligned_y = motor_y.position
    
    
    #TODO: Add language for unsuccessful alignment cases. Add warning for poor fits/no peak found.
    input("Diode alignment successful. Press Enter to continue...")
    
    print(f"Diode position after {nscans} scans = {diode_aligned_x:.3f}, {diode_aligned_y:.3f}")
    
 

    
def sample_align(
    scaler_id:str = "",
    initpos_x:float = 0,
    initpos_z:float = 0,
    initrot:float = 0,       
    rel_start_x:float = -10,  
    rel_start_z:float = -10,      
    rel_end_x:float = 10,   
    rel_end_z:float = 10,       
    points:float = 51,            
    peak_factor:float = 2.5,    
    width_factor:float = 0.8,   
    nscans:float = 3  
):
    """ 
    Lineup and center a sample in x where signal intensity is least intense. 
    Performs alignment at two roty positions spaced 90 degrees apart.
    At a minimum, caller must specify which scaler to use (`scaler_id`).

    PARAMETERS

    scaler_id "str":
    Specifies which scaler to use as a signal. Choices: "saxs_in_e". (default: "")

    initpos_x (initpos_z) *float*:
    Initial position of sample on x (z) axis. Lineup2 scan will run relative to this position. (default : 0)

    initrot *float*:
    Initial position of sample on roty axis. Alignment will be performed at this position and a position 
    90 degrees CCW relative to this position. (default : 0)

    rel_start_x (rel_start_z) *float*:
    Starting point for the scan on the x (z) axis, relative to the ``initpos``. (default: -10)

    rel_end_x (rel_end_z) *float*:
    Ending point for the scan on the x axis, relative to the ``initpos``. (default: 10)

    points "int":
    Number of steps in scan. (default: 51)

    peak_factor *float*:
    Threshold for detected peak amplitude for ``lineup2`` to detect a peak. 
    Peak maximum must be greater than ``peak_factor*minimum``. (default: 2.5)

    width_factor "float":
    FWHM must be less than ``width_factor*plot_range`` (default: 0.8)

    nscans *int*:
    Number of scans; scanning will stop if any scan cannot find a peak. (default: 3)
    """
    
    #TODO: add other options, like quit or initialize a diode_align call
    input("ATTENTION! Scaler must be aligned before sample. Press Enter to continue...")
        
    #Select scaler to use
    if scaler_id == "saxs_in_e":
        det = scaler1.channels.chan10
        
        #Check that shutters are open
        yield from check_shutter_a
        yield from check_shutter_c
        #yield from check_shutter_e
        
    elif not scaler_id:
        raise ValueError("Scaler (`scaler_id`) is not specified. Try ``sample_align??`` for options.")
    
    else: raise NameError("Scaler name (`scaler_id`) is not reconigzed. Try ``sample_align`` for options.")
    
    
    
    #Define SMS, move into beam 
    sample_stack = choose_motors()
    yield from bps.mov(sample_stack.x2, device_info[iconfig["SMS"]]["in"])
    
    #TODO: make this more flexible and call sample_stack.z
    if initrot == 90:
        input("WARNING!! Initial rotation is 90, no movement will be observed.")
    
    #Move sample to initial position 
    yield from bps.mov(
        sample_stack.x, initpos_x,
        sample_stack.roty, initrot
    )
    
    #Perform lineup scan at first rotation position 
    yield from lineup2(
        detectors = det,                mover = sample_stack.x,
        rel_start = rel_start_x,        rel_end = rel_end_x,
        points = points,                peak_factor = peak_factor,
        width_factor = width_factor,    nscans = nscans,
        md = {"title": "Sample lineup at first roty position"}
    )
    
    #Rotate 90 degrees and perform second lineup scan
    yield from bps.mov(
        sample_stack.z, initpos_z,
        sample_stack.roty, initrot+90)
    
    yield from lineup2(
        detectors = det,                mover = sample_stack.z,
        rel_start = rel_start_z,        rel_end = rel_end_z,
        points = points,                peak_factor = peak_factor,
        width_factor = width_factor,    nscans = nscans,
        md = {"title": "Sample lineup at first roty position"}
    )
    
    sample_aligned_x = sample_stack.x.position
    sample_aligned_z = sample_stack.z.position
    
    
    #TODO: Add language for unsuccessful alignment cases. Add warning for poor fits/no peak found.
    input("Sample alignment successful. Press Enter to continue...")
    
    print(f"Diode position after {nscans} scans = {sample_aligned_x:.3f}, {sample_aligned_z:.3f}")
    
    
    

    


    
    
    
