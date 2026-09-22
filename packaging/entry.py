"""Entry point for the packaged Selfproof binary.

PyInstaller bundles this together with the ``selfproof`` and ``renker_core``
packages. Running the binary with no arguments opens the dashboard; any
arguments are passed through to the normal CLI.
"""

from __future__ import annotations

import sys

from selfproof.cli import main

if __name__ == "__main__":
    sys.exit(main())
