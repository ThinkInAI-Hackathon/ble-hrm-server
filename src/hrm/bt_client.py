import asyncio
import io
import logging
import math
import os
import tempfile
import time
from datetime import datetime
from typing import List, Optional

import matplotlib.pyplot as plt
from bleak import BleakClient, BleakScanner
from dotenv import load_dotenv
from qiniu import Auth as QiniuAuth
from qiniu import put_file as QiniuPutFile

from hrm.ts_db import TsDB

# Heart Rate Service UUID (16-bit: 0x180D, full 128-bit form)
HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"

# Heart Rate Measurement Characteristic UUID (16-bit: 0x2a37, full 128-bit form)
HR_MEASUREMENT_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"


# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def upload_file(file_path: str) -> Optional[str]:
    """Upload a file to QINIU Storage, it will let DeepChat to download the file."""
    load_dotenv()
    QINIU_ACCESS_KEY = os.getenv("QINIU_ACCESS_KEY")
    QINIU_SECRET_KEY = os.getenv("QINIU_SECRET_KEY")
    QINIU_BUCKET_NAME = os.getenv("QINIU_BUCKET_NAME")
    QINIU_BUCKET_DOMAIN = os.getenv("QINIU_BUCKET_DOMAIN")
    # if file_path is not a PNG file, return none
    if not file_path.endswith(".png"):
        return None

    # Check if all QINIU keys are defined
    if not all(
        [QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_NAME, QINIU_BUCKET_DOMAIN]
    ):
        logger.warning("QINIU keys are not defined. Skipping upload.")
        return None

    q = QiniuAuth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)

    key = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    token = q.upload_token(QINIU_BUCKET_NAME, key, 3600)

    ret, info = QiniuPutFile(token, key, file_path, version="v2")

    base_url = f"{QINIU_BUCKET_DOMAIN}/{key}"
    # private_url = q.private_download_url(base_url, expires=3600)
    if ret is not None:
        return base_url
    else:
        return None


class BtClient:
    def __init__(self):
        logger.info("BtClient initialized")
        # 50000 is the max length of the db
        self.db = TsDB(50000)
        self.client: Optional[BleakClient] = None

    async def list_bluetooth_devices(self) -> dict[str, dict]:
        """Discover Bluetooth devices and filter by HRM profile. Returns a dic, key is the device id,
        value is a dict of device name and rssi."""

        devices = await BleakScanner.discover(return_adv=True)
        result = {}
        for device, adv_data in devices.values():
            if HEART_RATE_SERVICE_UUID in adv_data.service_uuids:
                name = device.name or "N/A"
                logger.info(f"Device: {device.address}, {name}, {device.rssi}")
                result[device.address] = {
                    "name": name,
                    "rssi": device.rssi,
                }
        return result

    # Tool: Start Monitoring Heart Rate
    async def monitoring_heart_rate(self, device_id: str, duration: int = 30 * 60):
        """Monitor the heart rate of the device for the given duration, default duration is 1800 seconds (30 minutes).
        The monitoring will be done in the background.

        Args:
            device_id: str, the device UUID to monitor
            duration: int, the duration to monitor, default is 1800 seconds (30 minutes)
        """
        logger.debug(f"Monitoring heart rate of {device_id} for {duration} seconds")
        self.client = BleakClient(device_id)
        if self.client.is_connected:
            logger.warning(f"Already connected to {device_id}")
        else:
            asyncio.create_task(self.background_monitor(duration))
        return

    async def background_monitor(self, duration: int):
        if not self.client:
            return
        async with self.client:
            self.db.clear()
            await self.client.start_notify(
                HR_MEASUREMENT_CHAR_UUID, self.count_heart_rate
            )
            # Keep listening for duration seconds
            await asyncio.sleep(duration)
            await self.client.stop_notify(HR_MEASUREMENT_CHAR_UUID)
            logger.info(f"Stopped monitoring heart rate of {self.client.address}")

    def count_heart_rate(self, sender: int, data: bytearray):
        """Count heart rate value from notification payload."""

        flags = data[0]

        hr_format_uint16 = flags & 0x01
        index = 1

        # Heart Rate Value
        if hr_format_uint16:
            heart_rate = int.from_bytes(data[index : index + 2], byteorder="little")
            index += 2
        else:
            heart_rate = data[index]
            index += 1
        logger.debug(f"Heart Rate: {heart_rate} bpm")
        self.db.insert(time.time(), heart_rate)

    # Tool: Get Heart Rate
    async def get_heart_rate(self) -> int:
        """Get the current HR, use last 10 sec and return the average of HR.

        Returns:
            dict, the average of HR in the 10 seconds since start_time, e.g.
            {
                "avg_hr": int
            }
        """
        # start time is 10 seconds ago
        start_time = time.time() - 10
        end_time = start_time + 10

        # round up by ceiling to the nearest integer
        return {"avg_hr": math.ceil(self.db.avg(start_time, end_time))}

    def get_heart_rate_bucket(
        self,
        since_from: float = 10.0,
        bucket_size: float = 1.0,
    ) -> List[dict]:
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
        end_time = time.time()
        start_time = end_time - since_from
        buckets = self.db.time_bucket(start_time, end_time, bucket_size)
        result = []
        for t, v in buckets:
            result.append(
                {
                    "time": t,
                    "value": math.ceil(v),
                }
            )
        return result

    # Tool: Evaluate Active Heart Rate
    def evaluate_active_heart_rate(self) -> dict:
        """Evaluate the active heart rate by the max heart rate of last min.

        Returns:
            dict, the max heart rate of last min, e.g.
            {
                "max_hr": int
            }
        """
        start_time = time.time() - 60
        data = self.db.query(start_time, time.time())
        if len(data) == 0:
            return {
                "max_hr": 0,
            }
        max_hr = max(val for ts, val in data)
        return {
            "max_hr": max_hr,
        }

    def build_heart_rate_chart(self, since_from: float = 600.0) -> str:
        """
        Build a heart rate plot chart using heart rate bucket data (bucket size 1s) and overlay the average heart rate line.
        Args:
            since_from: float, how many seconds ago to start (default 600s = 10min)
        Returns:
            str: The URL of the chart image (PNG)
        """
        bucket_size = 1

        bucket_len = since_from / bucket_size
        if bucket_len > 60:
            bucket_size = math.ceil(since_from / 60)
        else:
            bucket_size = 1
        data = self.get_heart_rate_bucket(
            since_from=since_from, bucket_size=bucket_size
        )
        if not data:
            logger.warning("No heart rate data available for chart.")
            return ""
        times = [d["time"] for d in data]
        # convert to datetime
        times = [datetime.fromtimestamp(t) for t in times]
        values = [d["value"] for d in data]
        if not values:
            logger.warning("No heart rate values to plot.")
            return ""
        avg_hr = sum(values) / len(values)
        plt.figure(figsize=(12, 6))
        plt.plot(times, values, label="Heart Rate", marker="o")
        plt.axhline(
            y=avg_hr, color="r", linestyle="--", label=f"Average HR: {avg_hr:.1f} bpm"
        )
        plt.xlabel("Time")
        plt.ylabel("Heart Rate (bpm)")
        plt.title("Heart Rate Over Time (bucketed by 10s)")
        plt.legend()
        plt.tight_layout()
        # Save PNG for debugging, the file should in tmp folder
        tmp_dir = tempfile.gettempdir()
        debug_file = os.path.join(tmp_dir, f"debug_{time.time()}.png")
        plt.savefig(debug_file, format="png")
        # full path of debug.png
        logger.debug(f"Debug PNG chart saved as {debug_file}")
        key = upload_file(debug_file)
        if key:
            logger.info(f"Debug PNG chart uploaded to {key}")
            plt.close()
        else:
            logger.error("Failed to upload debug PNG chart")
            svg_buffer = io.StringIO()
            plt.savefig(svg_buffer, format="svg")
            plt.close()
            key = svg_buffer.getvalue()
            svg_buffer.close()
        return key
