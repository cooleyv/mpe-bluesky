"""
Connect with APS Data Management workflows.
"""

__all__ = """
    DM_Workflow
    dm_workflow
""".split()

import logging
import os
import pathlib  # TODO: remove
import time

logger = logging.getLogger(__name__)

logger.info(__file__)

from apstools.utils import run_in_thread
from dm import ProcApiFactory
from ophyd import Component, Device, Signal

DEFAULT_FILE_PATH = pathlib.Path.home() / "BDP" / "etc" / "dm.setup.sh"  # TODO: remove
DEFAULT_WORKFLOW_NAME = "example-01"  # TODO use ""
ID_NO_JOB = "not_run"
ID_JOB_STARTING = "starting"
DEFAULT_WORKFLOW_ARGS = dict(filePath=str(DEFAULT_FILE_PATH))  # TODO use {}


class DM_Workflow(Device):
    """
    Support for the APS Data Management tools.

    The DM workflow dictionary of arguments ()``workflow_kwargs``)
    needs special attention.  Python's ``dict`` structure is not
    compatible with MongoDB.  In turn, ophyd does not support it.
    A custom plan can choose how to use `the `workflow_kwargs`` dictionary:
        - use with DM workflow, as planned
        - add ``workflow_kwargs`` to the start metadata
        - write as run stream::

            from apstools.devices import make_dict_device
            from apstools.plans import write_stream

            yield from write_stream(
                [
                    make_dict_device(workflow_kwargs, name="kwargs")
                ],
                "dm_workflow_kwargs"
            )
    """

    # TODO: revise these names
    workflow_name = Component(Signal, value=DEFAULT_WORKFLOW_NAME)
    # Dictionary structure is not compatible with MongoDB.
    # So, ophyd, in turn, does not support it.
    workflow_kwargs = DEFAULT_WORKFLOW_ARGS
    job = None
    job_id = Component(Signal, value=ID_NO_JOB, kind="config")
    owner = Component(
        Signal, value=str(os.environ["DM_STATION_NAME"]).lower(), kind="config"
    )
    wait_loop_period = Component(Signal, value=0.02, kind="config")
    wait_reporting_period = Component(Signal, value=10, kind="config")
    wait_reporting_verbose = Component(Signal, value=True, kind="config")

    # ophyd objects to record as run data
    processing_stage_id = Component(Signal, value=ID_NO_JOB)
    processing_stage_status = Component(Signal, value=ID_NO_JOB)
    processing_status = Component(Signal, value=ID_NO_JOB)
    run_time = Component(Signal, value=0)
    exit_status = Component(Signal, value=ID_NO_JOB, kind="config")
    error_message = Component(Signal, value="", kind="config")
    # TODO: stdOut from each stage

    def __repr__(self):
        innards = f"'{self.workflow_name.get()}'" f", argsDict={self.workflow_kwargs}"
        if self.job_id.get() != ID_NO_JOB:
            innards += f", id='{self.job_id.get()}'"
        return f"DM_Workflow({innards})"

    def __init__(self, name=None, workflow=DEFAULT_WORKFLOW_NAME, **kwargs):
        if name is None:
            raise KeyError("Must provide value for 'name'.")
        super().__init__(name=name)
        self.workflow_name.put(workflow)
        self.workflow_kwargs.update(kwargs)
        self.api = ProcApiFactory.getWorkflowProcApi()

    def start_workflow(self, name="", wait=False, timeout=120, **kwargs):
        """Kickoff a DM workflow with optional wait & timeout."""
        if name == "":
            wfname = self.workflow_name.get()
        else:
            wfname = name
        wfargs = self.workflow_kwargs.copy()
        wfargs.update(kwargs)

        @run_in_thread
        def _run_DM_workflow_thread():
            logger.info("run DM workflow: %s", self.workflow_name.get())
            self.job = self.api.startProcessingJob(
                workflowOwner=self.owner.get(),
                workflowName=wfname,
                argsDict=wfargs,
            )
            self.job_id.put(self.job["id"])
            logger.info("DM workflow started: %s", self.status)

            if wait:
                logger.info("Waiting for DM workflow: id=%s", self.job_id.get())
                self.wait_processing(timeout=timeout)
                logger.info("DM workflow: %s", self.status)

        self.job = ID_JOB_STARTING
        self.job_id.put(ID_NO_JOB)
        logger.info("start_workflow()")
        _run_DM_workflow_thread()
        self.processing_status.put(self.status)

    def wait_processing(self, timeout=120):
        """Wait for the DM workflow to finish."""
        if self.idle:
            return None
        t0 = time.time()
        timeout_deadline = t0 + timeout
        report_deadline = t0
        while not self.idle and time.time() < timeout_deadline:
            if self.wait_reporting_verbose.get():
                st = self.status
                report_now = (
                    st != self.processing_status.get()
                    or time.time() >= report_deadline
                )
                if report_now :
                    self.processing_status.put(st)
                    logger.info(
                        "DM workflow: %s, waiting %.2f s", self.status, time.time() - t0
                    )
                    report_deadline = time.time() + self.wait_reporting_period.get()
            time.sleep(self.wait_loop_period.get())
        self.processing_status.put(self.status)
        if self.idle:
            return
        raise TimeoutError(f"{self} after {timeout} s.")

    def run_as_plan(self, wf_name, wait=True, timeout=180, **kwargs):
        from bluesky import plan_stubs as bps

        # TODO: wf_name & kwargs into start metadata
        # TODO: wf_name & kwargs into document stream

        self.start_workflow(name=wf_name, wait=wait, timeout=timeout, **kwargs)
        if wait:
            while not self.idle:
                yield from bps.sleep(1)

    @property
    def idle(self):
        if self.job_id.get() == ID_NO_JOB:
            st = self.job  # ID_JOB_STARTING or instance of DM processing job
        else:
            st = self.processing_job.get("status", "unknown")
        return st in (ID_NO_JOB, "done")

    @property
    def processing_job(self):
        """Return the processing job for the current job_id."""
        # self.job and self.processing are different snapshots of the same process
        # TODO: refactor to update self.job
        if self.job_id.get() != ID_NO_JOB:
            return self.api.getProcessingJobById(self.owner.get(), self.job_id.get())

    @property
    def processing_jobs(self):
        """Return the list of processsing jobs."""
        return self.api.listProcessingJobs(self.owner.get())

    @property
    def status(self):
        """Return the job status."""
        pjob = self.processing_job
        if pjob is None:
            return
        pdict = pjob.getDictRep()
        self.processing_stage_id.put(pdict['stage'])
        self.processing_stage_status.put(pdict['status'])

        self.run_time.put(pdict.get("runTime", "-n/a-"))
        self.exit_status.put(pdict.get("exitStatus", "-n/a-"))
        self.error_message.put(pdict.get("stdErr", "-n/a-"))

        report = (
            f"id={pdict['id'][:8]}"
            f" {pdict['stage']}"
            f"({pdict['status']})"
            # f" runTime={pdict['runTime']:.2f}"
            # f" started={pdict['startTimestamp']}"
        )
        return report

    @property
    def workflows(self):
        """Return the list of workflows."""
        return self.api.listWorkflows(self.owner.get())


dm_workflow = DM_Workflow(name="dm_workflow", labels=["DM"])
