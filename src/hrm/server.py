from fastmcp import FastMCP
from fastmcp.resources import FunctionResource

from hrm.bt_client import BtClient

mcp = FastMCP(
    name="Bluetooth HRM MCP Server",
    instructions="""MCP server for Bluetooth Heart Rate Monitor. Provides tools and resources for HRM data, evaluation, and statistics results.
""",
)


cli = BtClient()

mcp.add_resource(
    FunctionResource(
        uri="discover://hrm",
        name="HRM Device",
        description="Bluetooth Heart Rate Monitor Devices",
        fn=cli.list_bluetooth_devices,
    )
)

# Wrap the methods as proper tools
@mcp.tool()
async def list_bluetooth_devices() -> dict[str, dict]:
    """Discover Bluetooth devices and filter by HRM profile. Returns a dic, key is the device id,
    value is a dict of device name and rssi."""
    return await cli.list_bluetooth_devices()

@mcp.tool()
async def monitoring_heart_rate(device_id: str, duration: int = 30 * 60):
    """Monitor the heart rate of the device for the given duration, default duration is 1800 seconds (30 minutes).
    The monitoring will be done in the background.

    Args:
        device_id: str, the device UUID to monitor
        duration: int, the duration to monitor, default is 1800 seconds (30 minutes)
    """
    return await cli.monitoring_heart_rate(device_id, duration)

@mcp.tool()
async def get_heart_rate() -> dict:
    """Get the current HR, use last 10 sec and return the average of HR.

    Returns:
        dict, the average of HR in the 10 seconds since start_time, e.g.
        {
            "avg_hr": int
        }
    """
    return await cli.get_heart_rate()

@mcp.tool()
def evaluate_active_heart_rate() -> dict:
    """Evaluate the active heart rate by the max heart rate of last min.

    Returns:
        dict, the max heart rate of last min, e.g.
        {
            "max_hr": int
        }
    """
    return cli.evaluate_active_heart_rate()

@mcp.tool()
def get_heart_rate_bucket(since_from: float = 10.0, bucket_size: float = 1.0) -> list[dict]:
    """Get the heart rate bucket of the given since_from time in seconds and bucket_size in seconds.

    Args:
        since_from: float, the start time of the monitoring, default 10 seconds ago
        bucket_size: float, the size of the bucket, default 1.0

    Returns:
        list[dict], the heart rate bucket, e.g.
        [
            {
                "time": float,
                "value": int,
            }
        ]
    """
    return cli.get_heart_rate_bucket(since_from, bucket_size)

@mcp.tool()
def build_heart_rate_chart(since_from: float = 600.0) -> str:
    """
    Build a heart rate plot chart using heart rate bucket data (bucket size 1s) and overlay the average heart rate line.
    Args:
        since_from: float, how many seconds ago to start (default 600s = 10min)
    Returns:
        str: The URL of the chart image (PNG)
    """
    return cli.build_heart_rate_chart(since_from)
