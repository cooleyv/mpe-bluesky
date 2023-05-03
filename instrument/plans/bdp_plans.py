"""
Plans for use by the BDP
"""

__all__ = [
    "demo202305",
]

import logging

logger = logging.getLogger(__name__)

logger.info(__file__)

from bluesky import plan_stubs as bps
import pathlib

from ..devices import DM_Workflow

DEFAULT_IMAGE_DIR = pathlib.Path("/home/1-id")  # TODO: s1iddata


def demo202305(
    image_dir=str(DEFAULT_IMAGE_DIR),
    fly_scan_time=60,
    dm_workflow="example-01",
    dm_filePath="/home/beams/S1IDTEST/.bashrc",
    dm_timeout=180,
    dm_wait=True,
    md={}
):
    """
    BDP: Simulate acquisition of a set of image files and start DM workflow.

    Examples::

        # all the defaults
        RE(demo202305())

        # non-default values
        RE(demo202305(fly_scan_time=2, md=dict(title="BS+DM test")))

    Wait to kickoff the DM workflow if a previous workflow is still running.
    """
    image_path = pathlib.Path(image_dir)
    logger.info(
        "In demo202305() plan."
        f"  {image_dir=}"
        f" (exists: {image_path.exists()})"
        f" {fly_scan_time=} s"
        f" {md=} s"
        )

    logger.info(f"Simulate fly scan for {fly_scan_time} s")
    # TODO: generate run documents?
    yield from bps.sleep(fly_scan_time)
    logger.info("Data collection (simulation) complete.")

    logger.info(f"Start DM workflow: {dm_workflow=}")
    wf = DM_Workflow(dm_workflow, filePath=dm_filePath, imageDir=image_dir)
    # DM_Workflow code is not a bluesky plan or ophyd,
    # no need to "yield from ..."
    # Not yet, at least.
    wf.start_workflow(wait=dm_wait, timeout=dm_timeout)
    if dm_wait:
        while not wf.idle:
            yield from bps.sleep(1)
    logger.info("Bluesky plan demo202305() complete.")
