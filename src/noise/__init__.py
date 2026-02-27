__name__ = "noise"
__version__ = "0.0.1"

import corelog
import os


corelog.register(
    os.environ.get("NOISE_LOG_LEVEL", "INFO"), handler_type=corelog.Handlers.RICH
)
