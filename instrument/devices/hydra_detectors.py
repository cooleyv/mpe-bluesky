"""
Construct support for the Hydra detectors.

:see: /home/1-id/s1iduser/mpe_feb24/macros_PK/hydra_2022Jan26/use_hydra_newer.mac
"""

__all__ = """
    ge1 ge2 ge3 ge4
    ge5
    htrigUSTRSEQ
    hydra_ab
    sseq_enable
    sseq_rad
    sseq_multi_det_sw
    sseq_multi_det_edge
    sseq_multi_det_pulse
""".split()
    # ge5

import logging
import time

from apstools.synApps import SseqRecord
from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO

from bluesky import plan_stubs as bps

logger = logging.getLogger(__name__)
logger.info(__file__)

from .. import iconfig
from .ad_common import GE_AreaDetector

READ_TIMEOUT_S = iconfig.get("PV_READ_TIMEOUT", 10.0)  # aka CB_TIME (in SPEC)
POLL_DELAY_S = 0.1
PROCESS_EPICS_RECORD = 1  # tells record to process when sent to .PROC field



class HydraABSelectorDevice(Device):
    """
    The switch between GE1 (A) and GE5 (B).

    SPEC:

    * ``set_RJ45_to_A``: ``hydra_ab.switch("A")``
    * ``set_RJ45_to_B``: ``hydra_ab.switch("B")``

    EXAMPLE::

        hydra_ab = HydraABSelectorDevice("1id:ESL4406:1:", name="hydra_ab")

    On the command line, to switch to GE1::

        RE(hydra_ab.switch("A"))

    In a plan, to switch to GE1::

        yield from hydra_ab.switch("A")
    """

    status = Component(EpicsSignalRO, "read.TINP", kind="omitted")
    read_asyn_A = Component(EpicsSignal, "selectA.PROC", kind="omitted")
    read_asyn_B = Component(EpicsSignal, "selectB.PROC", kind="omitted")

    def switch(self, choice):
        """Bluesky plan to switch between A or B."""
        processors = {"A": self.read_asyn_A, "B": self.read_asyn_B}
        process_asyn_record = processors.get(choice)
        if process_asyn_record is None:
            # fmt: off
            raise ValueError(
                f"Must choose one of these: {list(processors.keys())}."
                f"  Received {choice!r}"
            )
            # fmt: on

        t0 = time.time()
        # TODO: refactor in thread with status object
        objective = f"STATUS: {choice.upper()} POSITION"
        while self.status.get() != objective:
            # TODO: refactor with TQDM progress bar (comes with status object)
            # min=0, max=READ_TIMEOUT

            # tell asyn to process (means: read its input)
            yield from bps.abs_set(process_asyn_record, PROCESS_EPICS_RECORD)
            yield from bps.sleep(POLL_DELAY_S)
        logger.info("Done. %.3f sec.", time.time() - t0)


def _create_detector(prefix):
    """Create area detector object or assign it as ``None`` if timeout."""
    try:
        det = GE_AreaDetector(prefix, name=prefix.rstrip(":").lower())
        # TODO: auto warmup?
    except TimeoutError as exinfo:
        det = None
        logger.warning("Could not create GE detector %r (%s)", prefix, exinfo)
    return det


ge1 = _create_detector("GE1:")
ge2 = _create_detector("GE2:")
ge3 = _create_detector("GE3:")
ge4 = _create_detector("GE4:")
ge5 = None  # as of 2024-03-07
# ge5 = _create_detector("GE5:")

hydra_ab = HydraABSelectorDevice("1id:ESL4406:1:", name="hydra_ab")
sseq_enable = EpicsSignal("1id:userStringSeqEnable", name="sseq_enable", string=True)
sseq_rad = SseqRecord("1id:userStringSeq1", name="sseq_rad")
sseq_multi_det_sw = SseqRecord("1id:userStringSeq2", name="sseq_multi_det_sw")
sseq_multi_det_edge = SseqRecord("1id:userStringSeq3", name="sseq_multi_det_edge")
sseq_multi_det_pulse = SseqRecord("1id:userStringSeq4", name="sseq_multi_det_pulse")

# SPEC macro compatibility dictionaries
htrigUSTRSEQ = {
    "MULTI_DET SW": sseq_multi_det_sw,
    "MULTI_DET Edge": sseq_multi_det_edge,
    "MULTI_DET Pulse": sseq_multi_det_pulse,
    "RAD": sseq_rad,
}
DTHmode = {
    "MULTI_DET SW": "MultiDet SW",
    "MULTI_DET Edge": "MultiDet Edge",
    "MULTI_DET Pulse": "MultiDet Pulse",
    "RAD": "MultiDet SQ",  # Ineffective
}
