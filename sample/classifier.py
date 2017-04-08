import shutil
import os
import fnmatch


class Classifier:
    def __init__(self, expr, src, dst):
        self.expr = expr
        self.src = src
        self.dst = dst

    def classify(self):
        # make necessary directories for classified files
        os.makedirs(self.dst, exist_ok=True)

        for root, dirs, files in os.walk(self.src):
            for file in filter(lambda file: fnmatch.fnmatch(file, self.expr), files):
                shutil.move(os.path.join(root, file), os.path.join(self.dst, file))
