# Bluesky Instrument for HEXM

**Caution**:  Uses the bluesky queueserver (QS).  _Every_
Python file in this directory will be executed when QS starts the RunEngine.
Don't add extra Python files to this directory.  Instead, put them in `user/` or
somewhere else.

For more information, see: 

- Queueserver [tutorial](https://blueskyproject.io/bluesky-queueserver/tutorial.html#running-re-manager-with-custom-startup-code)
- Queueserver [hints](https://github.com/BCDA-APS/bdp_controls/blob/main/qserver/README.md)
- Bluesky Training: [How-to, examples, tutorials, reference](https://bcda-aps.github.io/bluesky_training)
