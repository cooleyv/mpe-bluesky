# Bluesky Instrument configuration

Describes the configuration files supporting an instrument for data acquisition with Bluesky.

description | configuration file
--- | ---
instrument customizations | `iconfig.yml`
interactive data collection | `collection.py`
bluesky-queueserver | `queueserver.py`

# Bluesky Instrument devices description 

Describes the devices that comprise the hardware of the instrument. Devices are grouped into .py files listed and described below. 

a. facility devices
    
    aps_source.py
    - connects to facility information about the storage ring using accelerator PVs. 

b. generic devices

    generic_motors.py
        - contains generalized modifications for motor PVs that are widely applicable across MPE beamlines. 
        - includes:
            - modification to EpicsMotor to include additional PV records per motor
            - definitions for axes in generic motors with 5, 6, 7 degrees of freedom

c. area detector (AD) devices 

    pixirad.py
        - contains means of generating pixirad AD, based on user preference and need. 
        - includes:
            - generation of pixirad AD for ADcore v3.2 or v3.12
            - function to enable plugins of interest specific to user's experiment
            - method to arm pixirad AD in preparation for collecting data in a hardware-triggered fastsweep scan


d. other measurement devices

    s1ide_scalers.py
        - generates scaler devices normally housed in the 1-ID-E hutch. 

e. motor devices

    s1idb_motors.py
        - generates motors normally housed in the 1-ID-B hutch. 

    s1idc_motors.py
        - generates motors normally housed in the 1-ID-C hutch. 
        - includes IOCs 1idc and those for labview rotation stage, AMCI units, and mobile driver racks (IOC names TBD).

    s1ide_motors.py
        - generates motors normally housed in the 1-ID-E hutch. 
        - includes IOCs 1ide1 and 1ide. 

    s1id_shutters.py
        - generates motors driving shutter motions, irrespective of hutch or location.
        - does not include fastshutter PVs controlled by FPGAs (see 'f. soft devices')

    s1id_slits.py
        - generates motors driving slit motions, irrespective of hutch or location.

f. soft devices

    s1id_FPGAs.py
        - generates devices from softglue PVs.
        - includes PSO controller for fly scans. 



# Bluesky Instrument plans description 

Describes the plans that comprise the protocols and functions of the instrument. 

a. auxiliary plans

    auxiliary_ad.py 
        - contains plan stubs for creating, configuring, or modifying area detectors. 
        - includes: 
            - choosing AD device given iconfig input from user
            - writing ophyd signal if it has a new value
            - configuring the AD HDF5 plugin for acquisition

    auxiliary_scan.py
        - contains plan stubs called in larger scanning plans.
        - includes:
            - choosing motor devices given iconfig input from user
            - checking shutter statuses
            - checking beam status

    auxiliary_SR.py
        - contains plan stubs pertaining to the storage ring and its status.
        - includes: 
            - waiting for beam to come back once it is down

b. software-triggered scanning plans

    alignment.py
        - contains plans for aligning devices at 1-ID
        - includes: 
            - aligning diodes 
            - aligning samples 

    software_triggering.py
        - contains plans for software-triggered acquisitions
        - includes:
            - acquiring bright frames 
            - acquiring dark frames 
            - acquiring single or multiple exposures 
            - acquiring continuously 

c. hardware-triggered scanning plans

    hardware_triggering.py
        - contains plans for hardware-triggered acquisitions
        - includes: 
            - performing a fastsweep scan (configuring devices, taxiing, arming devices, flying, disarming devicess)

