"""
Plan stubs that pertain to the storage ring (SR) and its status.
"""

all = [
    "wait_for_beam",
]

import logging
logger = logging.getLogger(__name__)
logger.info(__file__)

from ..devices.aps_source import aps 

def wait_for_beam(
    target = ['USER OPERATIONS', 'Bm Ln Studies'],
    poll_s = 300,
    warmup_time = 100
):        
    """Periodically checks if beam is back.
    
    PARAMETERS

    target "str":
        Specifies the target statuses that would indicate the beam is back. 
        Use `aps.machine_status.enum_strs` to see choices. 
        (default : ['USER OPERATRIONS', 'Bm Ln Studies']) 

    poll_s *int*:
        The sampling time in seconds that the function uses to check the beam status. (default : 300)
    
    warmup_time *int*:
        The amount of time in seconds that the function waits to warm up after finding a 
        status with beam. (default : 100)
    """
    
    if aps.machine_status.get() == 'NO BEAM':
        logger.info("Beam is down. Waiting for beam...")
        while aps.machine_status.get() not in target:
            time.sleep(poll_s)
        logger.info("Beam is back. Waiting {warmup_time} s to warm up.")
        time.sleep(warmup_time)
    else: logger.info("Beam is on. Check aps.machine_status for more information.")