"""Plans and associated plan stubs for hardware triggering (fastsweep/ fly scans).

Currently only meant to implement Varex triggering.

TODO: uncomment when ready to add in c_shutter control (need to amend prefix in device file); 
        swap out simulat shutter

TODO: If we want to collect more than one image per frame, this needs to be added into 
        total scan time/scan speed calculations. Do we ever collect more than one image per frame?

TODO: Pull layout and attribute files from iconfig (changes in varex.py and iconfig.yml)
TODO: Add checks for the number of images collected at the end of the plan and options to repeat if necessary


TODO: could pull experiment name and find which is current
FIXME: hard coded read path for varex, but this should be automatic 
TODO: add checks that directories/ dm experiment exists??
TODO: add optional scan folder for dets with TIF plugin, not HDF
FIXME: add try statement for gap dictionary
"""

all = [
    "taxi",
    "fly",
    "enfly",
    "setup_user",
    "mpe_bdp_demo_plan",
]

import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

import bluesky.plan_stubs as bps
from ophyd import Signal
from apstools.utils import cleanupText

#import bluesky utils
from ..utils import MINUTE
from ..utils import SECOND
from ..utils import WEEK
from ..utils import build_run_metadata_dict
from ..utils import dm_api_ds
from ..utils import dm_api_proc
from ..utils import share_bluesky_metadata_with_dm
from ..utils import DEFAULT_UPLOAD_TIMEOUT
from ..utils import DEFAULT_UPLOAD_POLL_PERIOD
from ..utils import wait_dm_upload
from ..utils import dm_upload
from ..utils import dm_get_experiment_datadir_active_daq
from ..utils import dm_isDaqActive
from ..utils import dm_start_daq
from ..utils import validate_experiment_dataDirectory

#import MPE devices
from ..devices.s20id_pso import *
from ..devices.s20idd_motors import aero_roty
from ..devices.varex import *
from ..devices.s20id_FPGAs import *
from ..devices.shutter_simulator import shutter #simulated shutter

#import DM devices
from ..devices import DM_WorkflowConnector

#import housekeeping stuff
import os
import time
import pathlib
import numpy as np
from .. import iconfig


###Define Global Variables

#set default wait and report periods
DEFAULT_REPORTING_PERIOD = 1 * MINUTE  # time between reports about an active DM workflow
DEFAULT_WAITING_TIME = 5200 * WEEK  # bluesky will raise TimeoutError if DM workflow is not done by DEFAULT_WAITING_TIME
DAQ_UPLOAD_WAIT_PERIOD = 1.0 * SECOND

#define experiment metadata
TITLE = iconfig["EXPERIMENT"]["TITLE"]
DESCRIPTION = iconfig["EXPERIMENT"]["DESCRIPTION"]
DEFAULT_RUN_METADATA = {"title": TITLE, "description": DESCRIPTION}

#define data directories for DAQ; all should be str
DEFAULT_DATA_PATH = '/net/s6iddata/export/hedm_sata/dev_jul24/' #dir for DAQ to monitor #FIXME
#DEFAULT_DATA_PATH = '/home/beams/S20HEDM/bluesky/user/bdp_demo_0724_simdet/dev_jul24'
DM_EXPERIMENT_NAME = iconfig["EXPERIMENT"]["DM_EXPERIMENT_NAME"]
DEFAULT_DETECTOR_NAME = "varex20idff"   #MUST look like BS object
DETECTOR_WORKSTATION = "gosper" #not needed

#define workflow vars from iconfig
ANALYSIS_SUBDIR = iconfig["ANALYSIS"]["analysis_subdir"]
DM_WORKFLOW_NAME = iconfig["ANALYSIS"]["dm_workflow_name"]
ANALYSIS_WORKSTATIONS = iconfig["ANALYSIS"]["analysis_workstations"] #option to have more than one

#define MIDAS vars from iconfig
PARAMETER_FILE = iconfig["ANALYSIS"]["parameter_file"]
NUM_CPUS = iconfig["ANALYSIS"]["num_cpus"]
NUM_FRAME_CHUNKS = iconfig["ANALYSIS"]["num_frame_chunks"]
PRE_PROC_THRESH = iconfig["ANALYSIS"]["pre_proc_thresh"]

#make a flag to show if setup plan has been run or not
DM_SETUP_FLAG = Signal(name = "DM_SETUP_FLAG", value = "")

###Define fly plans

def taxi(flyer, p0, p1, taxi_timeout = 60):
    """Plan stub to trigger a fly motor to taxi to start position in 
    preparation for a flyscan. 

    Called in enfly plan.
    
    PARAMETERS

    flyer *bluesky device object* : 
        The flyer object that controls the fly motor (e.g., psofly1). 
    
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


#TODO: make all keyword arguments
def enfly(
    start_pos: float = 0,
    end_pos: float = 180, 
    nframes: int = 10,
    ndarks: int = 10,
    exposure_time: float = 0.1, 
    scan_folder: str = "scan_name",
    file_name: str = "file_name",
    fly_motor = None,  #FIXME: find a type to specify
    flyer = None, #FIXME
    use_save: bool = True, 
    det = None #FIXME
):
    
    """
    Plan stub to set up and perform a fly scan

    See `enfly` and `enfly_w_dark` in ensemble_fly.mac for spec macro.
    
    PARAMETERS 

    start_pos *float* :
        Starting position of flyscan in EGUs (e.g., degrees).
    
    end_pos *float* :
        Ending position of flyscan in EGUs. 

    nframes *int* :
        Number of data frames to be collected during flyscan.
    
    ndarks *int* : 
        Number of dark frames to be collected.

    exposure_time *float* : 
        Duration of each exposure in seconds. 
    
    scan_folder *str* : 
        Last folder in path where files are written. Does not need
        to end in a '/'.

    file_name *str* : 
        Base name given to each output file. 
        Does not include temporary suffix or file number.
    
    fly_motor *bluesky motor object* : 
        Motor that will be used to perform flyscan.
        Must be entered in bluesky syntax (e.g., sms_aero.roty)
    
    flyer *bluesky object* : 
        The flyer controller object that controls the fly motor (e.g., psofly1).

    use_save *Boolean* : 
        True/False that determines whether results are saved.
        (default : `True`)

    det *bluesky AD* :
        Area detector that will capture images during flyscan. 
        (default : `varex20idff`)
    
    """
        
    #make sure things are unstaged to start 
    if fly_motor._staged.value != 'no':
        yield from bps.unstage(fly_motor)
    # for det in dets:  #TODO: add a modality if we plan to use multiple detectors at once
    if det._staged.value != 'no':
        yield from bps.unstage(det)  
        det.stage_sigs = {} 
    
    #define det readout times
    gaps = {
      "varex20idff" : 0.067,
      "s20varex2" : 0.067,
      "sim_det" : 0.05
    }
       
    #define gaps and other delay variables
    extra_time = 0.0    #was 0.03
    shutterclose_delay = 0
    shutteropen_delay = 0
    total_exposure_time = exposure_time + extra_time + gaps[det.name] 
        
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
    
    #print statement and pause for user
    print('Made it through calculations and checks.')
    # input('Press any key to continue...')

    #prepare detector in multiple mode (default fastsweep config)
    yield from det.fastsweep_config(exposure_time = exposure_time)

    #print statement and pause for user
    print('Detector has been configured for fastsweep.')
    # input('Press any key to continue...')
    
    #set flyer params
    yield from bps.mv(
        flyer.scan_control, "Standard",
        flyer.pulse_type, "Gate",
        flyer.start_position, start_pos, 
        flyer.end_position, end_pos, 
        flyer.scan_delta, scan_delta,   #deg/step
        flyer.slew_speed, scan_speed_dps,   #deg/s
        flyer.detector_setup_time, gaps[det.name] #gap.det + extra_time
    )
    
    print('PSO flyer settings set for fastsweep.')
    input('Press any key to start taxiing.')

    #disable PSO signal 
    yield from bps.mv(softglue.pso_signal_enable, '0')    #disable
    
    #taxi with default timeout 
    yield from taxi(
        flyer = flyer,
        p0 = start_pos, 
        p1 = end_pos, 
    )

    #print('Priming file saving next.')
    # input('Press any key to continue.')

    #set up number of images captured 
    yield from bps.mv(
        det.hdf1.num_capture, nframes + ndarks, 
        det.hdf1.capture, 'Done'
    )

    #configuration for not saving
    if not use_save:
        print('Not saving images. Setting to stream mode.')
        yield from bps.mv(
            det.hdf1.file_write_mode, 'Stream',
            det.hdf1.auto_save, 'No'    
        )
        
    #configuration for saving
    else: 
       
        yield from bps.mv(
            det.hdf1.file_write_mode, 'Capture',    #FIXME: is this correct?
            det.hdf1.auto_save, 'Yes',
            det.hdf1.file_path, det.hdf1.write_path_template, #+ scan_folder + "\\",  
            det.hdf1.file_name, file_name,
            det.hdf1.auto_increment, 'Yes',
        )
        
    print('File saving setup complete.')
    # input('Press any key to continue...')    

    #collect darks before the scan
    if ndarks > 0:
        #print(f"Collect {ndarks} dark images before the scan.")
        
        #close shutter
        # yield from bps.mv(c_shutter, 14)
        yield from bps.mv(shutter, "closed")
        print('Shutter closed.')
        

        #switch to fastsweep_dark_config
        yield from det.fastsweep_dark_config(ndark_frames = ndarks)
      
        print('Detector and shutter primed for dark frames.')
        input('Press any key to begin dark frame collection...')

        #press capture
        yield from bps.mv(det.hdf1.capture, 1)  #1 = start capturing, must be integer/Boolean (string doesn't work)

        #take darks
        yield from bps.mv(det.cam.acquire, 1)    #aka pushing Acquire


        while det.cam.acquire.get(as_string = True) != 'Done':
            yield from bps.wait(1)


        #print('Dark field collection complete. Preparing for data collection next.')
        # input('Press any key to continue...')

    else:
        print('No dark fields collected. Preparing for data collection next.')
        # input('Press any key to continue... \n')
    
    #Make sure shutter is open whether darks were collected or not
    # yield from bps.mv(c_shutter, 13)
    yield from bps.mv(shutter, "open")
    print('Shutter open.')
    
    #once darks are complete, switch to scan config and re-enable PSO signal
    yield from det.fastsweep_data_config(nframes = nframes)
    yield from bps.mv(softglue.pso_signal_enable, '1')    #enable

    print('Detector and shutter primed for data collection.')
    input('Press any key to begin flying...')

    #press capture, then acquire
    yield from bps.mv(det.cam.acquire, 1)   #FIXME: Or do we want to use this?
    
    #fly
    yield from fly(flyer = flyer)

    print('End of scan. Returning to default fastsweep config and ending capture.')

    yield from bps.mv(det.hdf1.capture, 0)
    yield from det.fastsweep_config(exposure_time = exposure_time)


    if det.hdf1.write_file.get(as_string = True) != 'Done':
        print('HDF file is still writing. Waiting for completion...')
        while det.hdf1.write_file.get(as_string = True) != 'Done':
            yield from bps.wait(1)
   

    
    #TODO: Add checks that correct number of frames captured, potential to repeat scan if needed. 



###Define experiment setup and data acquisition plans here

def setup_user(
    dm_experiment_name: str = DM_EXPERIMENT_NAME,
    detector_name = DEFAULT_DETECTOR_NAME,  #FIXME: this won't work for multiple dets?
    DATA_PATH = DEFAULT_DATA_PATH,
):

    """Plan to set up a DM experiment in preparation for taking data.
    
    PARAMETERS 
    
    dm_experiment_name *str* :
        DM experiment name; DM experiment must already exist for DAQ 
        to process correctly. Cannot create an experiment name in 
        python/Bluesky. By convention, should match the PI_FOLDER name
        as defined in iconfig.yml (ex : "dev_jul24")
    
    detector_name *str* :
        Detector name that will be used as a folder on Voyager. 
        (ex : "varex20idff")
    
    """

    #for demo only: make sure only detector available is called
    # if detector_name != DEFAULT_DETECTOR_NAME:
    #     raise(f"Must use 'detector_name={DEFAULT_DETECTOR_NAME!r}.")

    #provide some checks on DM server
    logger.info("DM_DS_WEB_SERVICE_URL: %s", os.environ["DM_DS_WEB_SERVICE_URL"])
    validate_experiment_dataDirectory(dm_experiment_name)
  
    #provide data directory and check that it is a directory and already exists
    #TODO: if path doesn't exist, make directory
    data_path = pathlib.Path(DATA_PATH)
    if not data_path.exists():
        raise(f"Path to data provided does not exist. Received {data_path}.")
    elif not data_path.is_dir(): 
        raise(f"Path to data provided is not recognized as a directory. Received {data_path}.")
    

    # Check DM DAQ is running for this experiment, if not then start it.
    logger.info("before dm_isDaqActive")
    daq_directory = detector_name   #data on Voyager is sorted into folder with det names
    daq = dm_get_experiment_datadir_active_daq(dm_experiment_name, DATA_PATH)
    if daq is None:
        #log that no DAQ is running
        logger.info(
            "Starting DM DAQ: experiment %r in data directory %r",
            dm_experiment_name,
            DATA_PATH
        )
        #start a DAQ
        daq = dm_start_daq(
            dm_experiment_name,
            DATA_PATH,
            destDirectory=daq_directory
        )
        #log that DAQ is now running
        logger.info(
            "Created DAQ for experiment %r, directory %r",
            dm_experiment_name,
            DATA_PATH
        )
    else:
        #log that DAQ is running
        logger.info(
            "Found DAQ for experiment %r, directory %r",
            dm_experiment_name,
            DATA_PATH
        )
    logger.info("DAQ info: %s", daq)
    # daq_info.put(json.dumps(daq))  # save for later

    #check that parameter file exists and is a file
    pfile = pathlib.Path(PARAMETER_FILE)

    if not pfile.exists():
        raise FileNotFoundError(f"Parameter file: {pfile}")
    elif not pfile.is_file():
        raise(f"Path file appears not to be a file. Received {pfile}.")

    #after checks, upload parameter file
    dm_upload(
        dm_experiment_name,
        str(pfile.parent),
        destDirectory=ANALYSIS_SUBDIR.lstrip("analysis/"),    #should look like hedm/ff_rec/
        experimentFilePath=pfile.name, 
        useAnalysisDirectoryAsRoot = True
    )

    #change signal flag to show setup is complete
    yield from bps.mv(DM_SETUP_FLAG, dm_experiment_name)


# -----------------------------------------------------------------------------
### Full demo plan below

def mpe_bdp_demo_plan(
    title: str = TITLE,
    description: str = DESCRIPTION,
    # data collection parameters ----------------------------------------
    start_pos: float = 0,
    end_pos: float = 20, 
    nframes: int = 40,
    ndarks: int = 10,
    exposure_time: float = 0.15, 
    scan_folder: str = "bluesky_fly",
    file_name: str = "full_plan_40frames",
    fly_motor = None,
    flyer = None,
    use_save: bool = True, 
    det = None,
    # DM workflow kwargs ----------------------------------------
    dm_workflow_name = DM_WORKFLOW_NAME,
    analysis_workstation: str = 'polaris',  #ANALYSIS_WORKSTATIONS,
    num_cpus: int = 64,
    num_frame_chunks: int = 100,
    pre_proc_thresh: int = 80,
    local_working_dir: str = "/scratch/s20hedm",
    # internal kwargs ----------------------------------------
    dm_concise=False,
    dm_wait=False,
    dm_reporting_period=DEFAULT_REPORTING_PERIOD,
    dm_reporting_time_limit=DEFAULT_WAITING_TIME,
    dm_image_file_upload_timeout=DEFAULT_UPLOAD_TIMEOUT,
    dm_image_file_upload_poll_period=DEFAULT_UPLOAD_POLL_PERIOD,
    # user-supplied metadata ----------------------------------------
    md: dict = DEFAULT_RUN_METADATA,
):
    """
    Full plan to collect data using a flyscan and port it to Voyager using
    DAQ. After collection, a DM workflow will be initiated on data already
    collected with beam.

    PARAMETERS


    """

    ### Run checks on arguments given

    #only one detector is configured for flyscan at 20IDD; check this is given   
    # if det.name!= DEFAULT_DETECTOR_NAME:
    #     raise ValueError(f"""Detector must match default given.
    #                      Received {det.name}.
    #                      Only {DEFAULT_DETECTOR_NAME} configured for this
    #                      plan at this time.""")

    #check that we are sending it to correct workstation
    analysis_workstation = analysis_workstation.lower()  # to be safe
    if analysis_workstation not in ANALYSIS_WORKSTATIONS:
        raise ValueError(f"Received {analysis_workstation}."
            "Must be one of these: {ANALYSIS_WORKSTATIONS}")

    #check that setup plan has been run using flag
    if len(DM_SETUP_FLAG.get()) == 0:
        raise RuntimeError("Must run mpe_setup_user() first.")
    logger.info(f"DM experiment from mpe_setup_user(): {DM_SETUP_FLAG.get()}.")
    
 
    # --------------------------------------------------------------------------

    ### Create metadata dictionary

    #create local dictionary
    _md = dict(
        title=title,
        safe_title=cleanupText(title),
        description=description,

        # detector parameters ----------------------------------------
        detector_name= det.name,
        exposure_time = exposure_time,
        num_data_frames = nframes,
        num_dark_frames = ndarks,
        start_pos = start_pos,
        end_pos = end_pos,
        fly_motor = fly_motor.name, 
        flyer = flyer.name,
        scan_folder = scan_folder,
        base_file_name = file_name,

        # DM workflow kwargs ----------------------------------------
        owner = dm_api_proc().username,
        workflow = dm_workflow_name,

        # internal kwargs --------------------------------------------
        dm_concise = dm_concise,
        dm_wait = dm_wait,
        dm_reporting_period = dm_reporting_period,
        dm_reporting_time_limit = dm_reporting_time_limit,
        dm_image_file_upload_timeout = dm_image_file_upload_timeout,
        dm_image_file_upload_poll_period = dm_image_file_upload_poll_period,
    )

    #add analysis metadata
    _md = build_run_metadata_dict(
        _md,
        # ALL following kwargs are stored under RE.md["data_management"]
        analysisMachine=analysis_workstation,
        num_cpus = num_cpus,
        num_frame_chunks = num_frame_chunks,
        pre_proc_thresh = pre_proc_thresh,
        local_working_dir=local_working_dir,
        # daqInfo=daq_info.get(),
    )

    #merge dictionaries so that user md takes highest priority
    _md.update(md)  



    # --------------------------------------------------------------------

    ### Set up workflow
    """NOTE: At most one workflow can be running. 
    DM workflow engine configuration is limiting to one job."""

    dm_workflow = DM_WorkflowConnector(name="dm_workflow")

    yield from bps.mv(
        dm_workflow.concise_reporting, dm_concise,
        dm_workflow.reporting_period, dm_reporting_period,
    )

    # -----------------------------------------------------------------
    
    ### Perform fly scan 

    yield from enfly(
        start_pos = start_pos,
        end_pos = end_pos, 
        nframes = nframes, 
        ndarks = ndarks,
        exposure_time = exposure_time,
        scan_folder = scan_folder,
        file_name = file_name,
        fly_motor = fly_motor,
        flyer = flyer,
        use_save = use_save,
        det = det
    )

    #logger.info("Finished data collection portion of plan. Workflow initiating.")    #TODO: change name
    input('Press any key to launch DM workflow...')
    # ------------------------------------------------------------------
    
    ### Wait for DAQ before starting workflow 

    #TODO: yield from wait_dm_upload(...)

    # ------------------------------------------------------------------
    
    ### Start APS data management workflow-- Fakeout for demo only
    #TODO: After demo, revise this to put data collected in workflow

    dm_workflow_file = "park_Au_cubes_ff_000106.edf.ge5"
    logger.info(f"""Starting DM workflow {dm_workflow_name}, 
                filePath = {dm_workflow_file}.""")

    #Demo only: send previously collected data to DM workflow
    yield from dm_workflow.run_as_plan(
        #set workflow params
        workflow= dm_workflow_name,
        wait=dm_wait,
        timeout=dm_reporting_time_limit,

        #define files for DM workflow        
        detector = "ge3",
        experimentName = "parraga_midas_setup_jun24", 
        filePath = dm_workflow_file,
        darkFileName = 'dark_before_000112.edf.ge5',
        paramFN = "ps_dmi_au.txt", 

        #set analysis params
        analysisMachine = analysis_workstation,
        nCPUs = NUM_CPUS, 
        numFrameChunks = NUM_FRAME_CHUNKS,
        preProcThresh = PRE_PROC_THRESH,
        
        #set priority in analysis queue
        demand = False,  #propels workflow to special queue

        localWorkingDir=local_working_dir,
    )

    


