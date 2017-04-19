import shutil
import os
import fnmatch
import pendulum


class Classifier:
    def __init__(self, expr, src, dst, **options):
        self.expr = expr
        self.src = src
        self.dst = dst
        self.options = options  # a list of additional options

    def match_name(self, expr, name):
        '''Return True if name matchs a glob pattern.'''

        return fnmatch.fnmatch(name, expr)

    def match_time(self, filepath):
        '''Return True if the modification time of the file is between some
        period of time.
        '''

        modified_time = pendulum.from_timestamp(os.path.getmtime(filepath))

        if self.options.get('since'):
            mintime = pendulum.parse(self.options['since'])
            if modified_time < mintime:
                return False
        if self.options.get('until'):
            maxtime = pendulum.parse(self.options['until'])
            if modified_time > maxtime:
                return False
        return True

    def match_size(self, filepath):
        size = os.path.getsize(filepath)

        if self.options.get('larger'):
            minsize = self.options['larger']
            if size < minsize:
                return False
        if self.options.get('smaller'):
            maxsize = self.options['smaller']
            if size > maxsize:
                return False
        return True

    def match_file(self, root, filename):
        '''Return True if the file satisfies all conditions.'''

        filepath = os.path.join(root, filename)
        return all([self.match_name(self.expr, filename),
                    self.match_time(filepath), self.match_size(filepath)])

    def filtered_files(self, recursive):
        for root, dirnames, filenames in os.walk(self.src):
            if self.options.get('exclude'):
                dirnames[:] = list(
                    filter(lambda d: not self.match_name(self.options['exclude'], d),
                           dirnames)
                )

            filtered = filter(lambda filename: self.match_file(root, filename),
                              filenames)
            for filename in filtered:
                yield os.path.join(root, filename), os.path.join(self.dst, filename)

            if not recursive:
                return

    def move_files(self):
        for src, dst in self.filtered_files(self.options.get('recursive')):
            shutil.move(src, dst)
            print(f'Moved {src} to {dst}.')

    def clean_dirs(self):
        '''Removes all empty directories recursively.'''

        for root, dirs, files in os.walk(self.src, topdown=False):
            if not dirs and not files:
                os.removedirs(root)

    def classify(self):
        '''Classify files.'''

        # make necessary directories for classified files
        os.makedirs(self.dst, exist_ok=True)

        self.move_files()

        if self.options.get('autoclean'):
            self.clean_dirs()
            print('Removed empty directories.')
