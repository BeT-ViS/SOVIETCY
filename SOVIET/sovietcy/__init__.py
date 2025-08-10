# sovietcy/__init__.py

# This file marks the `sovietcy` directory as a Python package.

# You can optionally define __all__ if you want to explicitly control
# what gets imported when someone does `from sovietcy import *`.
# For this application, direct imports of main components are usually preferred.
# For example:
# from .main import run_sovietcy
# from .network_scanner import NetworkScanner
# from .phishing_tool import PhishingTool

# __all__ = ["run_sovietcy", "NetworkScanner", "PhishingTool"]

# You can also add package-level initializations here,
# such as setting up a logger, defining package-wide constants,
# or performing checks.

# Example: Setting a package version
__version__ = "0.1.0"

# Example: Basic logging configuration for the package (optional, can be more complex)
import logging

# Ensure logs don't propagate to root logger if not explicitly handled
logging.getLogger(__name__).addHandler(logging.NullHandler())

# For debugging or specific scenarios, you might configure it like this:
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logging.info(f"Sovietcy package (version {__version__}) initialized.")

# It's generally good practice to keep __init__.py light,
# especially for applications. More complex logic typically goes into
# dedicated modules.
