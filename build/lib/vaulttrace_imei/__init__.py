from .cli import decode_imei
from .tac_lookup import basic_tac_profile
from .carrier_ranges import infer_carrier

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

__all__ = ["decode_imei", "basic_tac_profile", "infer_carrier", "__version__"]

def main():
    """Entry point for `python -m imei_tool` execution."""
    from .cli import main as cli_main
    cli_main()
