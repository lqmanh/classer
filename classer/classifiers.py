import fnmatch
import os
import re
import shutil

import hjson as json
import pendulum


class Classifier:
    """Normal classifier."""

    def __init__(self, exprs, src, dst, lastrun_file, **options):
        self.exprs = exprs
        self.src = os.path.expanduser(src)
        self.dst = os.path.expanduser(dst)
        self.lastrun_file = lastrun_file
        self.options = options  # a list of additional options

    def match_name(self, exprs, name):
        """Check if name matchs any of the glob patterns."""
        return any(fnmatch.fnmatch(name, expr) for expr in exprs)

    def match_time(self, filepath):
        """Check if the modification time of the file is between some period of time."""
        mod_time = pendulum.from_timestamp(os.path.getmtime(filepath))

        if self.options.get('since'):
            mintime = pendulum.parse(self.options['since'])
            if mod_time < mintime:
                return False
        if self.options.get('until'):
            maxtime = pendulum.parse(self.options['until'])
            if mod_time > maxtime:
                return False
        return True

    def match_size(self, filepath):
        """Check if the size of the file is between some amount of volume in bytes."""
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
        """Check if the file satisfies all provided conditions."""
        filepath = os.path.join(root, filename)
        return all([self.match_name(self.exprs, filename),
                    self.match_time(filepath),
                    self.match_size(filepath)])

    def filtered(self, recursive):
        """Filter files.

        Yield tuples of source filepath, destination filepath and filename itself.
        """
        for root, dirnames, filenames in os.walk(self.src):
            if root == self.dst:
                continue
            if self.options.get('exclude'):
                # modify dirnames in place
                dirnames[:] = list(
                    filter(lambda d: not self.match_name(self.options['exclude'], d),
                           dirnames)
                )

            filtered = filter(lambda filename: self.match_file(root, filename),
                              filenames)
            for filename in filtered:
                yield (os.path.join(root, filename),
                       os.path.join(self.dst, filename),
                       filename)

            # return at level 1 immediately if not recursive
            if not recursive:
                return

    def move_file(self, src, dst):
        """Move file."""
        shutil.move(src, dst)
        self.lastrun_file.write(f'Moved {src} to {dst}\n')
        print(f'Moved {src} to {dst}')

    def copy_file(self, src, dst):
        """Copy file."""
        shutil.copy2(src, dst)
        self.lastrun_file.write(f'Copied {src} to {dst}\n')
        print(f'Copied {src} to {dst}')

    def rename_on_dup(self, src, dst, filename):
        """Rename this duplicate then move it."""
        dst_dir = dst[:-len(filename)]
        head, _, ext = filename.rpartition('.')
        if not head:
            head, ext = ext, head
        copy_index = 2  # index of the duplicate
        while os.path.exists(dst):
            filename = head + f' ({copy_index}).' + ext
            dst = dst_dir + filename
            copy_index += 1
        self.move_file(src, dst)

    def overwrite_on_dup(self, src, dst, filename):
        """Replace the old file with the duplicate."""
        os.remove(dst)
        self.move_file(src, dst)

    def act_on_dup(self, src, dst, filename):
        """Choose action to do with the duplicate."""
        dup_option = self.options.get('duplicate')
        if dup_option == 'ask':
            print(f'{dst} already exists.')
            reply = input('(R)ename, (O)verwrite or (I)gnore? [r/O/I]: ').lower()
        else:
            reply = None

        if dup_option == 'rename' or reply == 'r':
            self.rename_on_dup(src, dst, filename)
        elif dup_option == 'overwrite' or reply == 'o':
            self.overwrite_on_dup(src, dst, filename)
        # if dup_option is ignore or None or reply is i or anything else,
        # do nothing

    def move_files(self):
        """Move or copy filtered files and resolve duplicates."""
        if self.options.get('copy'):
            action = self.copy_file
        else:
            action = self.move_file

        for src, dst, filename in self.filtered(self.options.get('recursive')):
            if os.path.exists(dst):
                self.act_on_dup(src, dst, filename)
            else:
                action(src, dst)

    def clean_dirs(self):
        """Remove all empty directories recursively from src."""
        for root, dirs, files in os.walk(self.src, topdown=False):
            if not dirs and not files:
                os.removedirs(root)
        print(f'Removed empty directories from {self.src}')

    def classify(self):
        """Classify files."""
        # make necessary directories for classified files
        os.makedirs(self.dst, exist_ok=True)

        self.move_files()

        if self.options.get('autoclean'):
            self.clean_dirs()


class AutoClassifier:
    """Automated classifier."""

    def __init__(self, path, lastrun_file):
        self.criteria_path = os.path.expanduser(path)
        self.lastrun_file = lastrun_file

        self.criteria = self.load_criteria()

    def load_criteria(self):
        """Load criteria from file.

        Return criteria as a dict. If the file fails to load, return an empty dict.
        """
        try:
            with open(self.criteria_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def classify(self):
        """Classify files using normal classifiers."""
        targets = self.criteria.pop('targets', {})
        exclusions = self.criteria.pop('exclusions', {})

        # pop these keys so as not to conflict when passed as additional options
        # to mini_worker (a Classifier instance)
        src = self.criteria.pop('src')
        top_dst = self.criteria.pop('dst')

        for target in targets:
            exprs = targets[target]
            dst = os.path.join(top_dst, target)
            exclude = exclusions.get(target, [])

            mini_worker = Classifier(exprs, src, dst, self.lastrun_file,
                                     exclude=exclude, **self.criteria)
            mini_worker.classify()


class ReverseClassifier:
    """Reverse classifier."""

    rename_on_dup = Classifier.rename_on_dup
    overwrite_on_dup = Classifier.overwrite_on_dup
    act_on_dup = Classifier.act_on_dup

    def __init__(self, lastrun_file, **options):
        self.lastrun_file = lastrun_file
        self.options = options  # a list of additional options

    def move_file(self, src, dst):
        """Move file."""
        shutil.move(src, dst)
        print(f'Moved {src} back to {dst}')

    def clean_dirs(self, path):
        """Remove all empty directories recursively from path."""
        try:
            os.removedirs(path)
        except OSError:
            pass
        else:
            print(f'Removed empty directories from {path}')

    def move_files(self):
        """Move files and resolve duplicates."""
        for line in self.lastrun_file:
            match = re.fullmatch(r'((Moved)|(Copied)) (.+?) to (.+?)', line.strip())
            if not match:
                continue
            action, *_, new_dst, new_src = match.groups()
            new_dst_dir, filename = os.path.split(new_dst)
            new_src_dir = os.path.split(new_src)[0]

            try:
                if action == 'Copied':
                    os.remove(new_src)
                    continue
                # make necessary directories for classified files
                os.makedirs(new_dst_dir, exist_ok=True)
                if os.path.exists(new_dst):
                    self.act_on_dup(new_src, new_dst, filename)
                else:
                    self.move_file(new_src, new_dst)
            except FileNotFoundError:
                continue

            if self.options.get('autoclean'):
                self.clean_dirs(new_src_dir)

    def classify(self):
        """Classify files by moving files back to their old paths."""
        self.move_files()
