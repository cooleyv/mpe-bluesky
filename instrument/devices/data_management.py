"""
Connect with APS Data Management workflows.
"""

__all__ = [
    "DM_Workflow",
]

import logging
import os
import pathlib
import time

logger = logging.getLogger(__name__)

logger.info(__file__)

from apstools.utils import run_in_thread
from dm import ProcApiFactory

DEFAULT_FILE_PATH = pathlib.Path.home() / "BDP" / "etc" / "dm.setup.sh"
DEFAULT_WORKFLOW_NAME = "example-01"


class DM_Workflow:
    """
    Support for the APS Data Management tools.
    """

    workflow_name = DEFAULT_WORKFLOW_NAME
    workflow_args = dict(filePath=str(DEFAULT_FILE_PATH))
    job = None
    job_id = None
    owner = str(os.environ["DM_STATION_NAME"]).lower()
    wait_reporting_period = 2
    wait_reporting_verbose = True

    def __repr__(self):
        innards = (
            f"'{self.workflow_name}'"
            f", argsDict={self.workflow_args}"
        )
        if self.job_id is not None:
            innards += f", id='{self.job_id}'"
        return (f"DM_Workflow({innards})"
        )

    def __init__(self, workflow=DEFAULT_WORKFLOW_NAME, **kwargs):
        self.workflow_name = workflow
        self.workflow_args.update(kwargs)
        self.api = ProcApiFactory.getWorkflowProcApi()

    def start_workflow(self, wait=False, timeout=120):
        """Kickoff a DM workflow with optional wait & timeout."""

        @run_in_thread
        def _run_DM_workflow_thread():
            logger.info("DM workflow starting: workflow: %s", self.workflow_name)
            self.job = self.api.startProcessingJob(
                workflowOwner=self.owner,
                workflowName=self.workflow_name,
                argsDict=self.workflow_args,
            )
            self.job_id = self.job["id"]
            logger.info("DM workflow: %s", self.status)
            
            if wait:
                logger.info("Waiting for DM workflow: id=%s", self.job_id)
                self.wait_processing(timeout=timeout)
                logger.info("DM workflow: %s", self.status)

        logger.info("start_workflow()")
        self.job = "starting"
        _run_DM_workflow_thread()

    def wait_processing(self, timeout=120):
        """Wait for the DM workflow to finish."""
        if self.idle:
            return None
        t0 = time.time()
        deadline = t0 + timeout
        while not self.idle and time.time() < deadline:
            if self.wait_reporting_verbose:
                logger.info(
                    "DM workflow: elapsed=%.1f s, %s",
                    time.time()-t0, self.status
                )
            time.sleep(self.wait_reporting_period)
        if self.idle:
            return
        raise TimeoutError(f"{self} after {timeout} s.")

    @property
    def idle(self):
        if self.job is None:
            st = None
        elif self.job == "starting":
            st = self.job
        else:
            st = self.processing_job.get("status", "unknown")
        return st in (None, "done")

    @property
    def processing_job(self):
        """Return the processing job for the current job_id."""
        if self.job not in (None, "starting"):
            return self.api.getProcessingJobById(self.owner, self.job_id)

    @property
    def processing_jobs(self):
        """Return the list of processsing jobs."""
        return self.api.listProcessingJobs(self.owner)

    @property
    def status(self):
        """Return the job status."""
        pjob = self.processing_job
        if pjob is None:
            return
        pdict = pjob.getDictRep()
        report = (
            f"id={pdict['id'][:7]}"
            f" {pdict['stage']}"
            f"({pdict['status']})"
            f" started={pdict['startTimestamp']}"
        )
        return report

    @property
    def workflows(self):
        """Return the list of workflows."""
        return self.api.listWorkflows(self.owner)
