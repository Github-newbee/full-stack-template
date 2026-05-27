import os
import threading
import time


EPOCH_MS = 1_704_067_200_000
WORKER_ID_BITS = 10
SEQUENCE_BITS = 12
MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1


def parse_snowflake_id(value: str) -> int:
    try:
        snowflake_id = int(value)
    except ValueError as exc:
        raise ValueError("Invalid snowflake id") from exc
    if snowflake_id <= 0:
        raise ValueError("Invalid snowflake id")
    return snowflake_id


class SnowflakeGenerator:
    def __init__(self, worker_id: int | None = None) -> None:
        if worker_id is None:
            worker_id = int(os.getenv("SNOWFLAKE_WORKER_ID", "1"))
        if worker_id < 0 or worker_id > MAX_WORKER_ID:
            raise ValueError(f"SNOWFLAKE_WORKER_ID must be between 0 and {MAX_WORKER_ID}")

        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def next_id(self) -> int:
        with self.lock:
            timestamp = self._timestamp_ms()
            if timestamp < self.last_timestamp:
                timestamp = self.last_timestamp

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & MAX_SEQUENCE
                if self.sequence == 0:
                    timestamp = self._wait_next_ms(timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp
            return (
                ((timestamp - EPOCH_MS) << (WORKER_ID_BITS + SEQUENCE_BITS))
                | (self.worker_id << SEQUENCE_BITS)
                | self.sequence
            )

    @staticmethod
    def _timestamp_ms() -> int:
        return int(time.time() * 1000)

    def _wait_next_ms(self, timestamp: int) -> int:
        next_timestamp = self._timestamp_ms()
        while next_timestamp <= timestamp:
            next_timestamp = self._timestamp_ms()
        return next_timestamp


generator = SnowflakeGenerator()


def next_snowflake_id() -> int:
    return generator.next_id()
