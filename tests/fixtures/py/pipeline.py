import os
from datetime import datetime, timedelta

MAX_RETRIES = 3


class DataPipeline:
    """Load and transform rows."""

    def __init__(self, source_name, batch_size=100):
        self.source_name = source_name
        self.batch_size = batch_size
        self._rows = []

    def load_rows(self, raw_rows):
        for index, row in enumerate(raw_rows):
            clean_row = {k.strip(): v for k, v in row.items()}
            self._rows.append(clean_row)
        return len(self._rows)

    def summary(self):
        started_at = datetime.now() - timedelta(minutes=5)
        return f"{self.source_name}: {len(self._rows)} rows since {started_at:%H:%M}"


def build_pipeline(name, *extra_args, **options):
    pipeline = DataPipeline(name, batch_size=options.get("batch_size", 10))
    total = pipeline.load_rows([{" a ": 1}, {" b ": 2}])
    print(pipeline.summary(), total, os.getcwd() != "", MAX_RETRIES, extra_args)
    return pipeline


if __name__ == "__main__":
    build_pipeline("demo", 1, 2, batch_size=50)
