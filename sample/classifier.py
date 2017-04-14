import shutil
import os
import fnmatch
import pendulum


class Classifier:
    def __init__(self, expr, src, dst, **options):
        self.expr = expr
        self.src = src
        self.dst = dst
        self.options = options  # store any additional options

    def match_name(self, filename):
        return fnmatch.fnmatch(filename, self.expr)

    def match_time(self, filepath):
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

    def match_file(self, root, filename):
        filepath = os.path.join(root, filename)
        return all([self.match_name(filename), self.match_time(filepath)])

    def move_recursively(self):
        for root, dirnames, filenames in os.walk(self.src):
            filtered = filter(lambda filename: self.match_file(root, filename),
                              filenames)
            for filename in filtered:
                shutil.move(os.path.join(root, filename),
                            os.path.join(self.dst, filename))

    def move_no_recursively(self):
        with os.scandir(self.src) as it:
            filtered = filter(lambda entry: self.match_file(*os.path.split(entry.path)),
                              it)
            for entry in filtered:
                shutil.move(entry.path, os.path.join(self.dst, entry.name))

    def clean_dirs(self):
        for root, dirs, files in os.walk(self.src, topdown=False):
            if not dirs and not files:
                os.removedirs(root)

    def classify(self):
        # make necessary directories for classified files
        os.makedirs(self.dst, exist_ok=True)

        if self.options.get('recursive'):
            self.move_recursively()
        else:
            self.move_no_recursively()

        if self.options.get('autoclean'):
            self.clean_dirs()
