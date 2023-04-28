# instrument building

The MPE group wants to build an instrument (for measurement) in a dynamic
way.  The combination of stages, detectors, etc. may change as often as
every few hours.  The method to configure the instrument should be easy
to understand and change as well a documented in the data stream and/or
logs, such that analysis can proceed.

An additional consideration is that certain controls, such as sample Y,
need to be reassigned depending on the circumstances.  Sometimes, there
may be more than one sample Y available and the assignment in the data
stream must be clear which one to consider.

a. user name is s1idtest

b. workstations

- syrah (windows - inside firewall) also running the PG5 (pointgrey detector) ioc.
- kurtag (linux - inside firewall)

c. the instrument to first deploy PyEpics / Bluesky at 1-ID

1-ID-C tomo instrument (copy 6-ID-D setup to 1-ID-C)

- This consists of the following stages:
  - tomoXC 1idc:m81
  - RotXC 1idc:m15
  - omeC 1idc:m9
  - samXC 1idc:m12
  - samZC 1idc:m13
  - samYC 1idc:m81
  - etaC 1idc:m10

- Leaving the slits, conical slits, and Dexela motions out with the
  understanding that we will add those as we develop multiple instruments
  and instrument switching routines.
- Detector is PointGrey (PG5) IOC / AreaDetector running on syrah
