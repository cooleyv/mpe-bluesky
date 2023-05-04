# Data Management for the BDP

Related to BDP activities in 2023-05.

- [Data Management for the BDP](#data-management-for-the-bdp)
  - [Example workflow](#example-workflow)
  - [DM command line API examples](#dm-command-line-api-examples)
  - [Install the DM package](#install-the-dm-package)
  - [Using the DM package](#using-the-dm-package)
  - [DM python API](#dm-python-api)
  - [Example](#example)
  - [2023-05-03](#2023-05-03)
    - [Example stage content](#example-stage-content)
- [Send metadata to DM](#send-metadata-to-dm)

## Example workflow

here is an example workflow for testing :

    /clhome/BDP/DM/production/examples/example-workflows/workflow-example-01.py

## DM command line API examples

```bash
(dm-user) bdp@terrier ~/DM $ source /clhome/BDP/DM/etc/dm.setup.sh

(dm-user) bdp@terrier ~/DM $ dm-list-workflows
id=6450e7c62d5d572a6b94a270 name=example-01 owner=bdp

(dm-user) bdp@terrier ~/DM $ dm-start-processing-job --workflow-name example-01 filePath:/clhome/BDP/.bashrc
id=cf6848a3-4b6f-47a5-8fbc-e3159b35672b owner=bdp status=pending

(dm-user) bdp@terrier ~/DM $ dm-get-processing-job --id=cf6848a3-4b6f-47a5-8fbc-e3159b35672b
id=cf6848a3-4b6f-47a5-8fbc-e3159b35672b owner=bdp status=running stage=10-REPEAT startTime=1683023996.805251 startTimestamp=2023/05/02 05:39:56 CDT

(dm-user) bdp@terrier ~/DM $ dm-get-processing-job --id=cf6848a3-4b6f-47a5-8fbc-e3159b35672b
id=cf6848a3-4b6f-47a5-8fbc-e3159b35672b owner=bdp status=done stage=13-DONE startTime=1683023996.805251 endTime=1683024074.9024842 runTime=78.10 startTimestamp=2023/05/02 05:39:56 CDT endTimestamp=2023/05/02 05:41:14 CDT
```

Note the `status` key in the above, which can be used for monitoring job progress

## Install the DM package

Here is how to install DM conda package:

```bash
$ conda create -n dm-api -c apsu aps-dm-api
$ conda activate dm-api
```

Once installed, the API docs can be found locally:

    $ ls ${CONDA_PREFIX}/opt/dm/doc/html/

## Using the DM package

Sourcing the DM setup file handles configuration and authentication, the relevant environment variables are:

```bash
(dm-api) bdp@terrier ~/DM $ env | grep DM_LOGIN
DM_LOGIN_FILE=/clhome/BDP/DM/etc/.bdp.system.login

(dm-api) bdp@terrier ~/DM $ env | grep DM_PROC
DM_PROC_WEB_SERVICE_URL=https://terrier.xray.aps.anl.gov:55536
```

Once you have the above, using api is straightforward:

```py
>>> from dm import ProcApiFactory
>>> api = ProcApiFactory.getWorkflowProcApi()
>>> api.listWorkflows(owner='bdp')
[{'name': 'example-01', 'owner': 'bdp', 'stages': {'01-START': {'command': '/bin/date +%Y%m%d%H%M%S', '
```

## DM python API

Here is how to submit and monitor job via API:

```py
>>> from dm import ProcApiFactory
>>> api = ProcApiFactory.getWorkflowProcApi()
>>> job=api.startProcessingJob(workflowOwner='bdp', workflowName='example-01', argsDict={'filePath' : '/clhome/BDP/.bashrc'})
>>> print(job['id'])
7802a648-35d7-42ed-b17e-0089791076e4
>>> print(api.getProcessingJobById(owner='bdp', id='7802a648-35d7-42ed-b17e-0089791076e4')['status'])
```

Note that jobs require some sort of input file specification, and in the above I
gave it a single file using `filePath` key. The spec you provide will depend on
the workflow. We mostly use `filePath`, but there are others we can use, and
implement new ones if we need to.

## Example

<pre>
haydn% <b>bash</b>
(base) s1idtest@haydn ~ $ <b>conda activate dm-api</b>
(dm-api) s1idtest@haydn ~ $ <b>source BDP/etc/dm.setup.sh</b>
(dm-api) s1idtest@haydn ~ $ <b>python</b>
Python 3.10.11 (main, Apr 20 2023, 19:02:41) [GCC 11.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> <b>from dm import ProcApiFactory</b>
>>> <b>api = ProcApiFactory.getWorkflowProcApi()</b>
>>> <b>api.listWorkflows(owner='bdp')</b>
[{'name': 'example-01', 'owner': 'bdp', 'stages': {'01-START': {'command': '/bin/date +%Y%m%d%H%M%S', 'outputVariableRegexList': ['(?P<timeStamp>.*)']}, '02-MKDIR': {'command': '/bin/mkdir -p /tmp/workflow.$timeStamp'}, '03-ECHO': {'command
</pre>

## 2023-05-03

so as far as terminology, DM Workflow class is a template, and ProcessingJob is
the thing you will run and get back from DM services

for starters you can report final job status and runtime, perhaps startTime and
endTime keys, and if things fail, you can pull the last stage, and get last
command error and exit status

Attributes `self.job` and `self.processing_job` are snapshots of the same
process. It must be updated while the job is running.  This is a *poll-only*
API.  DM will not provide an update as the processing stage changes. Content
might be updated faster than 1 second but any stage could take much longer (hour
or more). It is the same process, the content just grows (every time you call
it) as the process runs.

top level keys are the most important overall

### Example stage content

```py

    '10-REPEAT': {'command': 'echo "Count: `expr $count + 1`"',
        'outputVariableRegexList': ['Count: (?P<count>.*)'],
        'repeatPeriod': 10,
        'repeatUntil': '"$count" == "$randomNumber"',
        'maxRepeats': 10,
        'childProcesses': {'9': {'stageId': '10-REPEAT',
        'childProcessNumber': 9,
        'command': 'echo "Count: `expr 0 + 1`"',
        'workingDir': None,
        'status': 'done',
        'submitTime': 1683150326.997442,
        'startTime': 1683150326.9997125,
        'endTime': 1683150327.0023093,
        'runTime': 0.0025968551635742188,
        'exitStatus': 0,
        'stdOut': 'Count: 1\n',
        'stdErr': ''},
        '10': {'stageId': '10-REPEAT',
        'childProcessNumber': 10,
        'command': 'echo "Count: `expr 1 + 1`"',
        'workingDir': None,
        'status': 'done',
        'submitTime': 1683150327.0024977,
        'startTime': 1683150337.005433,
        'endTime': 1683150337.008252,
        'runTime': 0.0028188228607177734,
        'exitStatus': 0,
        'stdOut': 'Count: 2\n',
        'stdErr': ''},
        '11': {'stageId': '10-REPEAT',
        'childProcessNumber': 11,
        'command': 'echo "Count: `expr 2 + 1`"',
        'workingDir': None,
        'status': 'done',
        'submitTime': 1683150337.008671,
        'startTime': 1683150347.0111377,
        'endTime': 1683150347.013724,
        'runTime': 0.00258636474609375,
        'exitStatus': 0,
        'stdOut': 'Count: 3\n',
        'stdErr': ''},
```

# Send metadata to DM

2023-05-04

```py
>>> from dm import CatApiFactory

>>> api = CatApiFactory.getRunCatApi()

>>> metadata = {'resource': {'spec': 'AD_HDF5', 'root': '/', 'resource_path': 'clhome/BDP/voyager/adsimdet/2022/08/30/d585f272-dd9b-4ac0-b521_000.h5', 'resource_kwargs': {'frame_per_point': 1}, 'path_semantics': 'posix','uid': '506944a6-7632-4db8-9448-82b258211ed4','run_start': '43044b6e-f6ba-48cb-a975-90d236dcbaaa'},'datum_page': {'resource': '506944a6-7632-4db8-9448-82b258211ed4','datum_id': ['506944a6-7632-4db8-9448-82b258211ed4']}}

>>> runInfo = {'experimentName' : 'bdp-test-01', 'runId' : 'pj01', 'metadata' : metadata}

>>> md = api.addExperimentRun(runInfo)

>>> print(md)

{'experimentName': 'bdp-test-01', 'runId': 'pj01', 'metadata': {'resource': {'spec': 'AD_HDF5', 'root': '/', 'resource_path': 'clhome/BDP/voyager/adsimdet/2022/08/30/d585f272-dd9b-4ac0-b521_000.h5', 'resource_kwargs': {'frame_per_point': 1}, 'path_semantics': 'posix', 'uid': '506944a6-7632-4db8-9448-82b258211ed4', 'run_start': '43044b6e-f6ba-48cb-a975-90d236dcbaaa'}, 'datum_page': {'resource': '506944a6-7632-4db8-9448-82b258211ed4', 'datum_id': ['506944a6-7632-4db8-9448-82b258211ed4']}}, 'id': '63ed2bc18840ea27d37289ae'}

>>> mdl = api.getExperimentRuns('bdp-test-01')

>>> print(mdl)

[{'experimentName': 'bdp-test-01', 'runId': 'pj01', 'metadata':
```

as

```py
from dm import CatApiFactory

run = cat[-1]
experimentName = cat.name  # databroker catalog name
runId = f"uid_{run.metadata['start']['uid'][:8]}"  # first part of run uid
runInfo = dict(
    experimentName=experimentName,
    runId=runId,
    metadata={k: getattr(run, k).metadata for k in run}  # all streams
)

api = CatApiFactory.getRunCatApi()
md = api.addExperimentRun(runInfo)
# confirm
mdl = api.getExperimentRuns(experimentName)
```
