# notes 2024-01-23

With the idea of implementing instrument configurations from ophyd devices.

## Configuration (in YAML)

```yml
# prototype configuration
configuration: "1-ID-C:Almer2024-01"
  bds:
    undulator: undulator_us
    wbs: slitobject
    filters: filter1
    mono: kohzu
  bcs:
    lens1: lens_6dof
  sms:
  sample: sms_sample


configuration: 1-BM-B user
bds:
  # undulator: "ID1us:"
  wbs: slitobject
  filters: filter1
  mono: kohzu
bcs:
  lens1: "PV_PREFIX"
sms:
  sample: sms_sample2
  other: sms_other
```

## example ophyd code

```py

import apstools.devices
from ophyd import Component, Device, EpicsMotor, EpicsSignal, FormattedComponent

undulator_us = apstools.devices.ApsUndulator("ID01us", name="undulator_us")
undulator_ds = apstools.devices.ApsUndulator("ID01ds", name="undulator_ds")

class Generic6DOFDevice(Device):
    """
    Generic Lens device with 6 degrees of freedom.
    """
    x = FormattedComponent(EpicsMotor, "{prefix}{xpv}")
    y = FormattedComponent(EpicsMotor, "{prefix}{ypv}")
    z = FormattedComponent(EpicsMotor, "{prefix}{zpv}")
    rotx = FormattedComponent(EpicsMotor, "{prefix}{rotxpv}")
    roty = FormattedComponent(EpicsMotor, "{prefix}{rotypv}")
    rotz = FormattedComponent(EpicsMotor, "{prefix}{rotzpv}")

    def __init__(
        self, prefix="", *,
        xpv="", ypv="", zpv="", rotxpv="", rotypv="", rotzpv="",
        **kwargs
    ):
        self.prefix = prefix
        self.xpv = xpv
        self.ypv = ypv
        self.zpv = zpv
        self.rotxpv = rotxpv
        self.rotypv = rotypv
        self.rotzpv = rotzpv
        super().__init__(prefix=prefix, **kwargs)

lens_6dof = Generic6DOFDevice(
    "1idc:", name="lens_6dof",
    xpv="m1", ypv="m2", zpv="m3", rotxpv="m4", rotypv="m5", rotzpv="m6",
)


class Generic8DOFDevice(Generic6DOFDevice):
    """SMS device extends the Generic6DOFDevice with x2 & y2."""
    x2 = FormattedComponent(EpicsMotor, "{prefix}{x2pv}")  # , kind="normal"
    y2 = FormattedComponent(EpicsMotor, "{prefix}{y2pv}")

    def __init__(
        self, prefix="", *,
        xpv="", ypv="", zpv="", rotxpv="", rotypv="", rotzpv="",
        x2pv="", y2pv="",
        **kwargs
        ):
      self.x2pv = x2pv
      self.y2pv = y2pv
      super().__init__(
        prefix=prefix,
        xpv=xpv, ypv=ypv, zpv=zpv,
        rotxpv=rotxpv, rotypv=rotypv, rotzpv=rotzpv,
        **kwargs
    )

sms_sample = Generic8DOFDevice("1idc:", name="sms_sample",
    xpv="m11", ypv="m12", zpv="m13", 
    rotxpv="m14", rotypv="m15", rotzpv="m16",
    x2pv="m17", y2pv="m18",
)
# sms_other = SmsDevice("", name="sms_other", xpv="1idc:m1", ypv="33idf:m6", rotypv="aps:m72", ...)
```