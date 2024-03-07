"""
Bluesky plans for the BDP M21 demo, 2024-03-12.
"""

__all__ = """
    mpe_bdp_demo_plan
    mpe_setup_user
""".split()

import logging
import pathlib

from ophyd import Signal

from bluesky import plan_stubs as bps

from .ad_setup_plans import write_if_new
from ..utils import MINUTE
from ..utils import SECOND
from ..utils import build_run_metadata_dict
from ..utils import dm_api_ds
from ..utils import dm_api_proc
from ..utils import share_bluesky_metadata_with_dm

logger = logging.getLogger(__name__)
logger.info(__file__)

DM_EXPERIMENT_NAME = "prj-20240306"  # for testing & development
DM_WORKFLOW_NAME = "midas-ff"

ANALYSIS_SUBDIR = "analysis/hedm/ff_rec"
ANALYSIS_WORKSTATIONS = """califone polaris""".split()
BEAMS_PATH = pathlib.Path("/home/beams")
HOME_PATH = pathlib.Path.home()

# FIXME: What MPE data acquisition directory to watch?
DATA_PATH_LOCAL = HOME_PATH / "data"  # for the BDP demo 2024-03

PARAMETER_FILE_LOCAL = HOME_PATH / "ps_shade_au.txt"
EXAMPLE_DATA_FILE_LOCAL = HOME_PATH / "shade_Au_ff_000294.h5"
DATA_DIRECTORY_IOC = "/mnt/GE3-1/G"

DEFAULT_DETECTOR_NAME = "ge3"
DETECTOR_WORKSTATION = f"{DEFAULT_DETECTOR_NAME}-1"
IOC_AD_DATA_ROOT = "G:/"
LOCAL_AD_DATA_ROOT = DATA_PATH_LOCAL

TITLE = "BDP_XPCS_demo"  # keep this short, single-word
DESCRIPTION = "Demonstrate XPCS data acquisition and analysis."
DEFAULT_RUN_METADATA = {"title": TITLE, "description": DESCRIPTION}
DEFAULT_REPORTING_PERIOD = 10 * SECOND  # time between reports about an active DM workflow
# DEFAULT_WAITING_TIME = 10 * MINUTE  # time limit for bluesky reporting
DEFAULT_WAITING_TIME = 999_999_999_999 * SECOND  # unlimited (effectively)
# bluesky will raise TimeoutError if DM workflow is not done by DEFAULT_WAITING_TIME
DAQ_UPLOAD_WAIT_PERIOD = 1.0 * SECOND


daq_id = Signal(name="daq_id", value=0)
det_name = Signal(name="det_name", value=str(DEFAULT_DETECTOR_NAME))
dm_experiment = Signal(name="dm_experiment", value=str(DM_EXPERIMENT_NAME))
midas_parameter_file = Signal(
    name="midas_parameter_file", value=str(PARAMETER_FILE_LOCAL)
)


# see: https://github.com/aps-8id-dys/bluesky/blob/main/instrument/plans/bdp_demo.py#L155
def mpe_bdp_demo_plan(
    title: str = TITLE,
    description: str = DESCRIPTION,
    # detector parameters ----------------------------------------
    detector_name: str = DEFAULT_DETECTOR_NAME,
    acquire_time: float = 0.01,
    # acquire_period: float = 0.01,
    # num_exposures: int = 1,
    num_images: int = 100,
    # num_triggers: int = 1,
    # DM workflow kwargs ----------------------------------------
    analysisMachine: str = "califone",  # or "polaris"
    num_cpus: int = 100,
    local_working_dir: str = "/scratch/s1iduser",
    # internal kwargs ----------------------------------------
    dm_concise=False,
    dm_wait=False,
    dm_reporting_period=DEFAULT_REPORTING_PERIOD,
    dm_reporting_time_limit=DEFAULT_WAITING_TIME,
    # user-supplied metadata ----------------------------------------
    md: dict = DEFAULT_RUN_METADATA,
):
    """
    Acquire XPCS data with the chosen detector and run a DM workflow.
    """
    from ..utils.aps_data_management import dm_api_daq
    from ..utils.aps_data_management import dm_daq_wait_upload_plan
    from .ad_setup_plans import setup_hdf5_plugin  # FIXME
    
    if detector_name != det_name.get():
        raise ValueError(
            f"{detector_name=!r} not equal to the steup name:"
            f" 'mpe_setup_user(detector_name={det_name.get()!r})'."
        )

    analysisMachine = analysisMachine.lower()  # to be safe
    if analysisMachine not in ANALYSIS_WORKSTATIONS:
        raise ValueError(
            f"Received {analysisMachine=!r}."
            "  Must be one of these: {ANALYSIS_WORKSTATIONS}"
        )

    workflow_name = DM_WORKFLOW_NAME

    det = _pick_area_detector(detector_name)  # FIXME
    experiment_name = dm_experiment.get()
    if len(experiment_name) == 0:
        raise RuntimeError("Must run xpcs_setup_user() first.")
    experiment = dm_api_ds().getExperimentByName(experiment_name)
    logger.info("DM experiment: %s", experiment_name)

    # FIXME: determine the naming convention for the MPE group
    # TODO: experiment name is part of the file path?  check SPEC macros
    # 'title' must be safe to use as a file name (no spaces or special chars)
    safe_title = cleanupText(title)
    data_path = pathlib.Path(_xpcsDataDir(safe_title, num_images))  # FIXME:
    if data_path.exists():
        raise FileExistsError(
            # fmt: off
            f"Found existing directory '{data_path}'."
            "  Will not overwrite."
            # fmt: on
        )
    # AD will create this directory if not exists.
    file_name_base = _xpcsFileNameBase(safe_title, num_images)  # FIXME:
    yield from setup_hdf5_plugin(
        det.hdf1, data_path, file_name_base, num_capture=num_images
    )

    # _md is for a bluesky open run
    _md = dict(  # FIXME: edit, revise, prune, augment, etc. (from XPCS)
        detector_name=detector_name,
        acquire_time=acquire_time,
        acquire_period=acquire_period,
        num_capture=num_images,
        num_exposures=num_exposures,
        num_images=num_images,
        num_triggers=num_triggers,
        qmap_file=qmap_path.name,
        owner=dm_api_proc().username,
        workflow=workflow_name,
        title=title,
        safe_title=safe_title,
        description=description,
        header=xpcs_header.get(),
    )
    _md = build_run_metadata_dict(  # FIXME:
        _md,
        # ALL following kwargs are stored under RE.md["data_management"]
        # TODO: more?
        analysisMachine=analysisMachine,
    )
    _md.update(md)  # user md takes highest priority

    dm_workflow = DM_WorkflowConnector(name="dm_workflow")
    yield from bps.mv(
        dm_workflow.concise_reporting,
        dm_concise,
        dm_workflow.reporting_period,
        dm_reporting_period,
    )

    # TODO: "data acquisition"
    # copy (?hard link?) the 12GB file to DATA_PATH_LOCAL
    # note: 209 s to copy
    # note: 0.009 s to hard link
    # note: 0.009 s to soft link

    # before acquisition: EXAMPLE_DATA_FILE_LOCAL

    # after acquisition:
    # detector_file = det.hdf1.full_file_name.get()
    detector_file = DATA_PATH_LOCAL / EXAMPLE_DATA_FILE_LOCAL.name

    # TODO: wait for DAQ to upload this SPECIFIC FILE before launching the workflow
    # Needs a new function.  Test the new function with small files.
    # dm_get_experiment_file(experimentName, filename)
    # Polling loop:
    #    Need DAQ's ID to get the number of files that have been uploaded.
    #    Check that list for this file.
    #    Timeout is entirely possible.
    #    DAQ status could advise.
    #    Ask the experiment if this file is part of the experiment.
    # https://git.aps.anl.gov/search?search=getExperimentFile&nav_source=navbar&project_id=885&group_id=198&scope=wiki_blobs
    """
    def getExperimentFile(self, experimentName, experimentFilePath):

    FileCatApi

        :raises ObjectNotFound: in case file with a given path does not exist
    """

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

    # upload bluesky run metadata to APS DM
    share_bluesky_metadata_with_dm(experiment_name, workflow_name, run)

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

    .. note:: Set ``file_number=-1`` to continue with current HDF5 file numbering.
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
    parms = {
        "destDirectory": detector_name,
    }
    if not dm_isDaqActive(dm_experiment_name):
        # Need another DAQ if also writing to a different directory (off voyager).
        # A single DAQ can be used to cover any subdirectories.
        # Anything in them will be uploaded.
        logger.info(
            "Starting DM DAQ: experiment %r in data directory %r",
            dm_experiment_name,
            data_directory,
        )
      
        id_ = dm_start_daq(dm_experiment_name, data_directory, **parms)
        daq_id.put(id_)  # save the ID of the new DAQ, will use later

    # Upload parameter file
    midas_parameter_file.put(parameter_file)
    pfile = pathlib.Path(parameter_file)
    if not pfile.exists():
        raise FileNotFoundError(f"Parameter file: {pfile}")
    parms["experimentFilePath"] = pfile.name
    dm_upload(dm_experiment_name, str(pfile.parent), **parms)

    # TODO: What else?
