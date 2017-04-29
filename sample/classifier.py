import shutil
import os
import fnmatch
import hjson as json
import pendulum


class Classifier:
    def __init__(self, exprs, src, dst, **options):
        self.exprs = exprs
        self.src = src
        self.dst = dst
        self.options = options  # a list of additional options

    def match_name(self, exprs, name):
        '''Return True if name matchs any of the glob patterns.'''

        return any(fnmatch.fnmatch(name, expr) for expr in exprs)

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
        '''Return True if the size of the file is between some amount of volume
        in bytes.
        '''

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
        return all([self.match_name(self.exprs, filename),
                    self.match_time(filepath), self.match_size(filepath)])

    def filtered_files(self, recursive):
        '''Yield filtered files to move.'''

        for root, dirnames, filenames in os.walk(self.src):
            if self.options.get('exclude'):
                # modify dirnames in place
                dirnames[:] = list(
                    filter(lambda d: not self.match_name(self.options['exclude'], d),
                           dirnames)
                )

            filtered = filter(lambda filename: self.match_file(root, filename),
                              filenames)
            for filename in filtered:
                yield os.path.join(root, filename), os.path.join(self.dst, filename)

            # return at level 1 immediately if not recursive
            if not recursive:
                return

    def move_files(self):
        '''Move files.'''

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


class AutoClassifier:
    def __init__(self, path):
        self.path = path
        self.load_criteria()

    def load_criteria(self):
        try:
            with open(self.path) as f:
                self.criteria = json.load(f)
        except FileNotFoundError:
            self.criteria = {}

    def classify(self):
        targets = self.criteria.pop('targets', {})
        src = self.criteria.pop('src')
        top_dst = self.criteria.pop('dst')
        exclusions = self.criteria.pop('exclusions', {})

        for target in targets:
            exprs = targets[target]
            dst = os.path.join(top_dst, target)
            exclude = exclusions.get(target, [])

            mini_worker = Classifier(exprs, src, dst, exclude=exclude, **self.criteria)
            mini_worker.classify()
