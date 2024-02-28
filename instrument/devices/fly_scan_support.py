"""
Support for fly scans (fly_scan_support).

SPEC macros here::

    /home/1-id/s1iduser/mpe_feb24/macros_PK/fastsweep_2018Jan22

SPEC macro PV (in ``osc_fastsweep_FPGA_hydra.mac``) for fly scanning::

    #PSOPV="1ide:PSOFly1:" # for aero
    #PSOPV="1idrams1:PSOFly1:" # for ramsrot RAMS1
    if (fs_type=="aero") PSOPV="1ide:PSOFly1:"  # For aero, Ensemble
    if (fs_type=="rams1") PSOPV="1idrams1:PSOFly1:" # For ramsrot, RAMS1 with AeroTech dual loop
    if (fs_type=="rams3") PSOPV="1idrams3:PSOFly1:" # For ramsrot, RAMS3 with A32000 single loop
    PSOPV="1ide:PSOFly1:"

"""

__all__ = """
    aero_fly
""".split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal

from bluesky import plan_stubs as bps


class TaxiFlyDevice(Device):
    """
    Connect with EPICS fly scan support.
    """

    # busy records
    fly = Component(EpicsSignal, "fly", kind="omitted")
    taxi = Component(EpicsSignal, "taxi", kind="omitted")

    # configurations
    pulse_type = Component(EpicsSignal, "pulseType", kind="config")
    start_pos = Component(EpicsSignal, "startPos", kind="config")
    send_pos = Component(EpicsSignal, "sendPos", kind="config")
    slew_speed = Component(EpicsSignal, "slewSpeed", kind="config")
    scan_delta = Component(EpicsSignal, "scanDelta", kind="config")
    
    # record processing
    init_pso = Component(EpicsSignal, "initPSO.PROC", kind="omitted")

# from 'arm_aero' macro:
#         epics_put(sprintf("%spulseType",PSOPV), "Gate", CB_TIME)
#         epics_put(sprintf("%sstartPos",PSOPV), $2, CB_TIME)
#         epics_put(sprintf("%sendPos",PSOPV), $3, CB_TIME)
#         epics_put(sprintf("%sslewSpeed",PSOPV), OSC["speed_equ_per_sec"], CB_TIME)
#         epics_put(sprintf("%sscanDelta",PSOPV), fabs(($3)-($2))/OSC["nframes"], CB_TIME)
#         epics_put(sprintf("%sdetSetupTime",PSOPV), OSC["gap_time"], CB_TIME) # gap time in sec
#         #epics_put(sprintf("%sinitPSO.PROC",PSOPV), 1) # not existing any more
#         epics_put(sprintf("%staxi",PSOPV), "Taxi", 400.0)  # This will wait (PSOFlyScan) while the taxi is finished, or time out after 400 sec
#         while (epics_get(sprintf("%staxi",PSOPV)) !="Done") {
# #        p epics_get(sprintf("%staxi",PSOPV))
#                     epics_put(sprintf("%sfly",PSOPV), "Fly") # No callback on this button
#             while (epics_get(sprintf("%sfly",PSOPV)) != "Done") {
#         epics_put(sprintf("%sfly",PSOPV), "Done")
#     epics_put(sprintf("%s.INPA", FakeGATEPV), sprintf("%sfly CP NMS", PSOPV)); # Input PV for status of Fly

    def scan(self, *args, **kwargs):
        """Perform a fly scan as directed by the EPICS FPGA support."""
        yield from bps.null()  # TODO
        raise NotImplementedError("This work is incomplete.")


aero_fly = TaxiFlyDevice("1ide:PSOFly1:", name="aero_fly")
