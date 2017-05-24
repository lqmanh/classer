import os
from . import ReverseClassifier
from . import open_lastrun_file


def test_classify(tmpdir):
    subdir = tmpdir.mkdir('subdir')
    filepath1 = subdir.join('file1.md')
    filepath1.write('')
    filepath2 = subdir.join('file2.txt')
    filepath2.write('')

    src_dir = os.path.abspath(tmpdir)
    dst_dir = os.path.join(tmpdir, 'subdir')
    lastrun_path = tmpdir.join('lastrun.txt')
    lastrun_path.write(f'Moved {src_dir}/file1.md to {dst_dir}/file1.md\n'
                       f'Moved {src_dir}/file2.txt to {dst_dir}/file2.txt\n')

    with open(lastrun_path) as f:
        worker = ReverseClassifier(f)
        worker.classify()

    assert set(os.listdir(tmpdir)) == {'subdir', 'lastrun.txt',
                                       'file1.md', 'file2.txt'}
