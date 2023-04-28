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

from ..framework.initialize import bec

DEFAULT_IMAGE_DIR = "/home/1-id"  # TODO: s1iddata


def demo202305(image_dir=DEFAULT_IMAGE_DIR, fly_scan_time=60):
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
        f" {fly_scan_time=} s",
        )

    print(f"Simulate fly scan for {fly_scan_time} s")
    yield from bps.sleep(fly_scan_time)

    print("Data collection complete.")
