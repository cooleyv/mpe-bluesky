# Bluesky Instrument for HEXM

## Quick Reference

- all
  
  ```bash
  cd ~/bluesky
  become_bluesky
  ```

  ```bash
  queue-monitor &
  ```

- haydn: QS (queueserver) server
  
  ```bash
  ./qserver.sh start
  ```

- kurtag: `git` and `conda` activities
- erkel: data processing

## CAUTION

**Caution**:  Uses the bluesky queueserver (QS).  _Every_
Python file in this directory will be executed when QS starts the RunEngine.
Don't add extra Python files to this directory.  Instead, put them in `user/` or
somewhere else.

## For more information

For more information, see: 

- Queueserver:
  - [notes](./qserver.md)
  - [tutorial](https://blueskyproject.io/bluesky-queueserver/tutorial.html#running-re-manager-with-custom-startup-code)
  - XPCS [README](https://github.com/APS-8ID-DYS/bluesky)
- Bluesky Training:
  - Queueserver [hints](https://github.com/BCDA-APS/bdp_controls/blob/main/qserver/README.md)
  - General [How-to, examples, tutorials, reference](https://bcda-aps.github.io/bluesky_training)
