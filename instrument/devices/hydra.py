"""
Generates devices needed to control GE panels in hydra
configuration. 

TODO: check hydra.switch_status.get() to see if string or enum

:see: /home/1-id/s1iduser/mpe_feb24/macros_PK/hydra_2022Jan26/use_hydra_newer.mac
"""

__all__ = [
    "hydra",    #includes DTH module and switcher
    #user string sequence records
    "htrig_rad",
    "htrig_multi_det_sw",
    "htrig_multi_det_edge",
    "htrig_multi_det_pulse",
    "sseq_enable",
]

#import and set up logging
import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

#import mod components from ophyd
from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent 

#import detectors
from .ge_panels import *    #GE ADs as separate panels

#import other stuff
from bluesky import plan_stubs as bps
import time
#from .. import iconfig


# READ_TIMEOUT_S = iconfig.get("PV_READ_TIMEOUT", 10.0)  # aka CB_TIME (in SPEC)
# POLL_DELAY_S = 0.1
# PROCESS_EPICS_RECORD = 1  # tells record to process when sent to .PROC field


#Formatting for hydra below---------------------------------------------------------

class HydraSwitcher(Device):
    """
    Subclass of class `Hydra`. Adds attributes and swticher method
    for switching between GE1 (A) and GE5 (B). 
    
    Reference: `use_hydra_newer.mac`, see ``set_RJ45_to_A`` 
    and ``set_RJ45_to_B`` functions. 

    USAGE: 

    Command line, switch to config A (GE1):

        RE(hydra.switch("A"))

    In a plan, to switch to config A (GE1):

        yield from hydra.switch("A")
    """

    switch_status = Component(EpicsSignalRO, "1id:ESL4406:1:read.TINP", kind="omitted")
    switch_to_A = Component(EpicsSignal, "1id:ESL4406:1:selectA.PROC", kind="omitted", put_complete = True, trigger_value = 1)
    switch_to_B = Component(EpicsSignal, "1id:ESL4406:1:selectB.PROC", kind="omitted", put_complete = True, trigger_value = 1)

    def switch(self, choice):
        """Method to switch between configuration A or B.
        
        PARAMETERS: 
        choice *str* : 
            Choice of configuration. Must be either "A" (GE1) or "B" (GE5). 
        """
        
        #create a robust check to make sure choice is valid
        shorthand = {"A": self.config_A, "B": self.config_B}
        choose_config = shorthand.get(choice)
        #raise error if choose_config is not "A" or "B"
        if choose_config is None:
            # fmt: off
            raise ValueError(
                f"Must choose one of these: {list(shorthand.keys())}."
                f"  Received {choice!r}"
            )
            # fmt: on
       
        t0 = time.time()
    
        #If hydra is not in desired configuration, trigger proc field
        objective = f"STATUS: {choice.upper()} POSITION"
        if self.switch_status.get() != objective:
            logger.info(f"Status does not match {choice}. Executing {choose_config}.")
            yield from bps.trigger(choose_config, wait = True)

        logger.info("Switch complete. %.3f sec.", time.time() - t0)
            

class DTHModule(Device):
    """ 
    Subclass of class `Hydra`. Adds attributes and methods
    for DTH module.  
    """
    reset_logic = Component(EpicsSignal, "resetLogicBO")
    reset_trigger = Component(EpicsSignal, "resetTriggerBO")
    expected_status = Component(EpicsSignal, "statusLI")
    trigger_delay = Component(EpicsSignal, "triggerDelayLO.VAL")
    trigger_delay_step = Component(EpicsSignal, "triggerDelayStepLO.VAL")
    trigger_width = Component(EpicsSignal, "triggerWidthLO.VAL")
    trigger_width_step = Component(EpicsSignal, "triggerWidthStepLO.VAL")
    mode_mbbo = Component(EpicsSignal, "ModeMBBO")
    ge1_used_bo = Component(EpicsSignal, "GE1UsedBO")
    ge2_used_bo = Component(EpicsSignal, "GE2UsedBO")
    ge3_used_bo = Component(EpicsSignal, "GE3UsedBO")
    ge4_used_bo = Component(EpicsSignal, "GE4UsedBO")

    def initialize(self):
        """
        Method to initialize `hydra.dth` if full initiation needed.
        Sets parameters to default values, which can be changed 
        later in `hydra_support` plans.
        
        Usage: `hydra.dth.initialize()`       
        """
        #default DTH module parameters
        yield from bps.mv(
            self.reset_logic, 1, 
            self.trigger_delay, 0, 
            self.trigger_delay_step, 1, 
            self.trigger_width, 0, 
            self.trigger_width_step, 1, 
            self.mode_mbbo, "MultiDet SW"   #software-controlled trigger is default
        )
    
        #collect panels into a list for iterating through
        panels = [
            self.ge1_used_bo,
            self.ge2_used_bo, 
            self.ge3_used_bo,
            self.ge4_used_bo
        ]
    
        #setting all panels to unused in FPGA trigger transfer
        for panel in panels:
            yield from bps.mv(panel, "1")

    
    def fastsweep_config(self): 
        """Method for configuring hydra before flying in a fastsweep."""

        #clear the latches in dth module
        yield from bps.mv(self.dth.reset_trigger, 1)
    
                
class Hydra(HydraSwitcher):
    """Defines hydra class with subclasses above. 
    HydraSwticher class is used without modifications; 
    DTHModule class is added as a subclass (e.g., 
    DTHModule attributes are called with `hydra.dth` parent.)"""
    
    dth = Component(DTHModule, "dth1:DTH:")

hydra = Hydra("", name = "hydra")



#Formatting User SSeq records for hydra trigger modes below -------------------------------------------------------------

class MPE_Sseq(Device):
        """
        Subclass for making string sequence records with 
        all the fields MPE uses in hydra configuration.
        """
                
        #formatted components (require suffix)
        desired_out_link = FormattedComponent(EpicsSignal, "{prefix}.DOL{record_suffix}", kind = "config")
        out_link = FormattedComponent(EpicsSignal, "{prefix}.LNK{record_suffix}")
        delay = FormattedComponent(EpicsSignal, "{prefix}.DLY{record_suffix}", kind = "config")
        string_value = FormattedComponent(EpicsSignal, "{prefix}.STR{record_suffix}", string = True, kind = "config")
        numeric_value = FormattedComponent(EpicsSignal, "{prefix}.DO{record_suffix}", kind = "hinted")
        wait_completion = FormattedComponent(EpicsSignal, "{prefix}.WAIT{record_suffix}", kind = "config")

       
        def __init__(
            self, 
            prefix = "",
            *,
            record_suffix = "",
            **kwargs
        ):
            """Housekeeping."""
            self.record_suffix = record_suffix
            super().__init__(prefix = prefix, **kwargs)
            
        def reset(self):
            """Reset Sseq records to default values (clear
            out current values)."""
            
            yield from bps.mv(
                self.desired_out_link, "",
                self.out_link, "",
                self.delay, 0.0,
                self.string_value, "", 
                self.numeric_value, "",
                self.wait_completion, "NoWait"
            )
                
            
class htrigUSTRSEQ(Device):
    """General template and methods for the string sequences.
    Customized for MPE group instead of using apstools.synApps device.
    
    Calls MPE_Sseq subclass for each record step (10 total)."""
    
    #regular class components
    abort = Component(EpicsSignal, ".ABORT", kind = "omitted")
    scan = Component(EpicsSignal, ".SCAN")
    precision = Component(EpicsSignal, ".PREC", kind = "config")
    forward_link = Component(EpicsSignal, ".FLNK")
    switch_trigger = Component(EpicsSignal, ".PROC", kind="omitted", put_complete = True, trigger_value = 1)
    
    #subclass components (require suffix)
    ss1 = Component(MPE_Sseq, "", record_suffix = "1")
    ss2 = Component(MPE_Sseq, "", record_suffix = "2")
    ss3 = Component(MPE_Sseq, "", record_suffix = "3")    
    ss4 = Component(MPE_Sseq, "", record_suffix = "4")
    ss5 = Component(MPE_Sseq, "", record_suffix = "5")
    ss6 = Component(MPE_Sseq, "", record_suffix = "6")
    ss7 = Component(MPE_Sseq, "", record_suffix = "7")
    ss8 = Component(MPE_Sseq, "", record_suffix = "8")
    ss9 = Component(MPE_Sseq, "", record_suffix = "9")
    ssA = Component(MPE_Sseq, "", record_suffix = "A")
    
    def abort(self):
        """
        Method to push the abort button without timeout.
        Forces abort if necessary.
        
        Usage: USTRSEQ.abort()
        """
        self.abort.put(1, use_complete =False, force = True)
    
    def reset_all_records(self):
        """Method for clearing out all records (1-10).  
        Not the most elegant."""
        
        records = [self.ss1, self.ss2, self.ss3, self.ss4, self.ss5,
                   self.ss6, self.ss7, self.ss8, self.ss9, self.ssA]
        for record in records:
            yield from record.reset()
    
#user seq record objects
htrig_rad = htrigUSTRSEQ("1id:userStringSeq1", name = "htrig_rad")
htrig_multi_det_sw = htrigUSTRSEQ("1id:userStringSeq2", name = "htrig_multi_det_sw")
htrig_multi_det_edge = htrigUSTRSEQ("1id:userStringSeq3", name = "htrig_multi_det_edge")
htrig_multi_det_pulse = htrigUSTRSEQ("1id:userStringSeq4", name = "htrig_multi_det_pulse")  

#extra signal for enabling Sseqs
sseq_enable = EpicsSignal("1id:userStringSeqEnable", name="sseq_enable", string=True)

