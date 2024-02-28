"""
Support the Hydra detectors.

:see: /home/1-id/s1iduser/mpe_feb24/macros_PK/hydra_2022Jan26/use_hydra_newer.mac
"""

import logging
import time

from bluesky import plan_stubs as bps
from apstools.synApps.sseq import sseqRecordStep

logger = logging.getLogger(__name__)
logger.info(__file__)

from ..devices import ge1, ge2, ge3, ge4, ge5, fs_c, htrigUSTRSEQ, sseq_enable
from ..devices.ad_common import GE_AreaDetector

hydra_detectors = []  # which detectors to be used

# Users' preferred configurations

def hydra1():
    global hydra_detectors
    hydra_detectors = [ge1]

def hydra3():
    global hydra_detectors
    hydra_detectors = [ge1, ge2, ge3]

def hydra3_noGE2():
    global hydra_detectors
    hydra_detectors = [ge1, ge3, ge4]

def hydra4():
    global hydra_detectors
    hydra_detectors = [ge1, ge2, ge3, ge4]


def use_ge_hydra(driver: str, master: GE_AreaDetector):
    if driver not in ["old", "new"]:
        raise ValueError(
            f"Unrecognized hydra driver type: {driver!r}"
            " It must be 'old' or 'new'."
        )

    # TODO: check with team that this code does what is expected
    if driver == "old":  # GE_NEW (as said use_hydra_newer.mac, lines 134-5)
        for det in [master] + hydra_detectors:
            det.image.stage_sigs["enable"] = 1
            det.pva.stage_sigs["enable"] = 1
            det.hdf1.stage_sigs["enable"] = 0
            det.proc1.stage_sigs["enable"] = 1
            det.roi1.stage_sigs["enable"] = 1
            det.trans1.stage_sigs["enable"] = 1
    else:  # driver == "new", GE_AD (as said use_hydra_newer.mac, lines 137-8)
        for det in [master] + hydra_detectors:
            det.image.stage_sigs["enable"] = 0
            det.pva.stage_sigs["enable"] = 0
            det.hdf1.stage_sigs["enable"] = 1
            det.proc1.stage_sigs["enable"] = 0
            det.roi1.stage_sigs["enable"] = 0
            det.trans1.stage_sigs["enable"] = 0

    # TODO: What does this SPEC code accomplish?
    #     # old macro definitions
    #     rdef det_trig \'_adtrig_xtime_hydra\'
    #     rdef det_wait \'_adwait_hydra\'
    #     rdef detget_imgprefix \'detget_imgprefix_ad\'
    #     rdef detget_seqNumber \'detget_seqNumber_ad\' # with RBV value (same as _ad)
    #     rdef detabort \'hydra_abort\'
    #     rdef ccdset_Initialize  \'ccdset_Initialize_adhydra\'

    #     ### NEW TODO: define these
    #     rdef ccdset_trigmode \'set_hydra_TrigMode_par\'
    #     rdef ccdget_SeqNumber \'get_hydra_FileNumber(1)\'  # with not RBV value (same as _ad), only from the master detector
    #     rdef ccdset_seqnum \'set_hydra_FileNumber\'  # setting the values (same as _ad)

    #     rdef ccdset_time \'_adtrig_xtime_hydra\'
    #     rdef ccdset_period \'p "No period time setting for GE."\'
    #     # This should be checked later! for teh new driver vs. old driver
    #     rdef ccdset_filepath  \'set_hydra_FilePath\'

    #     _setarrayname_adhydra # This should not hurt the old driver
    #     adhydra_setup

    #     OSC["detDelay"] = 0.0  # For software mode
    #     OSC["cushion_time"] = 0.0
    #     printf("  Detector related macros are re-defined to %s in HYDRA mode, masterPV is %s\n", OSC["detector"], CCDPV)


def adhydra_setup(hydra_init_depth: str):
    """(plan) setup the Hydra detectors."""
    # to protect the detector (SEXS and MEXS signal may come out)
    yield from bps.mv(fs_c.shutter, "close")  # Cclose

    if hydra_init_depth != "fast":
        print("  TrigModChange setup...")
        t0 = time.time(); # We need this here to have the proper hCCDPV ready
        # TODO: setup_TrigModChange_Sseq
        print(f"Done. {time.time()-t0:.3f} sec.\n")

    # SPEC macro
    # def adhydra_setup '{
    #     ### Caution: No such thing here: ccdset_ImageMode("Single")
    #     local ihydra

    #     Cclose # to protect the detector (SEXS and MEXS signal may come out)

    #     # Setting to the default mode
    #     if (hydra_init_depth != "fast") {
    #         #p " ", hCCDPV
    #         printf("  TrigModChange setup..."); ttt=time(); # We need this here to have the proper hCCDPV ready
    #            setup_TrigModChange_Sseq
    #         printf("Done. %.3g sec.\n", time()-ttt)
    #     }
    #     set_hydra_TrigMode_par \"MULTI_DET\ SW\" # default: MULTI_DET SW
    #     #set_hydra_TrigMode_par \"RAD\" # default: MULTI_DET SW
    #     set_hydra_expTime 0.1 # default 0.1 sec
    #     set_hydra_NumberOfImagesPerDetTrig 1 # default: 1 frame
    #     for (ihydra=1 ; ihydra<=hydraNum; ihydra++) {
    #     	epics_put(sprintf("%sNumberOfRowsForUserSeq1", hCCDPV[ihydra]), 2048, CB_TIME) # 2048
    #     	epics_put(sprintf("%sNumberOfColumnsForUserSeq1", hCCDPV[ihydra]), 2048, CB_TIME) # 2048
    #     	epics_put(sprintf("%sArrayCallbacks", hCCDPV[ihydra]), "Disable", CB_TIME) # Disable; This is special for the hydra
    #         epics_put(sprintf("%sAutoIncrement", hADFILEPV[ihydra]),"Yes", CB_TIME)
    #         # Additonal for the new GE driver
    #         if (OSC["detector"]="GE_AD") {
    #         	epics_put(sprintf("%sEnableCallbacks", hADIMAGEPV[ihydra]), "Enable", CB_TIME) # Enable CB on image1
    #         	epics_put(sprintf("%sEnableCallbacks", hADFILEPV[ihydra]), "Enable", CB_TIME) # Enable CB on Raw1/TIFF1
    #             epics_put(sprintf("%sFileWriteMode", hADFILEPV[ihydra]), "Single", CB_TIME)
    #             epics_put(sprintf("%sAutoSave", hADFILEPV[ihydra]), "Yes", CB_TIME)

    #             epics_put(sprintf("%sFileWriteMode", hADFILEPV[ihydra]), "Stream", CB_TIME)  # Stream is the default mode
    #             epics_put(sprintf("%sNumCapture", hADFILEPV[ihydra]), 1, CB_TIME)  # This must be 1 for the initialization frame

    #             ### TODO: write these macros
    #             #flipimage_0
    #             #file_raw
    #             #notsummed
    #         }
    #     }

    #     if (OSC["detector"]="GE_AD") {
    #         # We have to initialize the file writer for Stream mode with 1 short frame. But only after the startup.
    #         # If Capture is not started, it will not save any file.
    #         ##det_trig
    #         _adtrig_xtime_hydra 0.1 1
    #         ##det_wait
    #         _adwait_hydra
    #     }

    #     sleep(EPICS_DELAY)
    #     ccdset_Initialize_adhydra

    # }' # adhydra_setup


def setup_TrigModChange_Sseq(hydra_init_depth):
    yield from bps.mv(sseq_enable, "Enable")

    # Clear the Busy state on the SSeqs, just in case
    for sseq in htrigUSTRSEQ.values():
        yield from bps.abs_set(sseq._abort, 1)

    # not needed if the sseq records have not changed
    if True:
        for mode, sseq in htrigUSTRSEQ.items():
            # initialize the sseq record
            yield from bps.mv(
                sseq.scanning_rate, "Passive",
                sseq.precision, 5,
            )
            for ch in sseq.steps.component_names:
                step = getattr(sseq.steps, ch)
                if isinstance(step, sseqRecordStep):
                    yield from bps.mv(
                        step.delay, 0.0,
                        step.input_pv, "",
                        step.numeric_value, 0.0,
                        step.output_pv, "",
                        step.string_value, "",
                        step.wait_completion, "After6" if ch <= "step5" else "NoWait"
                    )
                    # TODO:

    # def	setup_TrigModChange_Sseq '{
    #     # Usage: setup_TrigModChange_Sseq
    #     #   With option hydra_init_depth="fast" it will not reinitialize the whole record only the dynamic fields
    #     local ihydra ifield imode ii

    #     ...

    #     # TODO: This part is not really necessary if the UstrSeq records are not changed
    #     if (1) {
    #         # Initializig the userStrigSeq records
    #         for (imode=1; imode<=hmodesNum; imode++) {
    #             local hseq
    #             hseq = htrigUSTRSEQ[hmodes[imode]]
    #             ...

    #             for (ifield=1; ifield<=5; ifield++) {
    #                 epics_put(sprintf("%s.STR%d", hseq, ifield), hmodes[imode], CB_TIME) # Setting the detector modes
    #             }
    #             epics_put(sprintf("%s.STR%d", hseq, 6), sprintf("Hydra %s WAITING...", hmodes[imode] ), CB_TIME) # Setting the Caption
    #             epics_put(sprintf("%s.STRA", hseq), sprintf("Hydra %s Ready", hmodes[imode] ), CB_TIME) # Setting the Caption
    #             epics_put(sprintf("%s.FLNK", hseq), "0", CB_TIME) # Setting the Forward Link

    #         }
    #         # Setting the Output PVs, one time
    #         for (imode=1; imode<=hmodesNum; imode++) {
    #             local hseq
    #             hseq = htrigUSTRSEQ[hmodes[imode]]
    #             epics_put(sprintf("%s.LNK%d", hseq,  6), sprintf("%s.DESC NPP NMS", hseq), CB_TIME)
    #             epics_put(sprintf("%s.LNKA", hseq), sprintf("%s.DESC NPP NMS", hseq), CB_TIME)
    #         }
    #     }

    #     # Setting the Output PVs, dynamic
    #     for (imode=1; imode<=hmodesNum; imode++) {
    #         local hseq
    #         hseq = htrigUSTRSEQ[hmodes[imode]]
    #         for (ifield=1 ; ifield<=5; ifield++) {
    #             #Clears the fields
    #             epics_put(sprintf("%s.LNK%d", hseq,  ifield), "", CB_TIME)
    #         }
    #         for (ifield=1 ; ifield<=5; ifield++) {
    #             for (ihydra=1 ; ihydra<=hydraNum; ihydra++) {
    #                 if (hydra[ihydra]==ifield) {
    #                     # The output PVs: det trigger mode
    #                     epics_put(sprintf("%s.LNK%d", hseq,  ifield), sprintf("%sTriggerMode PP NMS", hCCDPV[ihydra]), CB_TIME)
    #                 }
    #             }
    #         }
    #     }
    # }'
