# Data Management for the BDP

Related to BDP activities in 2023-05.

- [Data Management for the BDP](#data-management-for-the-bdp)
  - [Example workflow](#example-workflow)
  - [DM command line API examples](#dm-command-line-api-examples)
  - [Install the DM package](#install-the-dm-package)
  - [Using the DM package](#using-the-dm-package)
  - [DM python API](#dm-python-api)
  - [Example](#example)

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
