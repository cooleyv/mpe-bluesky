"""
Plans for use by the BDP
"""

__all__ = """
    demo202305
""".split()

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # allow any log content at this level
logger.info(__file__)

from apstools.devices import make_dict_device
from apstools.plans import write_stream
from bluesky import plan_stubs as bps
from bluesky import preprocessors as bpp
import pathlib

from ..devices import dm_workflow

DEFAULT_IMAGE_DIR = pathlib.Path("/home/1-id")  # TODO: s1iddata


# TODO: consider continuous operations
#   one rule:  
#     Do not submit new DM job until previous one is done.
#     OK to acquire new data but wait new DM run until previous one is done

def demo202305(
    image_dir=str(DEFAULT_IMAGE_DIR),
    fly_scan_time=60,
    wf_name="example-01",
    dm_filePath="/home/beams/S1IDTEST/.bashrc",
    dm_timeout=180,
    dm_wait=True,
    dm_concise=True,
    md={}
):
    """
    BDP: Simulate fly scan acquisition of a set of image files and start DM workflow.

    Examples::

        # all the defaults
        RE(demo202305())

        # non-default values
        RE(demo202305(fly_scan_time=2, md=dict(title="BS+DM test")))

    Wait to kickoff the DM workflow if a previous workflow is still running.
    """
    image_path = pathlib.Path(image_dir)
    
    _md = dict(
        title="BDP demo2305",
        description=(
            "Simulate fly scan acquisition of a set"
            " of image files and start DM workflow."
        ),
        fly_scan_time=fly_scan_time,
        timeout=dm_timeout,
        wait=dm_wait,
        data_management=dict(
            owner=dm_workflow.owner.get(),
            workflow=wf_name,
            filePath=dm_filePath,
            image_directory=image_dir,
            concise=dm_concise,
        ),
    )
    _md.update(md)  # add user-contributed metadata
    logger.info(
        "In demo202305() plan."
        f"  {image_dir=}"
        f" (exists: {image_path.exists()})"
        f" {fly_scan_time=} s"
        f" {md=} s"
        )

    @bpp.run_decorator(md=_md)
    def _inner():
        logger.info(f"Simulate fly scan for {fly_scan_time} s")
        yield from bps.sleep(fly_scan_time)
        # simulate some data
        sim = make_dict_device(dict(x=1, y=2), name="sim")
        for x, y in [
            [1, 2],
            [2, 73],
            [3, 119],
            [4, 13],
        ]:
            # add the simulated data, point by point, as usual
            yield from bps.mv(sim.x, x, sim.y, y)
            yield from write_stream(sim, "primary")
        logger.info("Data collection (simulation) complete.")

        logger.info(f"Start DM workflow: {wf_name=}")
        yield from bps.mv(dm_workflow.concise_reporting, dm_concise)
        yield from dm_workflow.run_as_plan(
            wf_name, 
            wait=dm_wait, 
            timeout=dm_timeout, 
            # all kwargs after this line are DM argsDict content
            filePath=dm_filePath,
            imageDir=image_dir,
        )
        yield from write_stream([dm_workflow], "dm_workflow")
        logger.info("Bluesky plan demo202305() complete. %s", dm_workflow)

    yield from _inner()


def xyplot(dataset, xname, yname, title=None):
    """
    Plot the data from the primary stream (above).
    
    ::
    
        xyplot(cat[-1].primary.read(), sim.x.name, sim.y.name)
    """
    import matplotlib.pyplot as plt
    
    x = dataset[xname]
    y = dataset[yname]
    title = title or f"{yname} v. {xname}"

    plt.plot(x.values, y.values)
    plt.title(title)
    plt.xlabel(xname)
    plt.ylabel(yname)


def bluesky_md_to_dm(cat, run_ref):
    """
    Contribute a run's metadata to the APS Data Management database.
    
    ::
    
        bluesky_md_to_dm(cat, -1)  # most recent run
    """
    from dm import CatApiFactory

    run = cat[run_ref]
    experimentName = cat.name  # databroker catalog name
    runId = f"uid_{run.metadata['start']['uid'][:8]}"  # first part of run uid
    runInfo = dict(
        experimentName=experimentName,
        runId=runId,
        metadata={k: getattr(run, k).metadata for k in run}  # all streams
    )

    api = CatApiFactory.getRunCatApi()
    md = api.addExperimentRun(runInfo)
    # # confirm
    # mdl = api.getExperimentRuns(experimentName)
    return md
