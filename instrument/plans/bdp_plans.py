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
from bluesky import plans as bp
import pathlib

# from ..framework.initialize import bec
# from ..framework import dm_start_workflow
from ..devices import DM_Workflow

DEFAULT_IMAGE_DIR = "/home/1-id"  # TODO: s1iddata


def demo202305(
    image_dir=DEFAULT_IMAGE_DIR, 
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
        RE(demo202305("/home/1-id/s1iduser", 2))

    Wait to kickoff the DM workflow if a previous workflow is still running.
    """
    image_path = pathlib.Path(image_dir)
    print(
        "In demo202305() plan."
        f"  {image_dir=}"
        f" (exists: {image_path.exists()})"
        f" {fly_scan_time=} s"
        f" {md=} s"
        )

    print(f"Simulate fly scan for {fly_scan_time} s")
    yield from bps.sleep(fly_scan_time)

    print("Data collection (simulation) complete.")
    print(f"Start DM workflow: {dm_workflow=}")
    wf = DM_Workflow(dm_workflow, filePath=dm_filePath)
    wf.start_workflow(wait=dm_wait, timeout=dm_timeout)
    if dm_wait:
        while not wf.idle:
            yield from bps.sleep(1)
