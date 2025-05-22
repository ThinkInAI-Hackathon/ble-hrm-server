import time
from collections import deque
from typing import List


class TsDB:
    """
    A class for storing time-series data in memory.
    """

    def __init__(self, maxlen=50000):
        """
        Initialize the database with the given maximum length.
        """
        self.data = deque(maxlen=maxlen)

    def insert(self, timestamp: float, value: float):
        """
        Insert the data into the database.
        """
        self.data.append((timestamp, value))

    def query(self, start: float, end: float):
        """
        Query the data from the given start timestamp to the given end timestamp.
        If end is not provided, use the current time as the end timestamp.
        """
        if start >= end:
            raise ValueError("Start timestamp must be less than end timestamp")
        return [(ts, val) for ts, val in self.data if start <= ts <= end]

    def avg(self, start: float, end: float):
        """
        Calculate the average value of the data from the given start timestamp to the given end timestamp.
        """
        if len(self.data) == 0:
            return 0
        values = [val for ts, val in self.query(start, end)]
        return sum(values) / len(values)

    # def query_from(self, start: float):
    #     """
    #     Query the data from the given start timestamp.
    #     """
    #     return [(ts, val) for ts, val in self.data if ts >= start]

    def latest(self):
        return self.data[-1] if self.data else None

    def avg_from(self, start: float):
        """
        Calculate the average value of the data from the given start timestamp.
        """
        return self.avg(start, time.time())

    def clear(self):
        """
        Clear all data from the database.
        """
        self.data.clear()

    def time_bucket(self, start: float, end: float, bucket_size: float) -> List[float]:
        """
        Bucket the data from the given start timestamp to the given end timestamp into the given time bucket size.
        """
        if bucket_size <= 0:
            raise ValueError("Bucket size must be greater than 0")
        num_buckets = int((end - start) / bucket_size)
        buckets = [[] for _ in range(num_buckets)]
        data = self.query(start, end)
        for ts, val in data:
            index = int((ts - start) // bucket_size)
            if 0 <= index < num_buckets:
                buckets[index].append(val)
        result = []
        time_bucket = start
        for bucket in buckets:
            if len(bucket) > 0:
                result.append((time_bucket, sum(bucket) / len(bucket)))
            else:
                result.append((time_bucket, 0.0))
            time_bucket += bucket_size

        return result
