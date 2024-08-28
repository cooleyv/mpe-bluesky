"""
Contains plugin classes needed to build area detectors, 
modified for use by the MPE group. 

TODO: add all to export 
"""


__all__ = [
    "MPE_CamBase",
    "MPE_CamBase_V31",
    "MPE_CamBase_V34",
    "MPE_ImagePlugin",
    "MPE_ImagePlugin_V31",
    "MPE_ImagePlugin_V34",
    "MPE_PvaPlugin",
    "MPE_PvaPlugin_V31",
    "MPE_PvaPlugin_V34",
    "MPE_ProcessPlugin",
    "MPE_ProcessPlugin_V31",
    "MPE_ProcessPlugin_V34",
    "MPE_TransformPlugin",
    "MPE_TransformPlugin_V31",
    "MPE_TransformPlugin_V34",
    "MPE_OverlayPlugin",
    "MPE_OverlayPlugin_V31",
    "MPE_OverlayPlugin_V34",
    "MPE_ROIPlugin",
    "MPE_ROIPlugin_V31",
    "MPE_ROIPlugin_V34",
    "MPE_TIFFPlugin",
    "MPE_TIFFPlugin_V31",
    "MPE_TIFFPlugin_V34",
    "MPE_HDF5Plugin",
    "MPE_HDF5Plugin_V31",
    "MPE_HDF5Plugin_V34",
]

#import mod components from ophyd
from ophyd import DetectorBase
from ophyd import SingleTrigger
from ophyd import ADComponent
from ophyd import EpicsSignal
from ophyd import EpicsSignalWithRBV
from ophyd import EpicsSignalRO

#import plugin base versions from ophyd (v1.9.1)
"""Used for 1-ID retiga cameras."""
from ophyd.areadetector import CamBase
from ophyd.areadetector.plugins import PluginBase
from ophyd.areadetector.plugins import ImagePlugin
from ophyd.areadetector.plugins import PvaPlugin
from ophyd.areadetector.plugins import ProcessPlugin
from ophyd.areadetector.plugins import TransformPlugin
from ophyd.areadetector.plugins import OverlayPlugin
from ophyd.areadetector.plugins import ROIPlugin
from ophyd.areadetector.plugins import TIFFPlugin
from ophyd.areadetector.plugins import HDF5Plugin

#import plugins v3.1
"""Used for 1-ID pixirad IOC using v3.2 ADcore."""
from ophyd.areadetector.plugins import PluginBase_V31
from ophyd.areadetector.plugins import ImagePlugin_V31
from ophyd.areadetector.plugins import PvaPlugin_V31
from ophyd.areadetector.plugins import ProcessPlugin_V31
from ophyd.areadetector.plugins import TransformPlugin_V31
from ophyd.areadetector.plugins import OverlayPlugin_V31
from ophyd.areadetector.plugins import ROIPlugin_V31
from ophyd.areadetector.plugins import TIFFPlugin_V31
from ophyd.areadetector.plugins import HDF5Plugin_V31

#import plugins v3.4
"""Used for all other 1-ID and 20-ID dets. ADcore v3.4 and later."""
from ophyd.areadetector.plugins import PluginBase_V34
from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import PvaPlugin_V34
from ophyd.areadetector.plugins import ProcessPlugin_V34
from ophyd.areadetector.plugins import TransformPlugin_V34
from ophyd.areadetector.plugins import OverlayPlugin_V34
from ophyd.areadetector.plugins import ROIPlugin_V34
from ophyd.areadetector.plugins import TIFFPlugin_V34
from ophyd.areadetector.plugins import HDF5Plugin_V34

#import iterative file writers from apstools
from apstools.devices.area_detector_support import AD_EpicsTIFFIterativeWriter
from apstools.devices.area_detector_support import AD_EpicsHDF5IterativeWriter


#generate custom plugin mixin classes for MPE group
class MPE_PluginMixin(PluginBase): ...
class MPE_PluginMixin_V31(PluginBase_V31):...
class MPE_PluginMixin_V34(PluginBase_V34):...

#generate custom cambase classes
class MPE_CamBase(CamBase): ...

class MPE_CamBase_V31(CamBase): 
    """Contains updates to CamBase since v22."""
    pool_max_buffers = None
    
class MPE_CamBase_V34(CamBase):
    """Contains updates to CamBase since v22."""
    pool_max_buffers = None
    

#generate custom plugin classes
class MPE_ImagePlugin(ImagePlugin):...
class MPE_ImagePlugin_V31(ImagePlugin_V31):...
class MPE_ImagePlugin_V34(ImagePlugin_V34):...

class MPE_PvaPlugin(PvaPlugin):...
class MPE_PvaPlugin_V31(PvaPlugin_V31):...
class MPE_PvaPlugin_V34(PvaPlugin_V34):...

class MPE_ProcessPlugin(ProcessPlugin):...
class MPE_ProcessPlugin_V31(ProcessPlugin_V31):...
class MPE_ProcessPlugin_V34(ProcessPlugin_V34):...

class MPE_TransformPlugin(TransformPlugin):...
class MPE_TransformPlugin_V31(TransformPlugin_V31):...
class MPE_TransformPlugin_V34(TransformPlugin_V34):...

class MPE_OverlayPlugin(OverlayPlugin):...
class MPE_OverlayPlugin_V31(OverlayPlugin_V31):...
class MPE_OverlayPlugin_V34(OverlayPlugin_V34):...

class MPE_ROIPlugin(ROIPlugin):...
class MPE_ROIPlugin_V31(ROIPlugin_V31):...
class MPE_ROIPlugin_V34(ROIPlugin_V34):...


#create custom file writer classes
class MPE_TIFFPlugin(AD_EpicsTIFFIterativeWriter, TIFFPlugin):...
class MPE_TIFFPlugin_V31(AD_EpicsTIFFIterativeWriter, TIFFPlugin_V31):...
class MPE_TIFFPlugin_V34(AD_EpicsTIFFIterativeWriter, TIFFPlugin_V34):...

class MPE_HDF5Plugin(AD_EpicsHDF5IterativeWriter, HDF5Plugin):...
class MPE_HDF5Plugin_V31(AD_EpicsHDF5IterativeWriter, HDF5Plugin_V31):...
class MPE_HDF5Plugin_V34(AD_EpicsHDF5IterativeWriter, HDF5Plugin_V34):
    """Contains some updates to HDF plugin."""
    pool_max_buffers = None


