"""Command line entry point for ble-hrm-server."""

from __future__ import annotations

from pathlib import Path
import sys

from fastmcp.cli.cli import app

from . import server


def main() -> None:
    """Run the bundled MCP server."""
    app(
        args=["run", str(Path(server.__file__).resolve()), *sys.argv[1:]],
        standalone_mode=False,
    )


if __name__ == "__main__":
    main()
