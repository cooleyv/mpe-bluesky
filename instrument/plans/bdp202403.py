"""
Bluesky plans for the BDP M21 demo, 2024-03-12.
"""

__all__ = """
    mpe_bdp_demo_plan
    mpe_setup_user
""".split()

import json
import logging
import os
import pathlib

from apstools.utils import cleanupText
from ophyd import Signal

from bluesky import plan_stubs as bps

logger = logging.getLogger(__name__)
logger.setLevel("INFO")
logger.info(__file__)

from .ad_setup_plans import write_if_new
from ..devices import DM_WorkflowConnector
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

DM_EXPERIMENT_NAME = "prj-20240306"  # for testing & development
DM_WORKFLOW_NAME = "midas-ff"

ANALYSIS_SUBDIR = "analysis/hedm/ff_rec"
ANALYSIS_WORKSTATIONS = """califone polaris""".split()
BEAMS_PATH = pathlib.Path("/home/beams")
HOME_PATH = pathlib.Path.home()

# This is MPE data acquisition directory to watch.
DATA_PATH_LOCAL = HOME_PATH / "data"  # for the BDP demo 2024-03

PARAMETER_FILE_LOCAL = HOME_PATH / "ps_shade_au.txt"
EXAMPLE_DATA_FILE_LOCAL = HOME_PATH / "shade_Au_ff_000294.h5"
DATA_DIRECTORY_IOC = "/mnt/GE3-1/G"

DEFAULT_DETECTOR_NAME = "ge3"
DETECTOR_WORKSTATION = f"{DEFAULT_DETECTOR_NAME}-1"
IOC_AD_DATA_ROOT = "G:/"
LOCAL_AD_DATA_ROOT = DATA_PATH_LOCAL

TITLE = "BDP_MPE_demo"  # keep this short, single-word
DESCRIPTION = "Demonstrate MPE data acquisition and analysis."
DEFAULT_RUN_METADATA = {"title": TITLE, "description": DESCRIPTION}
DEFAULT_REPORTING_PERIOD = 1 * MINUTE  # time between reports about an active DM workflow
# DEFAULT_WAITING_TIME = 10 * MINUTE  # time limit for bluesky reporting on a workflow
DEFAULT_WAITING_TIME = 5200 * WEEK  # unlimited (100 years)
# bluesky will raise TimeoutError if DM workflow is not done by DEFAULT_WAITING_TIME
DAQ_UPLOAD_WAIT_PERIOD = 1.0 * SECOND


# daq_info = Signal(name="daq_info", value="")
det_name = Signal(name="det_name", value=str(DEFAULT_DETECTOR_NAME))
dm_experiment = Signal(name="dm_experiment", value=str(DM_EXPERIMENT_NAME))
midas_parameter_file = Signal(
    name="midas_parameter_file", value=str(PARAMETER_FILE_LOCAL)
)


def mpe_bdp_demo_plan(
    title: str = TITLE,
    description: str = DESCRIPTION,
    # detector parameters ----------------------------------------
    detector_name: str = DEFAULT_DETECTOR_NAME,
    acquire_time: float = 0.01,
    num_images: int = 100,
    # DM workflow kwargs ----------------------------------------
    analysisMachine: str = "califone",  # or "polaris"
    num_cpus: int = 100,
    local_working_dir: str = "/scratch/s1iduser",
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
    "Acquire" MPE image data and run a DM workflow.
    """
    from ..utils.aps_data_management import dm_api_daq
    from ..utils.aps_data_management import dm_daq_wait_upload_plan
    # from .ad_setup_plans import setup_hdf5_plugin  # once AD is used
    
    if detector_name != det_name.get():
        raise ValueError(
            f"{detector_name=!r} not equal to the setup name:"
            f" 'mpe_setup_user(detector_name={det_name.get()!r})'."
        )

    analysisMachine = analysisMachine.lower()  # to be safe
    if analysisMachine not in ANALYSIS_WORKSTATIONS:
        raise ValueError(
            f"Received {analysisMachine=!r}."
            "  Must be one of these: {ANALYSIS_WORKSTATIONS}"
        )

    workflow_name = DM_WORKFLOW_NAME
    experiment_name = dm_experiment.get()
    if len(experiment_name) == 0:
        raise RuntimeError("Must run mpe_setup_user() first.")
    experiment = dm_api_ds().getExperimentByName(experiment_name)
    logger.info("DM experiment: %s", experiment_name)
    
    # 'title' must be safe to use as a file name (no spaces or special chars)
    safe_title = cleanupText(title)

    # Not needed for BDP demo.
    # Later, will need to adapt to MPE group style for area detectors.
    #    # Q: What is the naming convention for the MPE group?
    #    # Q: Is experiment name is part of the file path?  check SPEC macros
    #
    #    det = _pick_area_detector(detector_name)
    #    data_path = pathlib.Path(_xpcsDataDir(safe_title, num_images))
    #    if data_path.exists():
    #        raise FileExistsError(
    #            # fmt: off
    #            f"Found existing directory '{data_path}'."
    #            "  Will not overwrite."
    #            # fmt: on
    #        )
    #    # AD will create this directory if not exists.
    #    file_name_base = _xpcsFileNameBase(safe_title, num_images)
    #    yield from setup_hdf5_plugin(
    #        det.hdf1, data_path, file_name_base, num_capture=num_images
    #    )

    # _md is for a bluesky open run
    _md = dict(
        title=title,
        safe_title=safe_title,
        description=description,
        # detector parameters ----------------------------------------
        detector_name=detector_name,
        acquire_time=acquire_time,
        num_images=num_images,
        # DM workflow kwargs ----------------------------------------
        owner=dm_api_proc().username,
        workflow=workflow_name,
        # internal kwargs ----------------------------------------
        dm_concise=dm_concise,
        dm_wait=dm_wait,
        dm_reporting_period=dm_reporting_period,
        dm_reporting_time_limit=dm_reporting_time_limit,
        dm_image_file_upload_timeout=dm_image_file_upload_timeout,
        dm_image_file_upload_poll_period=dm_image_file_upload_poll_period,
    )
    _md = build_run_metadata_dict(
        _md,
        # ALL following kwargs are stored under RE.md["data_management"]
        analysisMachine=analysisMachine,
        num_cpus=num_cpus,
        local_working_dir=local_working_dir,
        # daqInfo=daq_info.get(),
    )
    _md.update(md)  # user md takes highest priority

    # Rule: at most one workflow can running.
    # DM workflow engine configuration is limiting to one job.
    dm_workflow = DM_WorkflowConnector(name="dm_workflow")
    # fmt: off
    yield from bps.mv(
        dm_workflow.concise_reporting, dm_concise,
        dm_workflow.reporting_period, dm_reporting_period,
    )
    # fmt: on

    # ------------------------------------------------------------------
    # "data acquisition" for the BDP demo:  link image file to HOME/data/
    # note: 209 s to copy 12GB file from HOME to HOME/data
    # note: 0.0090 s to hard link
    # note: 0.0093 s to soft link
    if not EXAMPLE_DATA_FILE_LOCAL.exists():
        raise FileNotFoundError(
            f"Example image file {EXAMPLE_DATA_FILE_LOCAL} not found!"
        )
    detector_file = DATA_PATH_LOCAL / EXAMPLE_DATA_FILE_LOCAL.name
    if detector_file == EXAMPLE_DATA_FILE_LOCAL:
        raise ValueError(
            f"Cannot link {EXAMPLE_DATA_FILE_LOCAL} to {detector_file}."
        )
    if detector_file.exists():
        detector_file.unlink()

    # (hard) link the example image file to the detector output directory
    os.link(str(EXAMPLE_DATA_FILE_LOCAL), str(detector_file))
    # For the demo, update the time stamp so DAQ will see the file is new.
    detector_file.touch()
    # ------------------------------------------------------------------

    # after acquisition with area detector:
    # detector_file = det.hdf1.full_file_name.get()

    # Wait for DAQ to upload detector_file before launching workflow.
    yield from wait_dm_upload(
        dm_experiment.get(),
        f"{det_name.get()}/{detector_file.name}",
        timeout=dm_image_file_upload_timeout,
        poll_period=dm_image_file_upload_poll_period,
    )

    #
    # *** Start the APS Data Management workflow. ***
    #
    logger.info(
        "DM workflow %r, filePath=%r",
        workflow_name,
        detector_file.name,
    )
    yield from dm_workflow.run_as_plan(
        workflow=workflow_name,
        wait=dm_wait,
        timeout=dm_reporting_time_limit,
        # all kwargs after this line are DM argsDict content
        analysisMachine=analysisMachine,
        filePath=pathlib.Path(detector_file).name,
        experiment=dm_experiment.get(),
        detector=detector_name,
        paramFN=pathlib.Path(midas_parameter_file.get()).name,
        nCPUs=num_cpus,
        localWorkingDir=local_working_dir,
    )

    # No "bluesky" run for this BDP demo
    # # upload bluesky run metadata to APS DM
    # share_bluesky_metadata_with_dm(experiment_name, workflow_name, run)

    logger.info("Finished: mpe_bdp_demo_plan()")


def mpe_setup_user(
    dm_experiment_name: str = DM_EXPERIMENT_NAME,
    parameter_file: str = str(PARAMETER_FILE_LOCAL),
    detector_name=DEFAULT_DETECTOR_NAME,
    # file_number: int = -1  # when using area detector
):
    """
    Configure bluesky session for this user.

    PARAMETERS

    - dm_experiment_name *str*: Existing DM experiment to be used.
    - parameter_file *str*: MIDAS parameter file. (Full path on bluesky workstation.)
    - detector_name *str*: Hard-coded for the demo to be 'ge3'.

    # with AD (later), Set ``file_number=-1`` to continue with current HDF5 file numbering.
    """
    from ..utils import dm_isDaqActive
    from ..utils import dm_start_daq
    from ..utils import validate_experiment_dataDirectory
    
    if detector_name != DEFAULT_DETECTOR_NAME:
        raise(f"Must use 'detector_name={DEFAULT_DETECTOR_NAME!r} for the BDP demo.")

    validate_experiment_dataDirectory(dm_experiment_name)
    yield from write_if_new(dm_experiment, dm_experiment_name)
    yield from write_if_new(det_name, detector_name)

    # Full path to directory where new data will be written (by area detector IOC).
    # data_directory = f"{DATA_DIRECTORY_IOC}/{SOMETHING}"
    # For the demo, the data file will be in a local directory.
    data_directory = str(DATA_PATH_LOCAL)

    # Check DM DAQ is running for this experiment, if not then start it.
    logger.info("before dm_isDaqActive")
    daq_directory = detector_name
    daq = dm_get_experiment_datadir_active_daq(dm_experiment_name, data_directory)
    if daq is None:
        # Need another DAQ if also writing to a different directory.
        # A single DAQ can be used to cover any subdirectories.
        # Anything in them will be uploaded.
        logger.info(
            "Starting DM DAQ: experiment %r in data directory %r",
            dm_experiment_name,
            data_directory,
        )
      
        daq = dm_start_daq(
            dm_experiment_name,
            data_directory,
            destDirectory=daq_directory
        )
        logger.info(
            "Created DAQ for experiment %r, directory %r",
            dm_experiment_name,
            data_directory
        )
    else:
        logger.info(
            "Found DAQ for experiment %r, directory %r",
            dm_experiment_name,
            data_directory
        )
    logger.info("DAQ info: %s", daq)
    # daq_info.put(json.dumps(daq))  # save for later

    # Upload parameter file
    midas_parameter_file.put(parameter_file)
    pfile = pathlib.Path(parameter_file)
    if not pfile.exists():
        raise FileNotFoundError(f"Parameter file: {pfile}")
    dm_upload(
        dm_experiment_name,
        str(pfile.parent),
        destDirectory=detector_name,
        experimentFilePath=pfile.name
    )
