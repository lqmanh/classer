import os
import pendulum


class History:
    '''Store information about previous runs of classer.'''

    def __init__(self, path='~/.local/share/classer/history'):
        self.path = os.path.expanduser(path)
        # make necessary directories for history files
        os.makedirs(self.path, exist_ok=True)
        # list of paths to files storing history
        self.entries = []

    def update(self):
        '''Update entry list and sort it by time (ascending).'''

        self.entries = [entry.path for entry in os.scandir(self.path)]
        self.entries.sort(key=lambda entry: os.path.getmtime(entry))

    def get(self):
        '''Yield history entries.'''

        for entry in self.entries:
            yield entry

    def get_latest(self):
        '''Return the latest history entry or None if the list is empty.'''

        try:
            return self.entries[-1]
        except IndexError:
            return None

    def new(self):
        '''Add a new history entry to entry list and return it.'''

        filename = pendulum.now().format('%Y%m%d%H%M%S.txt')
        filepath = os.path.join(self.path, filename)
        self.entries.append(filepath)
        return filepath

    def print_entry(self, entry):
        '''Print history entry.'''

        print(f'{entry}:')
        with open(entry) as f:
            for line in f:
                print(line, end='')

    def print(self, n):
        '''Print n latest history entries. If n is smaller than 1 or greater
        than the number of entries, print all.
        '''

        if n < 1:
            n = len(self.entries)

        for i in range(n):
            try:
                self.print_entry(self.entries[-i - 1])
            except IndexError:
                return
            else:
                print()

    def remove(self, n):
        '''Remove n oldest history entries. If n is smaller than 1, do nothing;
        if n is greater than the number of entries, remove all.
        '''

        for i in range(n):
            try:
                entry = self.entries.pop(0)
            except IndexError:
                return
            else:
                os.remove(entry)

    def clear(self):
        '''Remove all history entries.'''

        for entry in self.entries:
            os.remove(entry)
        self.entries.clear()
