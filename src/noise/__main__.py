from .gui.app import NoiseMeterApp
import sys
import logging

logging.info(sys.argv)

if len(sys.argv) < 2:
    NoiseMeterApp().run()
else:
    from .cli import cli
    cli()
