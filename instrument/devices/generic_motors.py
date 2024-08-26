""" 
Contains generic motor devices; classes intended to be used 
locally (in devices folder) to generate motor stacks.
"""

#fmt:off

#Note: these are classes, not objects
__all__ = [
    "Generic5DOFDevice",
    "Generic6DOFDevice",
    "Generic7DOFDevice",
    "Generic8DOFDevice",
    "MPEMotor",
]

#fmt: on

import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

from ophyd import FormattedComponent, EpicsMotor, Device, Component, EpicsSignal, EpicsSignalRO

""" 
Begin generic device definitions here.
"""

class MPEMotor(EpicsMotor):
    #used in fastsweep plans
    backlash_dist = Component(EpicsSignal, ".BDST", kind = "config", auto_monitor = True)
    motor_step_size = Component(EpicsSignal, ".MRES", kind = "config")
    disable = Component(EpicsSignal, "_able.VAL", kind = "config")
    disable_readback = Component(EpicsSignalRO, "_able.RBV", kind = "omitted")
    
    #motor record PVs
    description = Component(EpicsSignal, ".DESC")
    speed_rps = Component(EpicsSignal, ".S", kind = "config")  #Rev per sec
    backup_speed_rps = Component(EpicsSignal, ".SBAK")  #Rev per sec
    max_speed_rps = Component(EpicsSignal, ".SMAX") #Rev per sec
    base_speed_rps = Component(EpicsSignal, ".SBAS")    #Rev per sec
    backup_acceleration = Component(EpicsSignal, ".BACC")
    move_fraction = Component(EpicsSignal, ".FRAC")
    home_speed_eps = Component(EpicsSignal, ".HVEL")    #EGU per sec
    motor_res_spr = Component(EpicsSignal, ".SREV") #steps per rev
    motor_res_epr = Component(EpicsSignal, ".UREV") #EGU per rev
    direction = Component(EpicsSignal, ".DIR")
    display_precision = Component(EpicsSignal, ".PREC")


class Generic5DOFDevice(Device):
    #Generic device with 5 degrees of freedom (no motion in Z)
    
    x       = FormattedComponent(MPEMotor, "{prefix}{xpv}")
    y       = FormattedComponent(MPEMotor, "{prefix}{ypv}")
    rotx    = FormattedComponent(MPEMotor, "{prefix}{rotxpv}")
    roty    = FormattedComponent(MPEMotor, "{prefix}{rotypv}")
    rotz    = FormattedComponent(MPEMotor, "{prefix}{rotzpv}")

    def __init__(self, prefix = "", *, xpv="", ypv="",rotxpv="", rotypv="", rotzpv="", **kwargs):
        self.prefix = prefix
        self.xpv = xpv
        self.ypv = ypv
        self.rotxpv = rotxpv
        self.rotypv = rotypv
        self.rotzpv = rotzpv
        super().__init__(prefix=prefix, **kwargs)

class Generic6DOFDevice(Generic5DOFDevice):
    #Generic device with 6 degrees of freedom (includes Z)
    
    z = FormattedComponent(MPEMotor, "{prefix}{zpv}")

    def __init__(self, prefix="", *,xpv="", ypv="", zpv="", rotxpv="", rotypv="", rotzpv="",**kwargs):
        self.zpv = zpv
        super().__init__(
            prefix=prefix,
            xpv=xpv, ypv=ypv, 
            rotxpv=rotxpv, rotypv=rotypv, rotzpv=rotzpv, 
            **kwargs
        )

class Generic7DOFDevice(Generic6DOFDevice):
    #Generic device with 7 degrees of freedom (includes x2)
    
    x2 = FormattedComponent(MPEMotor, "{prefix}{x2pv}")
    
    def __init__(
        self, prefix="", *,
        xpv="", ypv="", zpv="", rotxpv="", rotypv="", rotzpv="",
        x2pv="",
        **kwargs
    ):
        self.x2pv = x2pv
        super().__init__(
            prefix=prefix,
            xpv=xpv, ypv=ypv, zpv=zpv,
            rotxpv=rotxpv, rotypv=rotypv, rotzpv=rotzpv,
            **kwargs
        )
    

class Generic8DOFDevice(Generic6DOFDevice):
    #Generic device that extends to 8 degrees of freedom, adding x2 & y2.
    
    x2 = FormattedComponent(MPEMotor, "{prefix}{x2pv}")  # , kind="normal"
    y2 = FormattedComponent(MPEMotor, "{prefix}{y2pv}")

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