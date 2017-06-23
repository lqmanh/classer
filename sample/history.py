import os
import pendulum


class History:
    def __init__(self, path='~/.local/share/classer/history'):
        self.path = os.path.expanduser(path)
        os.makedirs(self.path, exist_ok=True)
        self.entries = []

    def update(self):
        self.entries = [entry.path for entry in os.scandir(self.path)]
        self.entries.sort(key=lambda entry: os.path.getmtime(entry))

    def get(self):
        for entry in self.entries:
            yield entry

    def get_latest(self):
        try:
            return self.entries[-1]
        except IndexError:
            return None

    def new(self):
        filename = pendulum.now().format('%Y%m%d%H%M%S.txt')
        return os.path.join(self.path, filename)
