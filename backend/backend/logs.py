import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from typing import Any


def setup_logging(level: str) -> QueueListener:
    queue: Queue[Any] = Queue(-1)
    queue_handler = QueueHandler(queue)
    logging.basicConfig(
        format=(
            "%(threadName)s(%(thread)d): %(asctime)s - %(levelname)s - "
            "%(name)s:%(lineno)d - %(message)s"
        ),
        level=level,
        handlers=[queue_handler],
    )
    stream_handler = logging.StreamHandler()
    return QueueListener(queue, stream_handler)
