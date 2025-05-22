import asyncio
import math
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hrm.bt_client import HEART_RATE_SERVICE_UUID, BtClient


@pytest.fixture(autouse=True)
def patch_print(monkeypatch):
    # Patch the custom print to avoid file writes during tests
    monkeypatch.setattr("hrm.bt_client.print", lambda msg: None)


@pytest.fixture
def bt_client():
    return BtClient()


@pytest.mark.asyncio
async def test_list_bluetooth_devices(bt_client):
    fake_device = MagicMock()
    fake_device.address = "00:11:22:33:44:55"
    fake_device.name = "TestHRM"
    fake_device.rssi = -50
    adv_data = MagicMock()
    adv_data.service_uuids = [HEART_RATE_SERVICE_UUID]
    devices = {("dev", 1): (fake_device, adv_data)}
    with patch(
        "hrm.bt_client.BleakScanner.discover", new=AsyncMock(return_value=devices)
    ):
        result = await bt_client.list_bluetooth_devices()
        assert fake_device.address in result
        assert result[fake_device.address]["name"] == "TestHRM"
        assert result[fake_device.address]["rssi"] == -50


@pytest.mark.asyncio
async def test_monitoring_heart_rate_creates_task(bt_client):
    with (
        patch("hrm.bt_client.BleakClient") as MockBleakClient,
        patch("hrm.bt_client.asyncio.create_task") as mock_create_task,
    ):
        mock_client = MockBleakClient.return_value
        mock_client.is_connected = False
        dummy_task = asyncio.create_task(asyncio.sleep(0))

        def side_effect(arg):
            # Return dummy_task for asyncio.sleep(0), MagicMock for background_monitor
            if (
                getattr(arg, "cr_code", None)
                and arg.cr_code.co_name == "background_monitor"
            ):
                return MagicMock()
            return dummy_task

        mock_create_task.side_effect = side_effect
        await bt_client.monitoring_heart_rate("device_id", duration=10)
        # Should be called at least once for background_monitor
        called_args = [c[0][0] for c in mock_create_task.call_args_list]
        assert any(
            hasattr(arg, "cr_code") and arg.cr_code.co_name == "background_monitor"
            for arg in called_args
        )
        dummy_task.cancel()  # Only await the real asyncio task


@pytest.mark.asyncio
async def test_monitoring_heart_rate_already_connected(bt_client):
    with (
        patch("hrm.bt_client.BleakClient") as MockBleakClient,
        patch("hrm.bt_client.asyncio.create_task") as mock_create_task,
    ):
        mock_client = MockBleakClient.return_value
        mock_client.is_connected = True
        await bt_client.monitoring_heart_rate("device_id", duration=10)
        mock_create_task.assert_not_called()


@pytest.mark.asyncio
async def test_background_monitor(bt_client):
    # Patch client and its methods
    mock_client = MagicMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.connect = AsyncMock()
    mock_client.start_notify = AsyncMock()
    mock_client.stop_notify = AsyncMock()
    mock_client.disconnect = AsyncMock()
    bt_client.client = mock_client
    with patch.object(bt_client.db, "clear") as mock_clear:
        await bt_client.background_monitor(duration=0.01)
        mock_client.connect.assert_called_once()
        mock_client.start_notify.assert_called_once()
        mock_client.stop_notify.assert_called_once()
        mock_client.disconnect.assert_called_once()
        mock_clear.assert_called_once()


@pytest.mark.parametrize(
    "flags,expected_hr",
    [
        (0x00, 60),  # 8-bit
        (0x01, 300),  # 16-bit
    ],
)
def test_count_heart_rate(bt_client, flags, expected_hr):
    with (
        patch.object(bt_client.db, "insert") as mock_insert,
        patch("time.time", return_value=123.0),
    ):
        if flags == 0x00:
            data = bytearray([flags, expected_hr])
        else:
            data = bytearray([flags]) + expected_hr.to_bytes(2, "little")
        bt_client.count_heart_rate(1, data)
        mock_insert.assert_called_once_with(123.0, expected_hr)


@pytest.mark.asyncio
async def test_get_heart_rate(bt_client):
    with patch.object(bt_client.db, "avg", return_value=59.1):
        result = await bt_client.get_heart_rate()
        assert result == {"avg_hr": math.ceil(59.1)}


@pytest.mark.parametrize(
    "data,expected",
    [
        ([(1, 60), (2, 70)], [{"time": 1, "value": 60}, {"time": 2, "value": 70}]),
        ([], []),
    ],
)
def test_get_heart_rate_bucket(bt_client, data, expected):
    with (
        patch("time.time", return_value=10.0),
        patch.object(
            bt_client.db, "time_bucket", return_value=[(d[0], d[1]) for d in data]
        ),
    ):
        result = bt_client.get_heart_rate_bucket(since_from=10.0, bucket_size=1.0)
        assert result == [{"time": d[0], "value": math.ceil(d[1])} for d in data]


@pytest.mark.parametrize(
    "data,expected",
    [
        ([], {"max_hr": 0}),
        ([(1, 60), (2, 80)], {"max_hr": 80}),
    ],
)
def test_evaluate_active_heart_rate(bt_client, data, expected):
    with (
        patch("time.time", return_value=100.0),
        patch.object(bt_client.db, "query", return_value=data),
    ):
        result = bt_client.evaluate_active_heart_rate()
        assert result == expected


@patch("hrm.bt_client.upload_file", return_value="http://fake.url/chart.png")
@patch("hrm.bt_client.plt")
def test_build_heart_rate_chart(mock_plt, mock_upload_file, bt_client):
    # Patch get_heart_rate_bucket to return fake data
    with patch.object(
        bt_client,
        "get_heart_rate_bucket",
        return_value=[{"time": 1, "value": 60}, {"time": 2, "value": 70}],
    ):
        url = bt_client.build_heart_rate_chart(since_from=2.0)
        assert url == "http://fake.url/chart.png"
        mock_plt.figure.assert_called()
        mock_plt.plot.assert_called()
        mock_plt.savefig.assert_called()
        mock_upload_file.assert_called()

    # Test no data case
    with patch.object(bt_client, "get_heart_rate_bucket", return_value=[]):
        url = bt_client.build_heart_rate_chart(since_from=2.0)
        assert url == ""
