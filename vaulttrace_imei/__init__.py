"""
IMEI/TAC Analysis Toolkit
Offline-first IMEI decoding, TAC profiling, and carrier inference.
"""

from .cli import decode_imei, main as _cli_main
from .tac_lookup import basic_tac_profile
from .carrier_ranges import infer_carrier

__version__ = "1.0.0"
__author__ = "Your Name or Org"
__license__ = "MIT"

__all__ = (
    "decode_imei",
    "basic_tac_profile",
    "infer_carrier",
    "__version__",
)

def __getattr__(name):
    # Lazy attribute error for clean API
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def __dir__():
    return sorted(__all__)

def main():
    """Entry point for `python -m package` execution."""
    _cli_main()
