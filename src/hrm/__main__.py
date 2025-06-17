"""Command line entry point for ble-hrm-server."""

from __future__ import annotations

from pathlib import Path
import sys

from fastmcp.cli.run import run_command

from . import server


def main() -> None:
    """Run the bundled MCP server."""
    run_command(str(Path(server.__file__).resolve()), server_args=sys.argv[1:])


if __name__ == "__main__":
    main()
