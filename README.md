# ble-hrm-server
A MCP server, which serve as a BLE heart rate monitoring to connect with a HRM device.

# MCP Definition

## Resources

Bluetooth HRM is based on Bluetooth protocol, we should use `bleak` to discover the device and connect to it.

- Discover Bluetooth Device & Filter by HRM profile (Heart Rate Service 0x180D)
- resource: `discover://hrm`

## Tools

- **Tool: Monitoring Heart Rate `monitoring_heart_rate`**

  - Summary: Start monitoring the heart rate of the device for the given duration, default duration is 30 minutes (1800 sec). The monitoring will be done in the background.
  - Inputs:
    - device_id: str, the device UUID to monitor
    - duration: int, the duration to monitor, default is 1800 seconds (30 minutes)
  - Outputs: None


- **Tool: Get Heart Rate `get_heart_rate`**
  - Summary: Get the current HR, use last 10 sec and return the average of HR
  - Inputs: None (assumes baseline reading)
  - Output: Current HR (int), e.g. `{"avg_hr": 60}`


- **Tool: Evaluate Active Heart Rate `evaluate_active_heart_rate`**

  - Summary: Evaluate the maximum heart of the last 60 seconds, the observed maximum during this exercise is recorded as the active heart rate. 
  - Inputs: None (assumes baseline reading)
  - Outputs: Max HR: int, e.g. `{"max_hr": 100}`

- **Tool: Get Heart Rate Bucket `get_heart_rate_bucket`**
  - Summary: Get the heart rate bucket of the last 10 seconds, the bucket size is 1 second.
  - Inputs:
    - since_from: float, the start time of the monitoring, default is 10 seconds ago
    - bucket_size: float, the size of the bucket, default is 1 second
  - Outputs: Heart Rate Bucket: list[dict], e.g. `[{"time": 1715904000, "value": 60}, {"time": 1715904001, "value": 61}]`

- **Tool: Build Heart Rate Chart `build_heart_rate_chart`**
  - Summary: Build the heart rate chart of the last 600 seconds, the bucket is a dynamic size, the default size is 1 second. The max bucket count is 60, if the bucket count is more than 60, the bucket size will be increased to `duration / 60` seconds.
  - Inputs:
    - since_from: float, the start time of the monitoring, default is 600 seconds ago
  - Outputs: Heart Rate Chart PNG URL: str, e.g. `https://example.com/chart.png`