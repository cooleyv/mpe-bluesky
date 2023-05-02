"""
Setup for for this beam line's APS Data Management Python API client.
"""

__all__ = """
    dm_workflows
    dm_start_workflow
""".split()

import logging
import os
import pathlib

from .. import iconfig

logger = logging.getLogger(__name__)

logger.info(__file__)

DM_SETUP_FILE = iconfig.get("DM_SETUP_FILE")
if DM_SETUP_FILE is None:
    dm_workflows = None
    dm_start_workflow = None
else:
    from dm import ProcApiFactory

    ENV_VAR_FILE = pathlib.Path(DM_SETUP_FILE)
    logger.info("APS DM environment file: %s", str(ENV_VAR_FILE))
    ENV_VARS = {}
    for line in open(ENV_VAR_FILE).readlines():
        if not line.startswith("export "):
            continue
        k, v = line.strip().split()[-1].split("=")
        ENV_VARS[k] = v

    os.environ.update(ENV_VARS)
    BDP_WORKFLOW_OWNER = os.environ["DM_STATION_NAME"].lower()
    logger.info("APS DM workflow owner: %s", BDP_WORKFLOW_OWNER)

    def dm_workflows(owner=BDP_WORKFLOW_OWNER):
        api = ProcApiFactory.getWorkflowProcApi()
        return api.listWorkflows(owner)

    def dm_start_workflow(workflow="example-01", **kwargs):
        """
        Kickoff (start) a DM workflow.

            dm_start_workflow("example-01", filePath="/clhome/BDP/.bashrc")
        """
        api = ProcApiFactory.getWorkflowProcApi()
        job=api.startProcessingJob(
            workflowOwner=BDP_WORKFLOW_OWNER,
            workflowName=workflow,
            argsDict=kwargs,
        )
        job_id = job['id']  # e.g. 7802a648-35d7-42ed-b17e-0089791076e4
        print(f"{job_id=}")
        print(api.getProcessingJobById(owner=BDP_WORKFLOW_OWNER, id=job_id)['status'])
        return job_id
