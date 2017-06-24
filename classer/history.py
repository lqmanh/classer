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
        filepath = os.path.join(self.path, filename)
        self.entries.append(filepath)
        return filepath

    def print_entry(self, entry):
        print(f'{entry}:')
        with open(entry) as f:
            for line in f:
                print(line, end='')

    def print(self, n):
        if n <= 0:
            n = len(self.entries)

        count = 0
        for entry in self.entries[::-1]:
            self.print_entry(entry)
            count += 1
            if count >= n:
                break

    def remove(self, n):
        for i in range(n):
            try:
                entry = self.entries.pop(0)
            except IndexError:
                return
            else:
                os.remove(entry)

    def clear(self):
        for entry in self.entries:
            os.remove(entry)
        self.entries.clear()
