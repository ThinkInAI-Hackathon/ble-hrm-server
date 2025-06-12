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
uv run src/hcm/server.py
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

# Code Coverage

| Name                    |    Stmts |     Miss |   Cover |
|------------------------ | -------: | -------: | ------: |
| src/hrm/\_\_init\_\_.py |        0 |        0 |    100% |
| src/hrm/bt\_client.py   |      139 |        5 |     96% |
| src/hrm/ts\_db.py       |       41 |        1 |     98% |
|               **TOTAL** |  **180** |    **6** | **97%** |

## Sponsor
Special thanks for Qiniu Cloud for providing the storage service. Qiniu also provides LLM inference services.

[<svg width="78px" height="22px" viewBox="0 0 78 22" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" class="navbar-logo"><defs><polygon id="Fg0w3r5QIV__path-1" points="0 0 30.5205 0 30.5205 20.33 0 20.33"></polygon></defs><g id="Fg0w3r5QIV__\u9996\u9875" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd"><g id="Fg0w3r5QIV__\u5207\u56FE" transform="translate(-96.000000, -54.000000)"><g id="Fg0w3r5QIV__\u7F16\u7EC4" transform="translate(96.000000, 54.000000)"><g transform="translate(0.000000, 0.080025)"><mask id="Fg0w3r5QIV__mask-2" fill="white"><use xlink:href="#Fg0w3r5QIV__path-1"></use></mask><g id="Fg0w3r5QIV__Clip-2"></g><path d="M30.520525,0.2356 C30.006775,0.05935 29.581775,0.2741 29.338025,0.45735 C25.957025,4.4536 20.905275,6.99135 15.260275,6.99135 C13.320775,6.99135 11.451275,6.69185 9.695525,6.13635 C9.238275,4.4771 8.915025,3.2991 8.915025,3.2991 C8.915025,3.2991 8.535275,2.1431 7.250025,2.34135 L7.619525,5.3361 C5.127025,4.19885 2.931025,2.5236 1.182525,0.45685 C0.938525,0.2741 0.513775,0.05935 2.5e-05,0.2356 C1.460525,4.14235 4.378775,7.3366 8.092025,9.16035 L9.104775,17.36185 C9.104775,17.36185 9.557525,20.5001 12.502025,20.5001 L18.800025,20.5001 C21.744525,20.5001 22.197275,17.36185 22.197275,17.36185 L22.909025,11.48435 C20.996775,11.3286 19.794275,12.6611 19.412775,13.9761 C18.772525,16.19035 18.773275,16.33185 18.647025,16.7181 C18.388525,17.50885 17.540275,17.6031 17.540275,17.6031 L13.762025,17.6031 C13.762025,17.6031 12.913275,17.50885 12.654775,16.7181 C12.488275,16.20885 11.656775,13.22985 10.819775,10.2076 C12.231525,10.60685 13.721025,10.8211 15.260275,10.8211 C22.249525,10.8211 28.209025,6.41835 30.520525,0.2356" id="Fg0w3r5QIV__Fill-1" fill="#00A6E0" mask="url(#Fg0w3r5QIV__mask-2)"></path></g><path d="M77.834725,12.6241 L77.834725,10.4211 L64.111225,10.4211 L64.111225,12.6241 L66.636475,12.6241 L64.683725,17.53235 L64.649975,17.53235 L64.649975,19.73535 L76.392975,19.73535 C77.130225,19.6816 77.792725,19.02635 77.792725,18.3471 C77.792725,18.0091 77.683975,17.62385 77.661475,17.54685 L77.662975,17.54685 L76.668975,14.80935 L74.238475,14.80935 L75.226975,17.53235 L67.066725,17.53235 L69.019225,12.6241 L77.834725,12.6241 Z M56.461225,9.3241 L61.354225,9.3241 L61.354225,7.17335 L56.461225,7.17335 L56.461225,4.99385 L54.258225,4.99385 L54.258225,7.17335 L50.874225,7.17335 L51.156725,5.5576 L48.853975,5.5576 L47.677475,12.28685 L48.613725,12.28685 C48.925475,12.2556 49.972725,12.0576 50.237975,10.8106 L50.497975,9.3241 L54.258225,9.3241 L54.258225,15.8871 L47.688725,15.8871 L47.688725,18.0901 L54.258225,18.0901 L54.258225,20.25685 L56.461225,20.25685 L56.461225,18.0901 L61.909975,18.0901 L61.909975,15.8871 L56.461225,15.8871 L56.461225,9.3241 Z M35.712475,5.0171 L33.509475,5.0171 L33.509475,7.1641 L31.321225,7.1641 L31.321225,9.3846 L33.509475,9.3846 L33.509475,18.3506 C33.571725,19.0916 34.165475,19.6801 34.907975,19.73535 L43.561225,19.7351 C44.338475,19.7006 44.963975,19.0816 45.008475,18.3071 L45.008475,14.8016 L42.809475,14.8016 L42.809475,17.4801 L35.712475,17.4801 L35.712475,9.3846 L45.538725,9.3846 L45.538725,7.1641 L35.712475,7.1641 L35.712475,5.0171 Z M64.683725,7.68135 L77.236225,7.68135 L77.236225,5.53035 L64.683725,5.53035 L64.683725,7.68135 Z" id="Fg0w3r5QIV__Fill-3" fill="#00A6E0"></path></g></g></g></svg>](https://www.qiniu.com)