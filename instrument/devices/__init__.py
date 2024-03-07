"""
local, custom Device definitions
"""

# from ophyd.log import config_ophyd_logging
# config_ophyd_logging(level="DEBUG")
#     # 'ophyd' — the logger to which all ophyd log records propagate
#     # 'ophyd.objects' — logs records from all devices and signals (that is, OphydObject subclasses)
#     # 'ophyd.control_layer' — logs requests issued to the underlying control layer (e.g. pyepics, caproto)
#     # 'ophyd.event_dispatcher' — issues regular summaries of the backlog of updates from the control layer that are being processed on background threads

from .data_management import *

# comment out for BDP demo: 2024-03-07 to 2024-03-13
#	from .ioc1ide1_motors import *
#	from .generic_motors import *
#	from .ioc1idc_motors import *
#	from .ioc1ide_scalers import *
#	from .s1id_shutters import *
#	from .s1id_slits import *
#
#	# after the above imports
#	from .hydra_detectors import *
#
#	#### other examples from the template (in bluesky_training)
#	from .aps_source import *

# from .aps_undulator import *

# from .area_detector import *
# from .calculation_records import *
# from .data_management import *
# from .fourc_diffractometer import *
# from .ioc_stats import *
# from .kohzu_monochromator import *
# from .motors import *
# from .noisy_detector import *
# from .scaler import *
# from .shutter_simulator import *
# from .simulated_fourc import *
# from .simulated_kappa import *
# from .slits import *
# from .sixc_diffractometer import *
# from .temperature_signal import *
