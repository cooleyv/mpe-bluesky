"""
Connect with APS Data Management workflows.

from: XPCS & S1IDTEST
"""

__all__ = """
    dm_experiment
    DM_WorkflowConnector
    dm_workflow
""".split()

import logging

from ophyd import Signal

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # allow any log content at this level
logger.info(__file__)

# from apstools.devices import DM_WorkflowConnector
from ._apstools_data_management import DM_WorkflowConnector  # noqa
from ..utils import dm_api_proc

dm_workflow = DM_WorkflowConnector(name="dm_workflow")
dm_workflow.owner.put(dm_api_proc().username)

# TODO: make this an EpicsSignal instead
dm_experiment = Signal(name="dm_experiment", value="")
