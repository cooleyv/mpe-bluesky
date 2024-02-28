"""
EPICS area_detector common support
"""

__all__ = """
    GE_AreaDetector
""".split()

import logging
from pathlib import PurePath

from apstools.devices import AD_EpicsFileNameHDF5Plugin
from apstools.devices import AD_plugin_primed
from apstools.devices import AD_prime_plugin2
from apstools.devices import CamMixin_V34
from ophyd import ADComponent
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd.areadetector import CamBase
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import SimDetectorCam
from ophyd.areadetector import SingleTrigger
from ophyd.areadetector.plugins import CodecPlugin_V34
from ophyd.areadetector.plugins import FileBase
from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import OverlayPlugin_V34
from ophyd.areadetector.plugins import PluginBase_V34
from ophyd.areadetector.plugins import ProcessPlugin_V34
from ophyd.areadetector.plugins import PvaPlugin_V34
from ophyd.areadetector.plugins import ROIPlugin_V34
from ophyd.areadetector.plugins import StatsPlugin_V34
from ophyd.areadetector.plugins import TransformPlugin_V34
from ophyd.ophydobj import Kind
from ophyd.status import Status

logger = logging.getLogger(__name__)
logger.info(__file__)

# from .. import iconfig  # noqa


class CamBase_V34(CamBase):
    """
    Updates to CamBase since v22.

    PVs removed from AD now.
    """

    pool_max_buffers = None


class FileBase_V34(FileBase):
    """
    Updates to FileBase since v22.

    PVs removed from AD now.
    """

    file_number_sync = None
    file_number_write = None


class GeDetectorCam_V34(CamMixin_V34, SimDetectorCam):
    """Camera support for the GE amorphous silicon detector."""

    _html_docs = "geAmorphousSiliconDetectorDoc.html"  # just a name

    number_rows_user_sseq1 = ADComponent(
        EpicsSignal, "NumberOfRowsForUserSeq1", kind="config"
    )
    number_columns_user_sseq1 = ADComponent(
        EpicsSignal, "NumberOfColumnsForUserSeq1", kind="config"
    )

    # initialize = ADComponent(EpicsSignal, "Initialize", kind="config")

    # # These components not found on GE detectors at 1-ID-E
    # file_number_sync = None
    # file_number_write = None
    # fw_clear = None
    # link_0 = None
    # link_1 = None
    # link_2 = None
    # link_3 = None
    # dcu_buff_free = None
    # offset = None


class Hydra_PluginMixin(PluginBase_V34):
    """Remove property attribute found in AD IOCs now."""

    _asyn_pipeline_configuration_names = None


class Hydra_EpicsFileNameHDF5Plugin(Hydra_PluginMixin, AD_EpicsFileNameHDF5Plugin):
    """Let EPICS control the file name.  Plugin for Ge aSi detector."""

    @property
    def _plugin_enabled(self):
        return self.stage_sigs.get("enable") in (1, "Enable")

    def generate_datum(self, *args, **kwargs):
        if self._plugin_enabled:
            super().generate_datum(*args, **kwargs)

    def read(self):
        if self._plugin_enabled:
            readings = super().read()
        else:
            readings = {}
        return readings

    def stage(self):
        if self._plugin_enabled:
            staged_objects = super().stage()
        else:
            staged_objects = []
        return staged_objects

    def trigger(self):
        if self._plugin_enabled:
            trigger_status = super().trigger()
        else:
            trigger_status = Status(self)
            trigger_status.set_finished()
        return trigger_status


class Hydra_CodecPlugin(Hydra_PluginMixin, CodecPlugin_V34):
    """CODEC plugin for Ge aSi detector."""


class Hydra_ImagePlugin(Hydra_PluginMixin, ImagePlugin_V34):
    """Image plugin for Ge aSi detector."""


class Hydra_OverlayPlugin(Hydra_PluginMixin, OverlayPlugin_V34):
    """Overlay plugin for Ge aSi detector."""


class Hydra_ProcessPlugin(Hydra_PluginMixin, ProcessPlugin_V34):
    """Process plugin for Ge aSi detector."""


class Hydra_PvaPlugin(Hydra_PluginMixin, PvaPlugin_V34):
    """PVA plugin for Ge aSi detector."""


class Hydra_ROIPlugin(Hydra_PluginMixin, ROIPlugin_V34):
    """ROI plugin for Ge aSi detector."""


class Hydra_StatsPlugin(Hydra_PluginMixin, StatsPlugin_V34):
    """Stats plugin for Ge aSi detector."""


class Hydra_TransformPlugin(Hydra_PluginMixin, TransformPlugin_V34):
    """Transform plugin for Ge aSi detector."""


class GE_AreaDetector(SingleTrigger, DetectorBase):
    """Ge amorphous silicon area detector."""

    # camera interface
    cam = ADComponent(GeDetectorCam_V34, "cam1:")

    # plugins for visualization and streaming
    image = ADComponent(Hydra_ImagePlugin, "image1:")
    pva = ADComponent(Hydra_PvaPlugin, "Pva1:")

    # plugins for image processing
    codec1 = ADComponent(CodecPlugin_V34, "CODEC1:")
    # over1 = ADComponent(Hydra_OverlayPlugin, "Over1:")
    proc1 = ADComponent(Hydra_ProcessPlugin, "Proc1:")
    roi1 = ADComponent(Hydra_ROIPlugin, "ROI1:")
    # stats1 = ADComponent(Hydra_StatsPlugin, "Stats1:")
    trans1 = ADComponent(Hydra_TransformPlugin, "Trans1:")

    # plugins for file writing
    # TODO: edf = ADComponent(Hydra_EdfFilePlugin, "EDF1:")
    hdf1 = ADComponent(
        Hydra_EpicsFileNameHDF5Plugin,
        "HDF1:",
        write_path_template=f"{PurePath('/')}/",
        read_path_template=f"{PurePath('/')}/",
        kind="normal",
    )
