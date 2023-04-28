"""
APS only: connect with facility information
"""

__all__ = [
    "aps",
]

import logging

logger = logging.getLogger(__name__)

logger.info(__file__)

import apstools.devices


class MyAPSMachine(apstools.devices.ApsMachineParametersDevice):

    # TODO: Confirm these are available during APS-U commissioning
    # not available during APS year-long shutdown
    global_feedback = None
    global_feedback_h = None
    global_feedback_v = None


aps = MyAPSMachine(name="aps")
