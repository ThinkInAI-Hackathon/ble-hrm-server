# ble-hrm-server
A MCP server, which serve as a BLE **H**eart **Rate** **M**onitoring to connect with a HRM device.

# Build Status
[![CI](https://github.com/ThinkInAI-Hackathon/ble-hrm-server/actions/workflows/ci.yml/badge.svg)](https://github.com/ThinkInAI-Hackathon/ble-hrm-server/actions/workflows/ci.yml)


# Installation

We recommend using a virtual environment and `uv` to manage dependencies.

This project uses `pyproject.toml` for dependency management.

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

# Install uv if not already installed
pip install uv

# Install dependencies
uv sync
```

# Environment Configuration

This project supports configuration via a `.env` file. You can use the provided `.env.sample` as a template.

```bash
cp .env.sample .env
```

The following environment variables are used:

- `QINIU_ACCESS_KEY`: Your Qiniu access key.
- `QINIU_SECRET_KEY`: Your Qiniu secret key.
- `QINIU_BUCKET_NAME`: The name of the Qiniu bucket.
- `QINIU_BUCKET_DOMAIN`: The domain associated with the Qiniu bucket.

# Usage

## Run the server

```bash
uv run src/hrm/server.py
```

After installing from PyPI, you can run the server directly using:

```bash
uvx ble-hrm-server
```

## Run the tests

```bash
uv run pytest
```

## Run the tests with coverage

```bash
uv run coverage run -m pytest
uv run coverage html
```

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


# MCP Settings

Here is the MCP settings for the server:

```json
{
  "mcpServers": {
    "blue-hrm": {
      "command": "uvx",
      "args": [
        "ble-hrm-server"
      ]
    }
  }
}
```

Here is a sample prompt for the LLM tested by DeepSeek V3.1:

```
你是一位健康专家，通过心率来检测测试者的心脏健康程度，现在测试者携带了蓝牙的心率带，

以下为检测步骤
- 你通过发现来获取的设备ID,通过rssi获取最接近的设备，再以此设备开始监控。
- 获取当前测试者的静息心率。
- 当测试结束后，提示测试者开始中高强度运动，比如波比跳，当测试者完成运动后，回复后，立刻测试其最高运动心率。
- 之后提示测试者计时休息2分钟，得到确认后，再次获取当前心率，并与最高心率的差额作为恢复心率。 

最后通过恢复心率的值和以下列表评估测试者的心脏健康程度，并用健康专家的口吻给测试者一些关于心脏健康方面的建议。
------
- <22: 身体年龄略大于 真实年龄
- 22～52: 身体年龄= 真实年龄 
- 53～58: 身体年龄略小于真实年龄 
- 59～65: 身体年龄比真实年龄小 
- >=66: 身体年龄比真实年龄小很多
```


# Code Coverage

| Name                    |    Stmts |     Miss |   Cover |
|------------------------ | -------: | -------: | ------: |
| src/hrm/\_\_init\_\_.py |        0 |        0 |    100% |
| src/hrm/bt\_client.py   |      139 |        5 |     96% |
| src/hrm/ts\_db.py       |       41 |        1 |     98% |
|               **TOTAL** |  **180** |    **6** | **97%** |

## Sponsor
Special thanks for Qiniu Cloud for providing the storage service. Qiniu also provides LLM inference services.

[![Qiniu Logo](docs/qiniu-logo.svg)](https://www.qiniu.com)