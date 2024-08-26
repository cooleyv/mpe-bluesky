#Creating a dictionary to pickle and use as record of in/out positions

all = [
    "device_info",
]

import pickle
import os

device_info = {
    'tomo_c': {
        'axis':'x',  'in':0, 'out':10, 'units': 'mm'},
    'tomo_ds_e': {
        'axis':'x',  'in':0, 'out':11, 'units': 'mm'},   
    'tomo_us_e': {
        'axis':'x',  'in':1, 'out': 6, 'units':'mm'},
    'sms_aero': {
        'axis':'x2', 'in':1, 'out': 6, 'units':'mm'},
    'mts': {
        'axis':'x2', 'in':1, 'out': 6, 'units':'mm'},
    'sms_lab': {
        'axis':'x2', 'in':1, 'out': 6, 'units':'mm'},
    'saxs_shield':{
        'axis':'x',  'in':1, 'out': 7, 'units':'mm'}
}

#Write to same folder this script is in
#FIXME: still writes to home folder?
# dir_path = os.path.dirname(os.path.realpath('instrument_in_out.py'))
# new_file_path = os.path.join(dir_path, 'instrument_in_out.pkl')

# with open('/home/beams/S1IDTEST/bluesky/instrument/utils/instrument_in_out.pkl', 'wb') as f:  #wb = write binary
#     pickle.dump(device_info, f)
    
# f.close()
    