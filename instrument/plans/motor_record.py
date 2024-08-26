""" 
Plans for taking a snapshot of the Setup window of a motor record.

#TODO: Check MPEMotor works
"""

__all__ = [
    "fetch_single_motrec",
    "make_temp_motor",
    "ioc_full_record",
    "single_motor_snapshot",
    "device_snapshot",
    "write_single_motrec"
]

import logging 
logger = logging.getLogger(__name__)
logger.info(__file__)

#import bluesky stuff
from bluesky import plan_stubs as bps

#import MPE custom devices
from ..devices import MPEMotor

#import other stuff
import pandas as pd
import os
import numpy as np
import datetime


def fetch_single_motrec(
    motor,      
):
    
    """Function for fetching motor record for single Bluesky motor.
    Returns a dataframe containing the motor record information.
    
    PARAMETERS
    
    motor *MPEMotor object* : 
        Motor that you want to fetch the setup record for.
    
    """

    #check that motor is MPEMotor type; will not work otherwise
    if motor.__class__.__name__ != "MPEMotor":
        return ValueError(f"Motor is not configured in Bluesky as MPEMotor. Couldn't fetch {motor.prefix} info.")

    #create a dictionary to link human-readable name to values
    mr_dict = {
        'Motor name' : motor.description.get(),
        'Direction' : motor.direction.get(as_string = True),
        'Precision' : motor.display_precision.get(),
        'Max. speed (Rev/s)' : motor.max_speed_rps.get(),
        'Speed (Rev/s)' : motor.speed_rps.get(),
        'Backlash speed (Rev/s)' : motor.backup_speed_rps.get(), 
        'Base speed (Rev/s)' : motor.base_speed_rps.get(),
        'Accel time (s)' : motor.acceleration.get(),
        'Backlash accel time (s)' : motor.backup_acceleration.get(),
        'Backlash distance (EGU)' : motor.backlash_dist.get(),
        'Move fraction' : motor.move_fraction.get(),
        'Home speed (EGU/s)' : motor.home_speed_eps.get(),
        #'Units' : motor.egu.get(),
        'Motor resolution (Steps/Rev)' : motor.motor_res_spr.get(),
        'Motor resolution (EGU/Rev)' : motor.motor_res_epr.get(),
        'Motor resolution (EGU/step)' : motor.motor_step_size.get()
    }

    #create dataframe for single motor
    df = pd.DataFrame(data = mr_dict, index = [motor.prefix])

    #return for inspection 
    return df

def make_temp_motor(motor_oms):
    """Small function to make a temporary MPE motor.
    Returns an MPEMotor object with the motor information. 
    Implements checks if the motor is not connected.
    
    PARAMETERS
    
    motor_oms *str* : 
        Prefix and name of the motor you want to make a temp motor for (e.g., "1idc:m99")
    
    """

    try:
        temp_motor = MPEMotor(motor_oms, name = "temp_motor")
        temp_motor.wait_for_connection()

    except TimeoutError: 
        print(f"Could not find motor record for {motor_oms}.")
    
    else: 
        return temp_motor
   
    
def ioc_full_record(
ioc = "1idc",
total_channels = 120,
save_path = "/home/beams/S1IDUSER/bluesky/user/",
show_df = True,
save_to_csv = True       
):

    """Function to fetch motor record for all motors on an IOC from EPICS. 
    Saves the record as a csv file in specified location.
    
    
    PARAMETERS 
    
    ioc *str* : 
        IOC prefix of motor series to save to a record. (default : "1idc")
    
    total_channels *int* :
        Total number of motor channels contained in the IOC (default : 120)
    
    save_path *str* : 
        Absolute save location for output csv file. (default : "")
        
    show_df *bool* : 
        Turns on and off the ability to print out the dataframe 
        containing the motor record as it is created. (default : True)
        
    save_to_csv *bool* : 
        Turns on and off the ability to save the output csv with the motor 
        record. (default : True)
    """

    #check string inputs
    if ioc[-1]  == ":":
        ioc = ioc[:-1]  #removes ':'

    #make list of channels to fetch information from 
    channels = list(map(str, np.linspace(1, total_channels, total_channels, dtype = int)))
    motors = [ioc + ":m" + x for x in channels]

    #make a dictionary connecting column titles to field names
    field_dict = {
        'Motor name' : 'DESC',
        'Direction' : 'DIR',
        'Precision' : 'PREC',
        'Max. speed (Rev/s)' : 'SMAX',
        'Speed (Rev/s)' : 'S',
        'Backlash speed (Rev/s)' : 'SBAK', 
        'Base speed (Rev/s)' : 'SBAS',
        'Accel time (s)' : 'ACCL',
        'Backlash accel time (s)' : 'BACC',
        'Backlash distance (EGU)' : 'BDST',
        'Move fraction' : 'FRAC',
        'Home speed (EGU/s)' : 'HVEL',
        #'Units' : motor.egu.get(),
        'Motor resolution (Steps/Rev)' : 'SREV',
        'Motor resolution (EGU/Rev)' : 'UREV',
        'Motor resolution (EGU/step)' : 'MRES'
    }

    print("Dictionary initialized.")

    #initialize a dataframe to append each motor to    
    motor_record_df = pd.DataFrame(data = field_dict, index = ['Field names'])    

    #TODO: add a try/except statement to skip motors not online; return a warning
    #for each motor channel, make a temporary device and fetch the motor record
        
    for motor in motors:
        print(f"Now working on {motor}.")
        try:
            temp_motor = MPEMotor(motor, name = "temp_motor")
            temp_motor.wait_for_connection()

        except TimeoutError: 
            print(f"Could not find motor record for {motor}.")
            continue

        else: 
            df = fetch_single_motrec(motor = temp_motor)

            #append to storage dataframe
            motor_record_df = pd.concat([motor_record_df, df])

    print(motor_record_df)

    #if save_to_csv:

    #TODO: add save_path
    fname = ioc + '_' + datetime.datetime.now().strftime("%Y%m%d") + '.csv'
    print(fname)
    #fpath = os.path.join(save_path, fname)
    fpath = save_path + fname
    print(fpath)
    motor_record_df.to_csv(fpath)
    print("saved successfully!")
    
  


def single_motor_snapshot(
        bluesky_motor = None, 
        motor_number = None, 
        ioc = "",
        resave_csv = True
):
    
    """Function for fetching a snapshot of the motor record
    for a single motor and editing the entries in the appropriate
    csv file. Accepts both epics motors (e.g., '1idc:m99') or 
    Bluesky motors (e.g., `sms_aero.y`)."""

    #make sure EITHER bluesky motor OR epics motor name is used
    if bluesky_motor and motor_number:
        return ValueError('Both bluesky motor and epics motor provided. Please provide only one.')
    if not bluesky_motor and not motor_number:
        return ValueError('Neither bluesky motor or epics motor provided. Please provide only one.')

    #check EPICS inputs
    if ioc != "" and ioc[-1] == ':':
        ioc = ioc[:-1]  #removes ':'
    if motor_number:
        if type(motor_number) !=  int:
            return ValueError(f'Motor number must be an integer. Received {motor_number}.')
        motor = ioc + ":m" + str(motor_number)   #motor is string of whole EPICS name
        temp_motor = make_temp_motor(motor) #FIXME: add yield from statement for RE

    if bluesky_motor: 
        temp_motor = bluesky_motor

    temp_df = fetch_single_motrec(temp_motor)
    ioc_prefix = temp_motor.prefix.split(':')[0]

    #make a df with just that motor (snapshot)
    temp_df = fetch_single_motrec(temp_motor)
    
    #make list of files where IOC files are stored
    csv_storage_path = '/home/beams/VCOOLEY/Documents/' #FIXME
    files = os.listdir(csv_storage_path)
    foi = []    #initialize files of interest

    for file in files: 
        if file.startswith(ioc_prefix) and file.endswith('.csv'):
            foi.append(file)
            
    #foi is now just a list of the right ioc files 
    most_recent = max(foi, key = os.path.getctime)
    print(f'Overwriting or appending in this IOC file: {most_recent}.')

    df = pd.read_csv(most_recent, index_col =0)
    

    #if row already exists in total df, rewrite
    if df.loc[temp_motor.prefix].any():
        print(f'Motor record already exists for {temp_motor.prefix}.')
        if resave_csv: print('Will overwrite motor record.')
        df.loc[temp_motor.prefix] = temp_df.loc[temp_motor.prefix]

        

    #if the row doesn't already exist, append to record
    else:
        df = pd.concat([temp_df, df])
        print('Motor record did not exist. Appending.')

    if resave_csv:
        #save to new csv labeled with date/time
        old_name_base = '_'.join(most_recent.split('_')[:-1])
        fname = old_name_base + '_' + datetime.datetime.now().strftime("%Y%m%d")

    print("NEW RECORD:")
    print(df)

    print(f'Completed snapshot of {temp_motor.prefix}.')
    

def device_snapshot(
        device,
        #ioc_csv_file,
        resave_csv = True
):
    
    """Function for fetching a snapshot of the motor record for 
    all motors in a bluesky device (e.g., `sms_aero`)."""

    #FIXME: Device components may come from different IOC files

    #df = pd.read_csv(ioc_csv_file)

    for attr in device.component_names: 
        if getattr(device, attr).__class__.__name__ == "MPEMotor":
            temp_motor = getattr(device, attr)
            ioc_prefix = temp_motor.prefix.split(':')[0]

            #make a df with just that motor (snapshot)
            temp_df = fetch_single_motrec(temp_motor)
            
            #make list of files where IOC files are stored
            csv_storage_path = '/home/beams/VCOOLEY/Documents/' #FIXME
            files = os.listdir(csv_storage_path)
            foi = []    #initialize files of interest

            for file in files: 
                if file.startswith(ioc_prefix) and file.endswith('.csv'):
                    foi.append(file)

            #foi is now just a list of the right ioc files 
            most_recent = max(foi, key = os.path.getctime)
            print(f'Overwriting or appending in this IOC file: {most_recent} for {temp_motor.prefix}.')

            df = pd.read_csv(most_recent, index_col = 0)

            #if row already exists in total df, rewrite
            if df.loc[temp_motor.prefix].any():
                print(f'Motor record already exists for {temp_motor.prefix}.')
                if resave_csv: print('Will overwrite motor record.')
                df.loc[temp_motor.prefix] = temp_df.loc[temp_motor.prefix]
            #if the row doesn't already exist, append to record
            else:
                df = pd.concat([temp_df, df])
                print('Motor record did not exist. Appending.')

            if resave_csv:
                #save to new csv labeled with date/time
                old_name_base = '_'.join(most_recent.split('_')[:-1])
                fname = old_name_base + '_' + datetime.datetime.now().strftime("%Y%m%d")
            
            print(f"Completed snapshot for {temp_motor.prefix}, aka {temp_motor.name}.\n")
            

def write_single_motrec(
    ioc_import,     #e.g., "1idc"
    motor_to_import,   #motor number, e.g., 5
    ioc_to_write,    
    motor_to_write,
    csv_to_import   #include '.csv'
):

    """Function to import motor record from csv and write it to
    a motor. Intended to be used when restoring motor record settings.
    
    DOES NOT copy current motor record to another motor; only looks at historical record (csv)."""


    #make an MPEMotor for motor_writeto
    motor_write_name = ioc_to_write + ":m" + str(motor_to_write)
    motor_writeto = MPEMotor(motor_write_name, name = "motor_writeto")


    #might be obsolete here
    #check that motor is MPEMotor type; will not work otherwise
    if motor_writeto.__class__.__name__ != "MPEMotor":
        return ValueError(f"Motor is not configured in Bluesky as MPEMotor. Couldn't fetch {motor_writeto.prefix} info.")

    df_import = pd.read_csv(csv_to_import, index_col=0)

    #make sure motor_writeto is enabled so that changes stick
    yield from bps.mv(motor_writeto.disable, 'Enable')

    motor_import_name = ioc_import + ":m" + str(motor_to_import)
    motor_import = MPEMotor(motor_import_name, name = "motor_import")

    yield from bps.mv(
        motor_writeto.description, df_import.loc[motor_import.prefix]['Motor name'],
        motor_writeto.direction, df_import.loc[motor_import.prefix]['Direction'],
        motor_writeto.display_precision, df_import.loc[motor_import.prefix]['Precision'],
        motor_writeto.max_speed_rps, df_import.loc[motor_import.prefix]['Max. speed (Rev/s)'],
        motor_writeto.speed_rps, df_import.loc[motor_import.prefix]["Speed (Rev/s)"],
        motor_writeto.backup_speed_rps, df_import.loc[motor_import.prefix]['Backlash speed (Rev/s)'],
        motor_writeto.base_speed_rps, df_import.loc[motor_import.prefix]["Base speed (Rev/s)"],
        motor_writeto.acceleration, df_import.loc[motor_import.prefix]["Accel time (s)"],
        motor_writeto.backup_acceleration, df_import.loc[motor_import.prefix]["Backlash accel time (s)"],
        motor_writeto.backlash_dist, df_import.loc[motor_import.prefix]["Backlash distance (EGU)"],
        motor_writeto.move_fraction, df_import.loc[motor_import.prefix]["Move fraction"],
        motor_writeto.home_speed_eps, df_import.loc[motor_import.prefix]["Home speed (EGU/s)"],
        motor_writeto.motor_res_spr, df_import.loc[motor_import.prefix]["Motor resolution (Steps/Rev)"],
        motor_writeto.motor_res_epr, df_import.loc[motor_import.prefix]["Motor resolution (EGU/Rev)"],
        motor_writeto.motor_step_size, df_import.loc[motor_import.prefix]["Motor resolution (EGU/step)"]
    )

    print(f"Motor import = {motor_import.prefix}.")
    print(f"Motor written = {motor_writeto.prefix}")