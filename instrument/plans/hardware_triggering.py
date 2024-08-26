"""
Plans and associated plan stubs for hardware triggering (fastsweep/ fly scans). 

FIXME: in FPGA_configure plan stub, do we need to open/change input for FS2?
FIXME: det gaps/extra time not working/confusing???

"""

all = [
   "FPGA_configure",
   "aero_configure",
   "arrays_configure",
   "IC_scalers_configure",
   "timestamp_array_configure",
   "frame_counter_configure",
   "taxi",
   "fly",
   "fastsweep",
]

import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

import time
from bluesky import plans as bp
from bluesky import plan_stubs as bps
#from .auxiliary_ad import *

# from ..devices.s1id_FPGAs import *
# from ..devices.s1ide_motors import sms_aero
# from ..devices.s1ide_scalers import *
# from ..devices.pixiradv2 import *
# from ..devices.hydra import *
# from .hydra_support import *

#from collections import OrderedDict
import numpy as np

import os



def FPGA_configure(
    stepper = False,
):
    
    """Plan stub for configuring FPGA PVs for a flyscan.
    See `mpe_feb24_pixirad` for original SPEC macro.
    
    PARAMETERS

    stepper *Boolean* :
      Boolean that determines whether a flyscan is performed by a stepper motor. 
      (default : False)
       
    """

    ##Setting up E-hutch FPGAs (`mpe_feb24_set_Ehutch`)
    #Identical to `mpe_feb24_set_Chutch`

    #define string inputs for fake_gate
    input_flyer_value = "1ide:PSOFly1:fly CP NMS"  #FIXME: should be adjustable
    output_link_value = "1ide:sg4:BUFFER-1_IN_Signal.PROC PP NMS"

    #configure fake_gate
    yield from bps.mv(
       fake_gate.description, "AERO rot stopGATE",
       fake_gate.scan, "Passive",
       fake_gate.initial_val, 0,
       fake_gate.initial_val_disable, 0,
       fake_gate.input_flyer, input_flyer_value, #TODO: populate automatically
       fake_gate.output_execute_delay, 0.0,
       fake_gate.output_execute_option, "Transition To Zero",
       fake_gate.output_data_option, "Use CALC",
       fake_gate.calculation_record, "(B&A)?1:0",
       fake_gate.output_link, output_link_value
    )

    #TODO: Decide if we need this to switch PVs (or devices)
    if stepper: ...

    #configure acromag time_counter FPGA
    yield from bps.mv(
       time_counter.readout_desc, "Readout",
       time_counter.readout_scan, "I/O Intr"
    )

    #configure DTH_DetRdy FPGA
    yield from bps.mv(
       det_ready.mode, "DTHDetRdy",
       det_ready.clock, "0",  #FIXME
       det_ready.set_signal, "DTHDetRdy",
       det_ready.data, "0",   #FIXME
       det_ready.clear, "0!"
    )

    #Set frame readback signal
    yield from bps.mv(softglue.frame_readback, "DetExp")

    #set FPGA output signals
    #TODO: Iterate over other ports and clear them (set to 0)
    yield from bps.mv(
       softglue.port_17_out, "FS1_auto",
       softglue.port_19_out, "FS1_auto",
       #standard outputs for DetExp
       softglue3.port_17_out, "DetExpE",
       softglue3.port_18_out, "Det2ExpE",
       softglue3.port_19_out, "Det3ExpE",
       #softglue3.port_20_out, "Det4ExpE",   #FIXME: only receive error for this input value
       #standard outputs for DetTrig
       softglue2.port_11_out, "detpls",
       softglue2.port_14_out, "detpls"
    )

    #close fast shutters
    yield from bps.mv(
       softglue.fs1_mask, '0',
       softglue.fs2_mask, '0'
    )

    #reset FPGA input signals
    #TODO: Iterate over other ports and clear them (set to 0)
    yield from bps.mv(
       #set FPGA input signals to select detE
       softglue3.port_5_in, "DetExpE",
       softglue3.port_25_in, "Det2ExpE",
       softglue3.port_17_in, "Det3ExpE", 
       #softglue3.port_8_in, "Det4ExpE",  #FIXME: only receive error for this input value
       #standard inputs for DetExp
       softglue.port_1_in, "Sweep", 
       softglue.port_2_in, "DetPls", 
       softglue.port_3_in, "DetExp", 
       softglue.port_8_in, "DTHDetRdy", 
       #fake zeroes
       #softglue2.port_25_in, '0',  #FIXME: not able to put or mv PV, only accepts str
       #softglue2.port_26_in, '0',  #FIXME: not able to put or mv PV, only accepts str
       #standard DetTrig inputs
       #softglue2.port_1_in, '1', #FIXME: not able to put or mv PV, only accepts str
       softglue2.port_2_in, 'detpls')

    #keep fs1 closed, then change to detExp control
    yield from bps.mv(
       softglue.fs1_mask, '0',
       softglue.fs1_control, "DepExp")
    
    #keep fs1 open
    yield from bps.mv(softglue.fs1_mask, '1')

    #set detector status monitor 
    yield from bps.mv(det_status_monitor.value, 9)

    print("det_status_monitor ok")


def aero_configure(
      start_pos,
      end_pos, 
      nframes,
      scan_speed_dps,
      gap_time,   #det_gap + extra_time
      flyer,   #flyer controller
      taxi_timeout = 40 #TODO: calculate this; define here since specific to motor
):

   """Plan stub to configure sms_aero.roty and associated PSO controller.
   Includes calling taxiing plan stub.
   Used in fastsweep plan. 

   PARAMETERS

   start_pos *float* :
      Starting position of flyscan in EGUs (e.g., in degrees for rotation scan).

   end_pos *float* : 
      Ending position of flyscan in EGUs. 

   nframes *int* :
      Number of frames to be collected during flyscan. 

   scan_speed_dps *float* :
      Desired scan speed calculated from motor parameters, `nframes`, and 
      scan range. Given in degrees per second. 

   gap_time *float*:
      The gap time in seconds between frames. Calculated as det_gap + extra_time. 

   flyer *bluesky device object* : 
      The flyer object that controls the fly motor (e.g., psofly1)

   taxi_timeout *int* : 
      Time in seconds the taxi is allowed to proceed until timeout occurs. 
      (default : 40)
   
   """

   #disable FPGA pulses
   yield from bps.mv(softglue4.pso_pulses, '0') #FIXME: only accepts string input

   #clear GATE state- execute PROC
   yield from bps.trigger(softglue4.clear_gate)

   #calculating values for PSO fields
   range = abs(end_pos-start_pos)   #in deg (total scan)
   scan_delta = range/nframes #deg/frame

   #populate fields in flyer MEDM window
   yield from flyer.configure(
      pulse_type = "Gate",
      start_pos = start_pos, 
      end_pos = end_pos, 
      scan_speed_dps = scan_speed_dps, 
      scan_delta = scan_delta, 
      gap_time = gap_time
   )
   
   #perform taxi to backoff distance
   yield from taxi(
      flyer = flyer, 
      p0 = start_pos, 
      p1 = end_pos,
      taxi_timeout = taxi_timeout
   )

   #clear GATE state- execute PROC
   yield from bps.trigger(softglue4.clear_gate)

   #enable FPGA pulses and enable fakeGATE stop
   yield from bps.mv(
      softglue4.pso_pulses, '1', #FIXME: only accepts string input
      fake_gate.initial_val_disable, 1    #.B field
   )



def arrays_configure(
      array,
      userCalc_name, 
      IC_suffix
):
   
   """Plan stub for setting up the userArrayCalc fields. 
   Called in IC_scalers_configure plan stub.
   
   PARAMETERS 

   array *bluesky device object* :
      Array object to be configured. 

   userCalc_name *str* :
      Nickname given to description field of `array`.

   IC_suffix *str* :
      Suffix describing fields related to the ion chamber. 


   """

   #generate string inputs
   array_length = 8000
   in_link_a_value = scaler2.prefix + IC_suffix + " NPP NMS"
   in_link_b_value = scaler2.prefix + "_cts.A NPP NMS"
   in_link_aa_value = scaler2.prefix + IC_suffix + " CP NMS"
   out_link_value = array.prefix + ".BB NPP NMS"
   bb_value = np.zeros(array_length)

   #set values
   yield from bps.mv(
      array.description, userCalc_name, 
      array.number_used, array_length,
      array.scan, "Passive",
      array.in_link_a, in_link_a_value, 
      array.in_link_b, in_link_b_value,
      array.in_link_c, "",    #disabled
      array.c_value, 0.0, 
      array.in_link_aa, in_link_aa_value, 
      array.in_link_bb, "",   #storage array
      array.bb_value, bb_value,   #reset-- must be an array
      array.calc_record, "C?(BB>>1)+AA:BB",  #formula used
      array.out_execute_delay, 0.0, 
      array.event_to_issue, 0,
      array.out_execute_option, "Every Time",
      array.out_data_option, "Use CALC",
      array.out_link, out_link_value, 
      array.wait, "NoWait"
   )



def IC_scalers_configure():
   
   """Plan stub to configure IC scalers.
   Called in fastsweep plan."""

   #configure scaler2
   yield from bps.mv(
      scaler2.count_mode, "OneShot",   #.CONT
      scaler2.normalized_counts, "Cts/sec",  #_calc_ctrl.VAL
      scaler2.enable_calcs, "ENABLE", #_calcEnable.VAL
      scaler2.delay, 0.0,   #.DLY
      scaler2.update_rate, 2.0,   #.RATE; Hz
      scaler2.count, "Done"   #.CNT
   )

   #collect scaler2 gates in an array to iterate through them 
   scaler2_gates = [
      scaler2.channels.chan01.gate,
      scaler2.channels.chan02.gate,
      scaler2.channels.chan03.gate,
      scaler2.channels.chan04.gate,
      scaler2.channels.chan05.gate,
      scaler2.channels.chan06.gate,
      scaler2.channels.chan07.gate,
      scaler2.channels.chan08.gate,
      scaler2.channels.chan09.gate,
      scaler2.channels.chan10.gate,
      scaler2.channels.chan11.gate,
      scaler2.channels.chan12.gate,
      scaler2.channels.chan13.gate,
      scaler2.channels.chan14.gate,
      scaler2.channels.chan15.gate,
      scaler2.channels.chan16.gate,
   ]

   #configure scaler 2 gates
   for gate in scaler2_gates:
      yield from bps.mv(gate, "N")

   #define string inputs for scaler trigger
   out_link_value = scaler2.prefix + ".CNT PP NMS"

   #configure scaler trigger
   yield from bps.mv(
      scaler_trigger.description, "DetPulseToScaler",
      scaler_trigger.scan, "Passive", 
      scaler_trigger.a_value, 0,
      scaler_trigger.b_value, 0,
      scaler_trigger.in_link_a, "", 
      scaler_trigger.out_execute_option, "On Change",
      scaler_trigger.out_data_option, "Use OCAL",
      scaler_trigger.calc_record, "(A&B)",
      scaler_trigger.out_calc, "(A&B)?1:0",
      scaler_trigger.out_link, out_link_value
   )

   #configure the userArrayCalc fields using a smaller plan stub 
   yield from arrays_configure(
      array = sample_monitor_array,
      userCalc_name = "Fastsweep MonCnt",
      IC_suffix = "_cts2.B"   #standard IC in E, after the DS slit, before the sample IC5-E
   )

   yield from arrays_configure(
      array = sample_transmission_array,
      userCalc_name = "Fastsweep TransmCnt",
      IC_suffix = "_cts2.C"   #pin diode after the sample IC4-E
   )

   yield from arrays_configure(
      array = energy_monitor_array, 
      userCalc_name = "Fastswep E-MonCnt",
      IC_suffix = "_cts2.A"   #after US Kohzu slits in E, IC3-E
   )

   yield from arrays_configure(
      array = intensity_transmission_array, 
      userCalc_name = "Fastswp E-TransmCnt",
      IC_suffix = "_cts1.D"   #IC2-E split IC, bottom part
   )

   yield from arrays_configure(
      array = integrated_time_array,
      userCalc_name = "Fastswp Integr.Ticks",
      IC_suffix = "_calc5.VAL"
   )



def timestamp_array_configure(
      nframes,
      det
):
   
   """Plan stub to confiure the timestamp array for flyscan. 
   Called in fastsweep plan. 
   
   PARAMETERS
   
   nframes *int* :
      Number of frames to be collected during flyscan.
      
   det *bluesky area detector object* :
      Area detector that will capture images during flyscan.
   """
   
   #define input values for timestamp_array
   array_length = 8000
   in_link_aa_value = det.prefix + "image1:TimeStamp_RBV CP NMS"  #FIXME: different for hydra
   out_link_value = timestamp_array.prefix + ".BB NPP NMS"
   bb_value = np.zeros(array_length)

   yield from bps.mv(
      timestamp_array.description, "TimeStamps",
      timestamp_array.number_used, array_length,
      timestamp_array.scan, "Passive",
      timestamp_array.in_link_a, "",
      timestamp_array.in_link_b, "", 
      timestamp_array.in_link_c, "",
      timestamp_array.a_value, nframes,
      timestamp_array.b_value, 0,
      timestamp_array.c_value, 0,
      timestamp_array.in_link_aa, in_link_aa_value,   #different for GE_NEW
      timestamp_array.in_link_bb, "",  #different for GE_NEW
      timestamp_array.in_link_dd, "", #different for GE_NEW
      timestamp_array.bb_value, bb_value,
      timestamp_array.calc_record, "C?(BB>>1)+AA:BB",
      timestamp_array.out_execute_delay, 0.0,
      timestamp_array.event_to_issue, 0,
      timestamp_array.out_execute_option, "Every Time", 
      timestamp_array.out_data_option, "Use CALC", 
      timestamp_array.out_link, out_link_value, 
      timestamp_array.wait, "NoWait"
   )



def frame_counter_configure(
      nframes
):
   """Plan stub to configure the frame counter transform record.
   Called in fastsweep plan.
   
   PARAMETERS

    nframes *int* :
      Number of frames to be collected during flyscan.
   
   """

   out_link_b_value = frame_counter.prefix + ".B NPP NMS"
   out_link_d_value = det_pulse_to_ad.prefix + ".C NPP NMS"  #might change with det + fly_motor

   yield from bps.mv(
      frame_counter.description, "FrameCounter",
      frame_counter.scan, "Passive",
      #clear input links
      frame_counter.in_link_a, "",
      frame_counter.in_link_b, "",
      frame_counter.in_link_c, "",
      frame_counter.in_link_d, "",
      frame_counter.in_link_e, "",
      frame_counter.comment_a, "a nframes",
      frame_counter.a_value, nframes,  #logs the starting number
      frame_counter.expression_a, ""   #clear
   )

   #because order is very important, make separate bps.mv() calls for 
   #subsequent fields. 
   #b group
   yield from bps.mv(
      frame_counter.comment_b, "b counter",  #counter
      frame_counter.expression_b, "C?(B-1):B",  #counting down
      frame_counter.b_value, 0   #just for initializing
   )
   #c group
   yield from bps.mv(
      frame_counter.comment_c, "c enable",   #group enables the counter
      frame_counter.expression_c, "C?(B-1):B",  #disabled for now
      frame_counter.b_value, 0   #clear
   )
   #d group
   yield from bps.mv(
      frame_counter.comment_d, "d disbl DetP_AD",  #group enables the DetPulseToAD signals
      frame_counter.d_value, 0,  #disabled for now
      frame_counter.expression_d, "(B<=0)?0:1"  #if det triggering should be stopped
   )
   #handling outputs and other options
   yield from bps.mv(
      frame_counter.calc_option, "Conditional",
      frame_counter.out_link_b, out_link_b_value, 
      frame_counter.out_link_d, out_link_d_value
   )
   #set frame number
   yield from bps.mv(frame_counter.b_value, nframes+1)







def taxi(flyer, p0, p1, taxi_timeout):

    """Plan stub to trigger a fly motor to taxi to start position in 
    preparation for a flyscan. 

    Called in aero_configure plan stub.
    
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
    Called in fastsweep plan. 
    
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










def fastsweep(  
      start_pos,
      end_pos,
      nframes,
      exposure_time,
      scan_folder,
      file_name,
      scalers, #list
      fly_motor, #sms_aero.roty,
      dets,
      use_hydra,
      PSOflyer = True,
      **kwargs
):
   """See `fastsweep` from `osc_fastsweep_FPGA_hydra.mac`
   Plan to perform fastsweep command with a flyer and detector.
   
   Outermost command for the fly scan (not including stepper scan layers
   outside of inner fly scan). 

   PARAMETERS

   start_pos *float* :
      Starting position of flyscan in EGUs (e.g., degrees for rotation scan).

   end_pos *float* : 
      Ending position of flyscan in EGUs. 

   nframes *int* :
      Number of frames to be collected during flyscan. 

   exposure_time *float* : 
      Duration of each expsosure in seconds. 

   scan_folder *str* :
      Last folder in path where files are written. Does not need to end with "/".

   file_name *str* :
      Base name given to each output file.
      Does not include temporary suffix or file number. 

   fly_motor *bluesky motor object* : 
      Motor that will be used to perform flyscan. 
      Must be entered in bluesky syntax (e.g., sms_aero.roty)

   use_hydra *bool* : 
      True/False value whether to use hydra or not (can be with or without pixirad).
   
   det *bluesky area detector objet* :
      Area detector that will capture images during flyscan. 

   PSOflyer *Boolean* :
      Boolean that decides whether a PSO controller is used to control `fly_motor`.


   """

   #make sure things are unstaged to start 
   if fly_motor._staged.value != 'no':
      yield from bps.unstage(fly_motor)
   for det in dets:
      if det._staged.value != 'no':
         yield from bps.unstage(det)  
         det.stage_sigs = {} 

   #empty anything unwanted in stage_sigs
   fly_motor.stage_sigs = {} 
      
  
   gaps = {
      "pixirad" : 0.05,
      "ge1" : 0.15,
      "ge2" : 0.15,
      "ge3" : 0.15,
      "ge4" : 0.15
   }

   #define gaps and other delay variables
   extra_time = 0.03
   #TODO: Define shutter variables in shutter object, not here
   shutterclose_delay = 0
   shutteropen_delay = 0
   total_exposure_time = exposure_time + extra_time + gaps[det.name]  #time per exposure  #FIXME: for each det???


   #fetch information about the scan from AD
   first_frame_number = det.tiff1.file_number.get()   #First frame number recorded by AD
   print(f"First frame number is {first_frame_number}")

   #fetch information about the fly motor (the motor PV, NOT FPGA flyer PV)
   max_speed = fly_motor.velocity.metadata["upper_ctrl_limit"] #.VMAX; deg/sec
   min_speed = fly_motor.velocity.metadata["lower_ctrl_limit"] #.VBAS; deg/sec
   max_pos = fly_motor.high_limit_travel.get()  #.HLM; deg
   min_pos = fly_motor.low_limit_travel.get()   #.LLM; deg
   time_to_accel = fly_motor.acceleration.get()  #.ACCL; sec
   resolution = fly_motor.motor_step_size.get() #.MRES; deg/step

   #check: Is time_to_accel configured?
   if time_to_accel == 0:
      raise ValueError("ACCL is not set for fly_motor.")
   
     #check: Is max_speed configured? 
   if max_speed == 0:
      raise ValueError("VMAX is not set for fly_motor.")

   """Per the EPICS databse, the intent of VBAS is to prevent the motor
   from moving at speeds slow enough to excite its resonance, which can
   cause the motor to miss steps. The motor is expected to accelerate from
   a stand-still to VBAS in one motor pulse. The motor speed is expected
   to increase linearly with time from the base speed (VBAS) to the full
   speed (VELO) in ACCL seconds. At the end of a motion, the speed is 
   expected to decrease similarly to VBAS."""

   print("Calculating details about the scan...")
   #calculate details about the scan
   range = abs(end_pos - start_pos)   #Total sweep range; in deg
   num_steps = range/resolution   #Number of steps taken in total
   scan_time = total_exposure_time*nframes  #Total time for scan, not including ramp up or down
   scan_speed_sps = num_steps/scan_time #steps/sec
   scan_speed_dps = range/scan_time #degrees/sec
      
   #check: Are positions in bounds?
   if start_pos > max_pos or start_pos < min_pos:
      raise ValueError("Starting position is out of range.")
   
   if end_pos >max_pos or start_pos < min_pos: 
      raise ValueError("Ending position is out of range.")
   
   #check: Is speed within bounds? 
   if scan_speed_dps > max_speed or scan_speed_dps < min_speed:
      raise ValueError("Requested scan speed is out of bounds.")
   print("Completed checks on velocity and position limits.")

   #calculate ramping parameters
   #e.g., number of motor steps performed in time it takes to open shutter (`steps_to_open`)
   steps_to_open = int(shutteropen_delay * scan_speed_sps)  
   steps_to_close = int(shutterclose_delay * scan_speed_sps)
   steps_to_accelerate = (scan_speed_sps - min_speed)/2 *time_to_accel  #aka asteps
   degs_to_accelerate = steps_to_accelerate * resolution    #aka arange

   #FIXME: Not sure if these are correct
   rampup_steps = steps_to_open + steps_to_accelerate
   rampup_time = (time_to_accel + shutteropen_delay)
   #assume acceleration/deceleration are symmetric
   rampdown_steps = steps_to_close + steps_to_accelerate
   rampdown_time = (time_to_accel + shutterclose_delay)

   print("Some scan information:")
   print(f"Scan time not incl. rampup or rampdown = {scan_time:.3f} sec.") 
   print(f"Desired scan speed = {scan_speed_sps:.3f} steps/sec or {scan_speed_dps:.3f} deg/sec.")
   print(f"Steps to open shutter = {steps_to_open:.0f}. Steps to close shutter = {steps_to_close:.0f}.")
   print(f"Steps to accel = {steps_to_accelerate:.0f}.")
   print(f"Degrees needed to accel = {degs_to_accelerate:.3f}.")

   #TODO: Add code for slave stage parameters?




   #FIXME: Calculating timeouts needs work!!!
   # #calculate taxi_timeout and fly_timeout (with a little extra room)
   # fly_fudge = 5  #Fudge factor
   # fly_timeout = (rampup_time + scan_time + rampdown_time) * fly_fudge
   # print(f"The fly_timeout is {fly_timeout}. The predicted fly_time is {fly_timeout/fly_fudge}.")
   
   # """taxi_time is a rough calculation since it does not take into
   # account the backoff distance, accleration time, etc. taxi_timeout
   # has a larger fudge factor that just makes sure the timeout is longer than 
   # the time needed to actually taxi, based on this approximation.""" 
   # current_pos = fly_motor.position
   # taxi_dist = abs(current_pos - start_pos)  
   # #note: fly_motor is staged later, so taxi velocity will not be scan_speed
   # taxi_time = taxi_dist / fly_motor.velocity.get()
   # taxi_fudge = 10
   # taxi_timeout = taxi_time * taxi_fudge   #Fudge factor of 10
   # print(f"The taxi_timeout is {taxi_timeout}.")

   print("Beginning hardware configuration for fastsweep...")


   #make sure plugins are enabled and primed for data collection 
   #NOTE: this function is contained in `DET.py` file, not here
   for det in dets:
      yield from det.enable_plugins()

   #set tiff1 plugin to defaults
   #FIXME: needs updated entries/do this elsewhere
   #yield from configure_tiff1(det = det)

   #configure  detector for fastsweep (permanent changes)
   #NOTE: this function is contained in `DET.py` file, not here
   for det in dets:
      yield from det.fastsweep_config(nframes = nframes)
   print(f"{det.name} config: success.")

   #configure FPGAs needed for fastsweep
   yield from FPGA_configure(**kwargs)
   print("FPGA config: success.")

   #select flyer (FPGA PV, NOT the motor PV)
   if PSOflyer:
      flyer = psofly1

   #configure aero fly stage and taxi to backoff position
   yield from aero_configure(
      start_pos = start_pos, 
      end_pos = end_pos,
      nframes = nframes, 
      scan_speed_dps = scan_speed_dps, 
      gap_time = det_gap+extra_time, 
      flyer = flyer, 
   )
   print("Flyer config: success.")
 
   #configure IC scalers   #FIXME: not sure if this happens before or after aero
   yield from IC_scalers_configure()
   print("IC_scaler config: success.")

   #configure timestamp_array
   yield from timestamp_array_configure(nframes = nframes, det = det)
   print("Timestamp_array config: success.")

   #configure frame_counter
   yield from frame_counter_configure(nframes = nframes)
   print("Frame_counter config: success.")
   print("Configuration concluded.")

   """Per the EPICS database, TP specifies for long, in seconds, the 
   scaler is to count if no other preset stops it. TP is effectively 
   a proxy for the preset field PR1. Whenever TP changes, the record will
   set PR1 = TP*FREQ and otherwise behave as though the user had changed
   PR1."""

   #arm scalers
   #FIXME: Really not sure about this part
   #Not sure if stage is configured to control the scaler
   #arm scalers (can't stage an EpicsSignal, so just mv directly)  
   # for scaler in scalers:
   #    yield from bps.mv(
   #       scaler.count_delay, rampup_time,
   #       scaler.preset_time, scan_time, 
   #       scaler.count, 1    #should this be moved to a trigger command??
   #    )
   

 

   #enable detector pulses to IC scaler(E-hutch)
   in_22Do_vlaue = scaler_trigger.prefix + ".A PP NMS"
   yield from bps.mv(softglue4.in_22Do, in_22Do_vlaue)  
   yield from bps.mv(softglue4.in_22IntEdge, "Both") 
   yield from bps.mv(scaler_trigger.b_value, 1) #enable

   #enable IC_scalers
   yield from bps.mv(
      sample_monitor_array.c_value, 1,
      sample_transmission_array.c_value, 1, 
      energy_monitor_array.c_value, 1, 
      intensity_transmission_array.c_value, 1,
      integrated_time_array.c_value,1
   )

 

   #if using hydra, do hydra-specific config here (not for GE panels)
   if use_hydra:
      yield from hydra.fastsweep_config()

      #if using hydra configuration in combination with SAXS method, extra setup needed
      if pixirad in dets:  
         yield from pixirad.config_with_waxs(nframes = nframes)   #MUST happen after det.fastsweep_config()
         yield from softglue4_menu.saxs_waxs_config()
         yield from softglue.saxs_waxs_config()

  

   #clear det_ready and enable/disable det pulses and counters
   yield from bps.mv(
      det_ready.clear, "0!",
      det_pulse_to_ad.b_value, 0,   #disable
      frame_counter.c_value, 1,  #enable
      timestamp_array.c_value, 1 #enable
   )
   print("Scalers and pulses enabled.")

   
   #organize last bits of stage_sigs for AD cam
   for det in dets:
      det.tiff1.stage_sigs["file_path"] = os.path.join(det.WRITE_PATH,scan_folder,'')
      det.tiff1.stage_sigs["file_name"] = file_name
      det.tiff1.stage_sigs["auto_save"] = "Yes"
      det.tiff1.stage_sigs["auto_increment"] = "Yes"
      det.tiff1.stage_sigs["capture"] = "Capture"  #FIXME: not sure if this applies to pixirad
      
      #special consideration for retigas
      if det.name.startswith("retiga"): 
         det.cam.stage_sigs["acquire_time"] = exposure_time
         det.cam.stage_sigs["acquire_period"] = 0  #retiga acquire period must be 0
         
      elif det.name == "pixirad" and hydra: 
         det.cam.stage_sigs["aquire_time"] = exposure_time + 0.138 - gaps[det.name]
         det.cam.stage_sigs["acquire_period"] = exposure_time + 0.138 - gaps[det.name] + 0.05
      
      else:
         det.cam.stage_sigs["acquire_time"] = exposure_time
         det.cam.stage_sigs["acquire_period"] = exposure_time + gaps[det.name]
         
      
      det.cam.stage_sigs["acquire"] = 1

   
   #organize up stage_sigs for the motor for staging right before fly scan 
   fly_motor.stage_sigs["velocity"] = scan_speed_dps
   fly_motor.stage_sigs["backlash_dist"] = 0.0 #turn off backlash 
   #FIXME: does backlash need to be off for taxiing?? 

   #stage fly_motor and detector (similar to arming)
   yield from bps.stage(fly_motor)
   for det in dets:
      yield from bps.stage(det)
      print(f"{det.name} staged successfully.")
   print(f"All dets and {fly_motor.name} staged. Prepared to fly.")

   #arm the strucks last FIXME: do we need this always, or just when using SAXS + WAXS? FIXME: is this in the right spot?
   yield from bps.mv(
      struck.channel_advance, "External",
      struck.erase_start, "Erase"
   )

   #fly here (press busy button to fly)
   print("Flying...")
   yield from fly(
      flyer = flyer,
      #fly_timeout = fly_timeout
   )


   #fetch information about the scan from AD
   last_frame_number = det.tiff1.file_number.get()   #First frame number recorded by AD
   print(f"Last frame number is {last_frame_number}")

   #TODO: add option for pixirad nframes not matching nframes argument
   for det in dets:
      if det.cam.num_images_counter.get() != nframes:
         print("WARNING! Number of images collected does not match nframes for {det.name}.")
         print(f"Number of images collect = {det.cam.num_images_counter.get()}.")
         print(f"Number frames request = {nframes}.")
      else: 
         print(f"Acquired expected number of frames for {det.name}.")

   print("Deconfiguring and disabling.")


   #TODO: rising and falling gate (sofglue.gate)?? Not sure if needed

   #if using, stop hydra
   if use_hydra: 
      yield from hydra_stop_capture()

   #unstage fly_motor and detector (disarm)
   for det in dets:
      yield from bps.unstage(det)
   yield from bps.unstage(fly_motor)

   #clear det_ready and disable det pulses and counters
   yield from bps.mv(
      det_pulse_to_ad.b_value, 0,   #disable
      frame_counter.c_value, 0,  #disable
      timestamp_array.c_value, 0 #disable
   )
   print("Scalers and pulses enabled.")


   #disable pulses -- specific to aero and rams
   yield from bps.mv(softglue4.pso_pulses, '0') 
   yield from bps.trigger(softglue4.clear_gate) #trigger PROC
   yield from bps.mv(fake_gate.initial_val_disable, 0)

   #disable IC_scalers
   yield from bps.mv(
      sample_monitor_array.c_value, 0,
      sample_transmission_array.c_value, 0, 
      energy_monitor_array.c_value, 0, 
      intensity_transmission_array.c_value, 0,
      integrated_time_array.c_value, 0
   )

   #disable detector pulses to IC scaler(E-hutch)
   yield from bps.mv(softglue4.in_22IntEdge, "None")
   yield from bps.mv(softglue4.in_21IntEdge, "None")  #FIXME: This is not configured to begin with
   #FIXME: do we need in_17IntEdge too?? Or just for stepper?
   yield from bps.mv(scaler_trigger.b_value, 0)

   #disable det_pulse and frame_counter
   yield from bps.mv(
      det_pulse_to_ad.b_value, 0,
      frame_counter.c_value, 0,
      det_ready.clear, "0!"
   )

 
   #FIXME:
   # #disarm scalers
   # for scaler in scalers: 
   #    yield from bps.mv(scaler.count, 0)

   print("Deconfiguring complete. Getting IC counts")

   #get the arrays (names preserved from spec macro)
   moncnt   = sample_monitor_array.bb_value
   trcnt    = sample_transmission_array.bb_value
   Emoncnt  = energy_monitor_array.bb_value
   Etrcnt   = intensity_transmission_array.bb_value
   cntticks = integrated_time_array.bb_value

   #FIXME: not sure what to do with these after this? (`printdoublearrayshort`)

   print("End of flyscan.")




