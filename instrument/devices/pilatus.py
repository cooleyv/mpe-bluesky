"""
Contains class for pilatus detector.
"""


__all__ = [

]

#import for logging
import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#import from ophyd 
from ophyd import DetectorBase, Pilatus