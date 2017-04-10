import shutil
import os
import fnmatch


class Classifier:
    def __init__(self, expr, src, dst, **options):
        self.expr = expr
        self.src = src
        self.dst = dst
        self.options = options  # store any additional options

    def move_files(self):
        def match(file):
            conditions = (fnmatch.fnmatch(file, self.expr),)
            return all(conditions)

        if self.options.get('recursive', None):
            for root, dirs, files in os.walk(self.src):
                for file in filter(match, files):
                    shutil.move(os.path.join(root, file), os.path.join(self.dst, file))
            return

        with os.scandir(self.src) as it:
            for entry in filter(lambda entry: entry.is_file() and match(entry.name), it):
                shutil.move(entry.path, os.path.join(self.dst, entry.name))

    def clean_dirs(self):
        for root, dirs, files in os.walk(self.src, topdown=False):
            if not dirs and not files:
                os.removedirs(root)

    def classify(self):
        # make necessary directories for classified files
        os.makedirs(self.dst, exist_ok=True)

        self.move_files()
        if self.options.get('autoclean', None):
            self.clean_dirs()
