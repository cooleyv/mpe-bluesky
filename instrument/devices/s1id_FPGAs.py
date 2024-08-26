""" 
Consolidating FPGA channels into devices for fly scan support. 
Some devices not directly FPGA, but needed to support fly scan operations.
"""

#fmt:off

__all__ = [
    "psofly1",
    "fake_gate",
    "time_counter",
    "det_ready",
    "hem_info", #technically not an FPGA?
    "softglue",
    "softglue2",
    "softglue3",
    "softglue4",
    "softglue4_menu",
    "det_status_monitor",   #not an FPGA?
    "scaler_trigger",
    "sample_monitor_array",
    "sample_transmission_array",
    "energy_monitor_array",
    "intensity_transmission_array",
    "integrated_time_array",
    "timestamp_array",
    "frame_counter",
    "det_pulse_to_ad",
    "struck",
]

#fmt: on

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
    start_position = Component(EpicsSignal, "startPos", kind="config")
    end_position = Component(EpicsSignal, "endPos", kind="config")
    slew_speed = Component(EpicsSignal, "slewSpeed", kind="config")
    scan_delta = Component(EpicsSignal, "scanDelta", kind="config")
    delta_time = Component(EpicsSignalRO, "deltaTime", kind="config")
    pulse_type = Component(EpicsSignal, "pulseType", kind="config")
    detector_setup_time = Component(EpicsSignal, "detSetupTime", kind="config")
    scan_control = Component(EpicsSignal, "scanControl", kind="config")

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


psofly1 = PSOTaxiFlyDevice("1ide:PSOFly1:", name="psofly1")




class FakeGate(Device):
    description = Component(EpicsSignal, ".DESC")
    scan = Component(EpicsSignal, ".SCAN")
    initial_val = Component(EpicsSignal, ".A")
    initial_val_disable = Component(EpicsSignal, ".B")
    input_flyer = Component(EpicsSignal, ".INPA")   #alternate name: input_a
    output_execute_delay = Component(EpicsSignal, ".ODLY")
    output_execute_option = Component(EpicsSignal, ".OOPT")
    output_data_option = Component(EpicsSignal, ".DOPT")
    calculation_record = Component(EpicsSignal, ".CALC")
    output_link = Component(EpicsSignal, ".OUT")
 

fake_gate = FakeGate("1ide:userCalcOut4", name = "fake_gate")

class IntTimeCounter(Device):
    ticks = Component(EpicsSignal, "1ide:userArrayCalc6")
    #name = Component(EpicsSignal, "_calc1.VAL")    #don't know PV
    det_pulse = Component(EpicsSignal, "1id:9440:1:bi_0")
    readout_desc = Component(EpicsSignal, "1id:9440:1:bi_1.DESC")
    readout_scan = Component(EpicsSignal, "1id:9440:1:bi_1.SCAN")

time_counter = IntTimeCounter("", name = "time_counter")

class DetReady(Device):
    mode = Component(EpicsSignal, "FI8_Signal")
    clock = Component(EpicsSignal, "DFF-2_CLOCK_Signal")
    set_signal = Component(EpicsSignal, "DFF-2_SET_Signal")
    data = Component(EpicsSignal, "DFF-2_D_Signal")
    clear = Component(EpicsSignal, "DFF-2_CLEAR_Signal")

det_ready = DetReady("1id:softGlue:", name = "det_ready")

class HEMInfo(Device):
    energy_keV = Component(EpicsSignal, "1id:userTran3.A")

hem_info = HEMInfo("", name = "hem_info")

class SoftGlue(Device):
    frame_readback = Component(EpicsSignal, "UpCntr-4_CLOCK_Signal")
    fs1_control = Component(EpicsSignal, "AND-1_IN1_Signal")
    #fs2 = Component(EpicsSignal, "AND-2")
    fs1_mask = Component(EpicsSignal, "AND-1_IN2_Signal")
    fs2_mask = Component(EpicsSignal, "AND-2_IN2_Signal")
    
    #Need input and output signal ports??
    port_1_in  = Component(EpicsSignal, "FI1_Signal")
    port_2_in = Component(EpicsSignal, "FI2_Signal")
    port_3_in = Component(EpicsSignal, "FI3_Signal")
    port_8_in = Component(EpicsSignal, "FI8_Signal")

    port_17_out = Component(EpicsSignal, "FO17_Signal")
    port_19_out = Component(EpicsSignal, "FO19_Signal")

    gate = Component(EpicsSignal, "FI1_BI")
    clear_dth_ready = Component(EpicsSignal, "clear_DTHDetRedy_FPGA")

softglue = SoftGlue("1id:softGlue:", name = "softglue")

class SoftGlue3(Device): 
    #TODO: Add all input and output ports to clear?
    port_5_in = Component(EpicsSignal, "FI5_Signal")
    port_25_in = Component(EpicsSignal, "FI25_Signal")
    port_17_in = Component(EpicsSignal, "FI17_Signal")
    port_8_in = Component(EpicsSignal, "FI8_Signal")

    port_17_out = Component(EpicsSignal, "FO17_Signal")
    port_18_out = Component(EpicsSignal, "FO18_Signal")
    port_19_out = Component(EpicsSignal, "FO19_Signal")
    port_20_out = Component(EpicsSignal, "FO20_Signal")


softglue3 = SoftGlue3("1id:softGlue3:", name = "softglue3")

class SoftGlue2(Device):
    #TODO: add the rest of the input/output ports?
    port_25_in = Component(EpicsSignal, "FI25_Signal")
    port_26_in = Component(EpicsSignal, "FI26_Signal")
    port_1_in = Component(EpicsSignal, "FI1_Signal")
    port_2_in = Component(EpicsSignal, "FI2_Signal")
    port_11_out = Component(EpicsSignal, "FO11_Signal")
    port_14_out = Component(EpicsSignal, "FO14_Signal")

softglue2 = SoftGlue2("1ide:sg2:", name = "softglue2")

class DetStatusMonitor(Device):
    description = Component(EpicsSignal, ".DESC")
    value = Component(EpicsSignal, ".A")

det_status_monitor = DetStatusMonitor("1ide1:userCalc5", name = "det_status_monitor")


class SoftGlue4(Device):

    #components from 1ide:sg4
    pso_pulses = Component(EpicsSignal, "1ide:sg4:AND-1_IN2_Signal")
    clear_gate = Component(EpicsSignal, "1ide:sg4:BUFFER-1_IN_Signal.PROC", kind = "omitted", put_complete = True, trigger_value =1)
    in_22Do = Component(EpicsSignal, "1ide:sg4:In_22Do.OUT")
    in_21IntEdge = Component(EpicsSignal, "1ide:sg4:In_21IntEdge")
    in_22IntEdge = Component(EpicsSignal, "1ide:sg4:In_22IntEdge")

    #components from 1id:softGlue4
    in_17IntEdge = Component(EpicsSignal, "1id:softGlue4:In_17IntEdge") #FIXME: is this the right parent?
    in_18IntEdge = Component(EpicsSignal, "1id:softGlue4:In_18IntEdge")
    advance_delay = Component(EpicsSignal, "1id:softGlue4:DnCntr-4_PRESET}")    #delay between gate and channel advance in 8 MHz ticks
    load_signal = Component(EpicsSignal, "1id:softGlue4:DnCntr-4_LOAD_Signal.PROC", kind = "omitted", put_complete = True, trigger_value = 1)
    signal_selector = Component(EpicsSignal, "1id:softGlue4:DivByN-1_N") #every nth signal from GE triggers a follower AD frame
    reset_signal_selector = Component(EpicsSignal, "1id:softGlue4:DivByN-1_RESET_Signal.PROC", kind = "omitted", put_complete = True, trigger_value = 1)
    enable_signal_selector = Component(EpicsSignal, "1id:softGlue4:DivByN-1_ENABLE_Signal")
    clock_signal_selector = Component(EpicsSignal, "1id:softGlue4:DivByN-1_CLOCK_Signal")
    clear_signal = Component(EpicsSignal, "1id:softGlue4:DFF-1_CLEAR_Signal.PROC", kind = "omitted", put_complete = True, trigger_value = 1)

    def saxs_waxs_config(self):
        """Method for configuring self for using SAXS + WAXS (hydra)."""
        
        #arming 
        yield from bps.mv(self.advance_delay, 2)
        yield from bps.trigger(self.load_signal, wait = True)

        yield from bps.mv(self.signal_selector, 1)
        yield from bps.trigger(self.reset_signal_selector, wait = True)

        yield from bps.mv(
            self.enable_signal_selector, "gate",
            self.clock_signal_selector, "det_pulse",
            self.clear_signal, 1
        )



softglue4 = SoftGlue4("", name = "softglue4")

class SoftGLue4Menu(Device):
    curr_name = Component(EpicsSignal, "currName")
    status = Component(EpicsSignal, "status")
    name1 = Component(EpicsSignal, "name1")
    load_config1 = Component(EpicsSignal, "leadConfig1.PROC", kind = "omitted", put_complete = True, trigger_value = 1)

    def saxs_waxs_config(self):
        """Method for loading in softglue configuration for SAXS + WAXS (hydra)."""

        #conditional to run this if not set
        if self.curr_name != "SAXS_WAXS":

            #first, clear settings
            yield from bps.mv(self.name1, "clear")
            yield from bps.trigger(self.load_config1, wait = True)

            #then load saxs + waxs settings
            yield from bps.mv(self.name1, "SAXS_WAXS")
            yield from bps.trigger(self.load_config1, wait = True)

            print(f"SoftGlue configuration {self.curr_name} loaded successfully.")

        else: 
            print(f"SoftGlue configuration {self.curr_name} already loaded.")


softglue4_menu = SoftGLue4Menu("1ide:SG4Menu:", name = "softglue4_menu")

class ScalerTrigger(Device):
    description = Component(EpicsSignal, ".DESC")
    scan = Component(EpicsSignal, ".SCAN")
    a_value = Component(EpicsSignal, ".A")
    b_value = Component(EpicsSignal, ".B")
    in_link_a = Component(EpicsSignal, ".INPA")
    out_execute_option = Component(EpicsSignal, ".OOPT")
    out_data_option = Component(EpicsSignal, ".DOPT")
    calc_record = Component(EpicsSignal, ".CALC")
    out_calc = Component(EpicsSignal, ".OCAL")
    out_link = Component(EpicsSignal, ".OUT")
    
scaler_trigger = ScalerTrigger("1ide:userCalcOut2", name = "scaler_trigger")


class GenericArrayCalc(Device):
    """Generic device to correct array calc fields."""

    description = Component(EpicsSignal, ".DESC")
    number_used = Component(EpicsSignal, ".NUSE")
    scan = Component(EpicsSignal, ".SCAN")
    in_link_a = Component(EpicsSignal, ".INPA")
    in_link_b = Component(EpicsSignal, ".INPB")
    in_link_c = Component(EpicsSignal, ".INPC")
    c_value = Component(EpicsSignal, ".C")
    in_link_aa = Component(EpicsSignal, ".INAA")
    in_link_bb = Component(EpicsSignal, ".INBB")
    bb_value = Component(EpicsSignal, ".BB")
    calc_record = Component(EpicsSignal, ".CALC")
    out_execute_delay = Component(EpicsSignal, ".ODLY")
    event_to_issue = Component(EpicsSignal, ".OEVT")
    out_execute_option = Component(EpicsSignal, ".OOPT")
    out_data_option = Component(EpicsSignal, ".DOPT")
    out_link = Component(EpicsSignal, ".OUT")
    wait = Component(EpicsSignal, ".WAIT")


sample_monitor_array = GenericArrayCalc("1ide:userArrayCalc1", name = "sample_monitor_array")
sample_transmission_array = GenericArrayCalc("1ide:userArrayCalc2", name = "sample_transmission_array")
energy_monitor_array = GenericArrayCalc("1ide:userArrayCalc3", name = "energy_monitor_array")
intensity_transmission_array = GenericArrayCalc("1ide:userArrayCalc4", name = "intensity_transmission_array")
integrated_time_array = GenericArrayCalc("1ide:userArrayCalc6", name = "integrated_time_array")

class TimestampArrayCalc(GenericArrayCalc):
    """Modifying the generic device to add some fields for the timestamp array PV."""
    
    a_value = Component(EpicsSignal, ".A")
    b_value = Component(EpicsSignal, ".B")
    in_link_dd = Component(EpicsSignal, ".INDD")

timestamp_array = TimestampArrayCalc("1ide:userArrayCalc5", name = "timestamp_array")

class FrameCounterTran(Device):
    description = Component(EpicsSignal, ".DESC")
    scan = Component(EpicsSignal, ".SCAN")
    #input links
    in_link_a = Component(EpicsSignal, ".INPA")
    in_link_b = Component(EpicsSignal, ".INPB")
    in_link_c = Component(EpicsSignal, ".INPC")
    in_link_d = Component(EpicsSignal, ".INPD")
    in_link_e = Component(EpicsSignal, ".INPE")
    #a
    comment_a = Component(EpicsSignal, ".CMTA")
    a_value = Component(EpicsSignal, ".A")
    expression_a = Component(EpicsSignal, ".CLCA")
    #b
    comment_b = Component(EpicsSignal, ".CMTB")
    expression_b = Component(EpicsSignal, ".CLCB")
    b_value = Component(EpicsSignal, ".B")
    #c
    comment_c = Component(EpicsSignal, ".CMTC")
    expression_c = Component(EpicsSignal, ".CLCC")
    c_value = Component(EpicsSignal, ".C")
    #d
    comment_d = Component(EpicsSignal, ".CMTD")
    d_value = Component(EpicsSignal, ".D")
    expression_d = Component(EpicsSignal, ".CLCD")
    #options and outputs
    calc_option = Component(EpicsSignal, ".COPT")
    out_link_b = Component(EpicsSignal, ".OUTB")
    out_link_d = Component(EpicsSignal, ".OUTD")

frame_counter = FrameCounterTran("1id:userTran10", name = "frame_counter")


class DetPulseToAD(Device):
    b_value = Component(EpicsSignal, ".B")
    description = Component(EpicsSignal, ".DESC")
    scan = Component(EpicsSignal, ".SCAN")
    a_value = Component(EpicsSignal, ".A")
    in_link_a = Component(EpicsSignal, ".INPA")
    in_link_b = Component(EpicsSignal, ".INPA")
    c_value = Component(EpicsSignal, ".C")
    aa_value = Component(EpicsSignal, ".AA")
    bb_value = Component(EpicsSignal, ".BB")
    calc_record = Component(EpicsSignal, ".CALC")
    out_calc = Component(EpicsSignal, ".OCAL")
    out_execute_option = Component(EpicsSignal, ".OOPT")
    out_data_option = Component(EpicsSignal, ".DOPT")
    out_link = Component(EpicsSignal, ".OUT")
    wait = Component(EpicsSignal, ".WAIT")
    
det_pulse_to_ad = DetPulseToAD("1id:userStringCalc4", name = "det_pulse_to_ad")


class Struck(Device):
    channel_advance = Component(EpicsSignal, "ChannelAdvance")
    erase_start = Component(EpicsSignal, "EraseStart")

struck = Struck("1id:mcs:", name = "struck")