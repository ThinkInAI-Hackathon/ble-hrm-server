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
        text="Bluetooth Heart Rate Monitor Devices",
        fn=cli.list_bluetooth_devices,
    )
)

mcp.add_tool(cli.list_bluetooth_devices)
mcp.add_tool(cli.monitoring_heart_rate)
mcp.add_tool(cli.get_heart_rate)
mcp.add_tool(cli.evaluate_active_heart_rate)
mcp.add_tool(cli.get_heart_rate_bucket)
mcp.add_tool(cli.build_heart_rate_chart)
