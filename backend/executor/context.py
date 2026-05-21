class ExecutionContext:

    def __init__(self):

        self.values = {}

        self.history = []

    def set(self, key, value):

        self.values[key] = value

        self.history.append({
            "key": key,
            "value": value,
        })

    def get(self, key, default=None):

        return self.values.get(key, default)

    def get_all(self):

        return dict(self.values)

    def clear(self):

        self.values = {}

        self.history = []
