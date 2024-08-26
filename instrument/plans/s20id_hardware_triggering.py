"""Plans and associated plan stubs for hardware triggering (fastsweep/ fly scans).

Currently only meant to implement Varex triggering.

FIXME: staging det not waiting with bps.stage()
FIXME: not sure where to start capture for darks and flying
FIXME: original code doesn't set acquire_period?
"""

all = [
    "taxi",
    "fly",
    "enfly"
]

import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#import bluesky basics
from bluesky import plan_stubs as bps

#import MPE devices
from ..devices.s20id_pso import *
from ..devices.varex import varex20idff
from ..devices.s20id_FPGAs import *

import time
import numpy as np



def taxi(flyer, p0, p1, taxi_timeout = 60):
    """Plan stub to trigger a fly motor to taxi to start position in 
    preparation for a flyscan. 

    Called in enfly plan.
    
    PARAMETERS
    
    p0 *float* : 
    Starting position of flyscan in EGUs (e.g., in degrees for rotation scan).

    p1 *float* : 
    Ending position of flyscan in EGUs. 

    taxi_timeout *int* : 
    Time in seconds the taxi is allowed to proceed until timeout occurs. 
    (default : 40)


    """

    try:
        yield from bps.mv(flyer.start_position, p0)
        yield from bps.mv(flyer.end_position, p1)
    except Exception as excuse:
        print(f"An error occurred in setup: {excuse}. Ending the plan early.")
        return
    
    t0 = time.time()
    yield from bps.mv(flyer.taxi.timeout, taxi_timeout)
    yield from bps.trigger(flyer.taxi, wait=True)
    t1 = time.time()
    print(f"Taxi completed in {t1-t0:.3f}s")


def fly(flyer, fly_timeout = 3600):

    """Plan stub to trigger a fly motor to fly. Typically performed after taxiing.
    Called in enfly plan. 
    
    PARAMETERS   
    
    flyer *bluesky device object* : 
      The flyer object that controls the fly motor (e.g., psofly1). 

    fly_timeout *int* :
      Time in seconds the flight is allowed to proceed until timeout occurs. 
      (default : 3600)

    """
    t0 = time.time()
    yield from bps.mv(flyer.fly.timeout, fly_timeout)
    yield from bps.trigger(flyer.fly, wait=True)
    t1 = time.time()
    print(f"Fly completed in {t1-t0:.3f}s")
    
    #TODO: add check if flyscan took the expected amount of time



def enfly(
    start_pos,
    end_pos, 
    nframes,
    ndarks,
    exposure_time, 
    scan_folder,
    file_name,
    fly_motor,  #sms_aero.roty
    flyer,
    use_save = True, 
    det = varex20idff,
    **kwargs
):
    
    """See `enfly` and `enfly_w_dark` in ensemble_fly.mac for spec macro."""
        
    #make sure things are unstaged to start 
    if fly_motor._staged.value != 'no':
        yield from bps.unstage(fly_motor)
    for det in dets:
      if det._staged.value != 'no':
         yield from bps.unstage(det)  
         det.stage_sigs = {} 

    #empty anything unwanted in stage_sigs
    fly_motor.stage_sigs = {} 
    
    #define det readout times
    gaps = {
      "varex20idff" : 0.067
    }
       
    #define gaps and other delay variables
    extra_time = 0.03
    shutterclose_delay = 0
    shutteropen_delay = 0
    total_exposure_time = exposure_time + extra_time + gaps[det.name]  #time per exposure  #FIXME: for each det???
        
    #fetch information about the fly motor (the motor PV, NOT FPGA flyer PV)
    max_speed = fly_motor.velocity.metadata["upper_ctrl_limit"] #.VMAX; deg/sec
    min_speed = fly_motor.velocity.metadata["lower_ctrl_limit"] #.VBAS; deg/sec
    max_pos = fly_motor.high_limit_travel.get()  #.HLM; deg
    min_pos = fly_motor.low_limit_travel.get()   #.LLM; deg
    time_to_accel = fly_motor.acceleration.get()  #.ACCL; sec
    resolution = fly_motor.motor_step_size.get() #.MRES; deg/step

    #calculate some information about the scan
    range = abs(end_pos - start_pos)   #Total sweep range; in deg
    num_steps = range/resolution   #Number of steps taken in total
    scan_time = total_exposure_time*nframes  #Total time for scan, not including ramp up or down
    scan_speed_sps = num_steps/scan_time #steps/sec
    scan_speed_dps = range/scan_time #degrees/sec
    scan_delta = range/nframes#deg/frame  
    
    
    #run some checks and return warnings
    if start_pos > max_pos or start_pos < min_pos: 
        Warning(f"""Start position is out of bounds. \n
                Min allowed {min_pos}, max allowed {max_pos}. \n
                Received {start_pos}.""")

    if end_pos > max_pos or end_pos < min_pos:
        Warning(f"""End position is out of bounds. \n
                Min allowed {min_pos}, max allowed {max_pos}. \n
                Received {end_pos}.""")  
        
    if scan_speed_dps > max_speed or scan_speed_dps < min_speed:
        Warning(f"""Requested scan speed is out of bounds. \n
                Min allowed {min_speed} deg/s, max allowed {max_speed} deg/s. \n 
                Calculated {scan_speed_dps} deg/s. \n 
                Adjust nframes, scan range, or exposure time.""")  
        
    #prepare detector in continuous mode (default fastsweep config)
    #TODO: potentially add kwargs for num_img, trigger_mode, image_mode
    yield from det.fastsweep_config()
    
    #set flyer params
    yield from bps.mv(
        flyer.scan_control, "Standard",
        flyer.pulse_type, "Gate",
        flyer.start_pos, start_pos, 
        flyer.end_pos, end_pos, 
        flyer.scan_delta, scan_delta,   #deg/step
        flyer.slew_speed, scan_speed_dps,   #deg/s
        flyer.detector_setup_time, total_exposure_time  #gap.det + extra_time
    )
    
    #disable PSO signal 
    yield from bps.mv(softglue.pso_signal_enable, 0)    #disable
    
    #taxi with default timeout 
    yield from taxi(
        flyer = flyer,
        p0 = start_pos, 
        p1 = end_pos, 
    )
        
    if not use_save:
        print('Not saving images. Setting to stream mode.')
        yield from bps.mv(
            det.hdf1.file_write_mode, 'Stream',
            det.hdf1.capture, 'Done',
            det.hdf1.auto_save, 'No',
            det.hdf1.num_capture, nframes+ndarks)
        
        #start capture
        yield from bps.mv(det.hdf1.capture, 1)
        
    #collect darks before the scan
    if ndarks > 0:
        print(f"Collect {ndarks} dark images before the scan.")
        
        #close shutter
        yield from bps.mv(c_shutter, 14)
        
        #set stage_sigs for collecting a dark frame
        det.cam.stage_sigs = {
            'frame_type' : "dark",
            'num_images' : ndarks,
            'trigger_mode' : "Internal",
            'acquire_time' : exposure_time,
            'acquire_period' : total_exposure_time,
            'skip_frames' : 1,
            'num_frames_skip' : 1
        }
        
        det.proc1.stage_sigs = {
            'enable_background' : 'Disable'
        }
        
        det.hdf1.stage_sigs = {
            'file_path' : os.path.join(det.WRITE_PATH,scan_folder,''),
            'file_name' : file_name,
            'auto_save' : 'Yes',
            'auto_increment' : 'Yes',
            'capture' : 'Capture'
        }
        if not use_save: 
            det.hdf1.stage_sigs['auto_save'] = "No"
        
        #implement stage_sigs
        det.stage() #FIXME: should yield from, but bps.stage() not waiting?
      
        #FIXME: start capture again here?
      
        #take darks
        yield from bps.trigger(det, wait = True)
        
        #unstage back to flyscan setup
        det.unstage()   #FIXME
        
        #re-open shutter
        yield from bps.mv(c_shutter, 13)
        
    #once darks are complete, re-enable PSO signal
    yield from bps.mv(softglue.pso_signal_enable, 1)    #enable
    
    #fly
    yield from fly(flyer = flyer)
    