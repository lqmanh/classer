import shutil
import os
import fnmatch
import re
import hjson as json
import pendulum


class Classifier:
    '''Normal classifier.'''

    def __init__(self, exprs, src, dst, lastrun_file, **options):
        self.exprs = exprs
        self.src = os.path.abspath(src)
        self.dst = os.path.abspath(dst)
        self.lastrun_file = lastrun_file
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
        '''Return True if the file satisfies all provided conditions.'''

        filepath = os.path.join(root, filename)
        return all([self.match_name(self.exprs, filename),
                    self.match_time(filepath),
                    self.match_size(filepath)])

    def filtered(self, recursive):
        '''Filter files and yield tuples of source filepath, destination filepath
        and filename itself.
        '''

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
        '''Move file from src to dst.'''

        shutil.move(src, dst)
        self.lastrun_file.write(f'Moved {src} to {dst}\n')
        print(f'Moved {src} to {dst}')

    def rename_on_dup(self, src, dst, filename):
        '''Rename this duplicate then move it.'''

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
        '''Replace the old file with this duplicate.'''

        os.remove(dst)
        self.move_file(src, dst)

    def act_on_dup(self, src, dst, filename):
        '''Choose action to do with the duplicate.'''

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
        '''Move filtered files or resolve duplicates.'''

        for src, dst, filename in self.filtered(self.options.get('recursive')):
            if os.path.exists(dst):
                self.act_on_dup(src, dst, filename)
            else:
                self.move_file(src, dst)

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
    '''Automated classifier.'''

    def __init__(self, path, lastrun_file):
        self.criteria_path = os.path.abspath(path)
        self.lastrun_file = lastrun_file

        self.load_criteria()

    def load_criteria(self):
        '''Loads criteria from json file. If the file fails to load,
        self.criteria is default to an empty dict.
        '''

        try:
            with open(self.criteria_path) as f:
                self.criteria = json.load(f)
        except FileNotFoundError:
            self.criteria = {}

    def classify(self):
        '''Classify files using Classifier instances.'''

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
    '''Reverse classifier.'''

    def __init__(self, lastrun_file):
        self.lastrun_file = lastrun_file

    def classify(self):
        '''Move files back to their old paths.'''

        for line in self.lastrun_file:
            line = line.strip()
            match = re.fullmatch(r'Moved (.+?) to (.+?)', line)
            if not match:
                continue
            dst = match.group(1)
            # make necessary directories for classified files
            os.makedirs(os.path.split(dst)[0], exist_ok=True)
            src = match.group(2)
            shutil.move(src, dst)
            print(f'Moved {src} back to {dst}')
