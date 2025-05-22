import time

import pytest

from hrm.ts_db import TsDB


def test_insert_and_latest():
    db = TsDB(maxlen=3)
    db.insert(1.0, 10.0)
    db.insert(2.0, 20.0)
    db.insert(3.0, 30.0)
    assert db.latest() == (3.0, 30.0)
    db.insert(4.0, 40.0)
    # maxlen=3, so the first entry should be dropped
    assert db.latest() == (4.0, 40.0)
    assert list(db.data) == [(2.0, 20.0), (3.0, 30.0), (4.0, 40.0)]


def test_query():
    db = TsDB()
    db.insert(1.0, 10.0)
    db.insert(2.0, 20.0)
    db.insert(3.0, 30.0)
    result = db.query(1.5, 2.5)
    assert result == [(2.0, 20.0)]
    result = db.query(0.0, 5.0)
    assert result == [(1.0, 10.0), (2.0, 20.0), (3.0, 30.0)]
    result = db.query(4.0, 5.0)
    assert result == []


def test_avg_from():
    db = TsDB()
    db.insert(1.0, 10.0)
    db.insert(2.0, 20.0)
    db.insert(3.0, 30.0)
    avg = db.avg_from(2.0)
    assert avg == pytest.approx((20.0 + 30.0) / 2)
    avg = db.avg_from(1.0)
    assert avg == pytest.approx((10.0 + 20.0 + 30.0) / 3)
    with pytest.raises(ZeroDivisionError):
        db.avg_from(4.0)


def test_empty_latest():
    db = TsDB()
    assert db.latest() is None


def test_with_real_time():
    COUNT = 100
    AVERAGE = (0 + COUNT - 1) / 2
    db = TsDB(COUNT + 50)
    from_time = time.time()
    for i in range(COUNT):
        db.insert(time.time(), i)
        time.sleep(0.001)
    assert db.avg_from(from_time) == AVERAGE
    _, value = db.latest()
    assert value == COUNT - 1


def test_clear():
    db = TsDB()
    db.insert(1.0, 10.0)
    db.insert(2.0, 20.0)
    assert len(db.data) == 2
    db.clear()
    assert len(db.data) == 0
    assert db.latest() is None
    assert db.query(0, 10) == []


def test_avg():
    db = TsDB()
    db.insert(1.0, 10.0)
    db.insert(2.0, 20.0)
    db.insert(3.0, 30.0)
    # Average from 1.0 to 2.0 (should include 1.0 and 2.0)
    avg = db.avg(1.0, 2.0)
    assert avg == pytest.approx((10.0 + 20.0) / 2)
    # Average from 2.0 to 3.0 (should include 2.0 and 3.0)
    avg = db.avg(2.0, 3.0)
    assert avg == pytest.approx((20.0 + 30.0) / 2)
    # Average for a range with exception
    with pytest.raises(ZeroDivisionError):
        db.avg(4.0, 5.0)


def test_time_bucket():
    db = TsDB()
    db.insert(1.0, 10.0)
    db.insert(1.5, 12.0)
    db.insert(2.0, 20.0)
    db.insert(2.5, 22.0)
    db.insert(3.0, 30.0)
    db.insert(3.5, 32.0)
    buckets = db.time_bucket(0.0, 4.0, 1.0)
    assert len(buckets) == 4
    assert buckets == [(0.0, 0.0), (1.0, 11.0), (2.0, 21.0), (3.0, 31.0)]
    buckets = db.time_bucket(1.0, 4.0, 0.5)
    assert len(buckets) == 6
    assert buckets == [
        (1.0, 10.0),
        (1.5, 12.0),
        (2.0, 20.0),
        (2.5, 22.0),
        (3.0, 30.0),
        (3.5, 32.0),
    ]
