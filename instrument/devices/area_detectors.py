""" 
EPICS area detectors not part of the hydra system.
#TODO: Update point grey with more specific name that indicates which point grey it is
#TODO: Add detectors as needed
"""

__all__ = [
    "pixirad",
    "pointgrey",
]

import logging 

logger = logging.getLogger(__name__)
logger.info(__file__)

from .ad_factory import MPEAreaDetectorFactory
from .. import iconfig

#Import plugin enable/disable statuses from iconfig for each detector
pg_conf = iconfig["AREA_DETECTOR"]["POINT_GREY"]
pixirad_conf = iconfig["AREA_DETECTOR"]["PIXIRAD"]


#Generate detectors using the area detector factory (see `ad_factory.py`)
pixirad = MPEAreaDetectorFactory(
    "PIXIRAD", 
    use_image     = pixirad_conf["USE_IMAGE"],
    use_overlay   = pixirad_conf["USE_OVERLAY"],
    use_process   = pixirad_conf["USE_PROC"],
    use_pva       = pixirad_conf["USE_PVA"],
    use_roi       = pixirad_conf["USE_ROI"],
    use_stats     = pixirad_conf["USE_STATS"],
    use_transform = pixirad_conf["USE_TRANSFORM"])

pointgrey = MPEAreaDetectorFactory(
    "POINT_GREY", 
    use_image     = pg_conf["USE_IMAGE"],
    use_overlay   = pg_conf["USE_OVERLAY"],
    use_process   = pg_conf["USE_PROC"],
    use_pva       = pg_conf["USE_PVA"],
    use_roi       = pg_conf["USE_ROI"],
    use_stats     = pg_conf["USE_STATS"],
    use_transform = pg_conf["USE_TRANSFORM"])


