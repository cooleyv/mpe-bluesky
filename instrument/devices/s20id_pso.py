"""Device for HT-HEDM PSO controller at 20-ID-D. 
See `/home/beams/S20HEDM/spec/macros/std/ensemble_fly.mac` for 
spec macro version.

PSO classes and objects are copied from 1-ID setup in 1-ID-E, 7/02/2024.

TODO: Find some way to version control both PSOs at the same time.
FIXME: add correct IOC prefix for the pso controller for 20ID. """

__all__ = [
    "s20_psofly",
]

#import for logging 
import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#import mod components from ophyd
from ophyd import DeviceStatus
from ophyd import Component
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import Device
from ophyd import Signal

#import other stuff
from bluesky import plan_stubs as bps
import time
from apstools.synApps import BusyRecord

class MyBusyRecord(BusyRecord):
    timeout = Component(Signal, value=10, kind="config")

    def trigger(self):
        """
        Start this busy record and return status to monitor completion.

        This method is called from 'bps.trigger(busy, wait=True)'.
        """
        status = DeviceStatus(self, timeout=self.timeout.get())

        def watch_state(old_value, value, **kwargs):
            if old_value in (1, "Busy") and value not in (1, "Busy"):
                # When busy finishes, state changes from 1 to 0.
                status.set_finished()
                self.state.clear_sub(watch_state)

        # Push the Busy button...
        self.state.put(1)  # use number instead of "Taxi" text or "Fly" text.
        # Start a CA monitor on self.state, call watch_state() with updates.
        self.state.subscribe(watch_state)

        # And return the DeviceStatus object.
        # The caller can use it to tell when the action is complete.
        return status

class PSOTaxiFlyDevice(Device):
    """PSO taxi & fly device."""
    
    taxi = Component(MyBusyRecord, "taxi", kind="omitted")
    fly = Component(MyBusyRecord, "fly", kind="omitted")
    
    #(spec macro vars are commented after)
    start_position = Component(EpicsSignal, "startPos", kind="config")  #start_
    end_position = Component(EpicsSignal, "endPos", kind="config")  #end_
    slew_speed = Component(EpicsSignal, "slewSpeed", kind="config") #_speed
    scan_delta = Component(EpicsSignal, "scanDelta", kind="config") #step_
    delta_time = Component(EpicsSignalRO, "deltaTime", kind="config")   #not used
    pulse_type = Component(EpicsSignal, "pulseType", kind="config") #_pls_type
    detector_setup_time = Component(EpicsSignal, "detSetupTime", kind="config") #_det_setup
    scan_control = Component(EpicsSignal, "scanControl", kind="config") #_scan_control 

    def taxi_fly_plan(self):
        yield from bps.trigger(self.taxi, wait=True)
        yield from bps.trigger(self.fly, wait=True)

    def configure(
            self,
            pulse_type,
            start_pos,
            end_pos, 
            scan_speed_dps, 
            scan_delta, 
            gap_time
    ):
        """Method for configuring PSO device at beginning of flyscan. 
        Populates fields in MEDM window automatically."""

        yield from bps.mv(
            self.pulse_type, pulse_type,
            self.start_position, start_pos,
            self.end_position, end_pos,
            self.slew_speed, scan_speed_dps,
            self.scan_delta, scan_delta,
            self.detector_setup_time, gap_time
        )


s20_psofly = PSOTaxiFlyDevice("s20id:PSOFly1:", name="s20_psofly")




