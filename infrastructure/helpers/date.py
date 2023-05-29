from datetime import datetime


def get_utc_timestamp() -> float:
    return (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
