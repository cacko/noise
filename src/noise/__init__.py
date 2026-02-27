__name__ = "noise"
__version__ = "0.0.1"

import corelog
import os

log_level = os.environ.get("NOISE_LOG_LEVEL", "ERROR")

corelog.register(
    log_level=log_level, handler_type=corelog.Handlers.RICH
)
