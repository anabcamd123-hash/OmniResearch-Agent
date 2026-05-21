from datetime import datetime

class TaskHistory:

    def __init__(self):

        self.records = []

    def add_record(
        self,
        task_name,
        status,
        duration=None
    ):

        record = {
            "task": task_name,
            "status": status,
            "time": datetime.now().strftime(
                "%H:%M:%S"
            )
        }

        if duration is not None:
            record["duration"] = round(duration, 2)

        self.records.append(record)

history = TaskHistory()
