from dataclasses import dataclass


@dataclass
class HealthError(Exception):
    report: dict[str, str]
