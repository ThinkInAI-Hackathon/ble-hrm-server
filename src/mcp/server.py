from fastmcp import FastMCP, FunctionResource

from mcp.bt_client import BtClient

mcp = FastMCP(
    name="Bluetooth HRM MCP Server",
    instructions="""MCP server for Bluetooth Heart Rate Monitor. Provides tools and resources for HRM data, evaluation, and statistics results.
""",
)


cli = BtClient()

mcp.add_resource(FunctionResource(
    uri="discover://hrm", name="HRM Device", text="Bluetooth Heart Rate Monitor Devices", fn=cli.list_bluetooth_devices))
# mcp_instance.add_resource_fn(self.get_device, uri="bt://{device_id}")

mcp.add_tool(cli.list_bluetooth_devices)
mcp.add_tool(cli.monitoring_heart_rate)
mcp.add_tool(cli.get_heart_rate)
mcp.add_tool(cli.evaluate_active_heart_rate)
mcp.add_tool(cli.get_heart_rate_bucket)
mcp.add_tool(cli.build_heart_rate_chart)

# mcp.add_tool(cli.evaluate_heart_health_status)