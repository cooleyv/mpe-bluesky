# Bluesky Instrument for MPE
# Includes 20-ID and 1-ID

## Quick Reference

- all
  
  ```bash
  bash
  cd ~/bluesky
  become_bluesky
  ```

  Start the QS GUI:

  ```bash
  queue-monitor \
  --zmq-control-addr tcp://kurtag.xray.aps.anl.gov:60615 \
  --zmq-info-addr tcp://kurtag.xray.aps.anl.gov:60625 &
  ```

<!--
usage: queue-monitor \
  --zmq-control-addr tcp://localhost:60615. \
  --zmq-info-addr tcp://localhost:60625 \
  --http-server-uri http://localhost:60610
-->

  Watch the QS console from a terminal session:

  ```bash
  qserver-console-monitor --zmq-info-addr tcp://kurtag.xray.aps.anl.gov:60625
  ```

- kurtag: QS (queueserver) server
  
  ```bash
  ./qserver.sh start
  ```

- kurtag: `git` and `conda` activities (need an external workstation, not kurtag)
- erkel: data processing

## CAUTION

**Caution**:  Uses the bluesky queueserver (QS).  _Every_ Python file in this
directory will be executed when QS starts the RunEngine. Don't add extra Python
files to this directory.  Instead, put them in `user/` or somewhere else.

## For more information

For more information, see: 

- Queueserver:
  - [notes](./qserver.md)
  - [tutorial](https://blueskyproject.io/bluesky-queueserver/tutorial.html#running-re-manager-with-custom-startup-code)
  - XPCS [README](https://github.com/APS-8ID-DYS/bluesky)
- Bluesky Training:
  - Queueserver [hints](https://github.com/BCDA-APS/bdp_controls/blob/main/qserver/README.md)
  - General [How-to, examples, tutorials, reference](https://bcda-aps.github.io/bluesky_training)
