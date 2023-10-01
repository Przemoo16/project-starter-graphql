class HealthError(Exception):
    def __init__(self, report: dict[str, str]):
        super().__init__()
        self.report = report
