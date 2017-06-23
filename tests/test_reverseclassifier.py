import os
from . import *


def test_classify(tmpdir):
    subdir = tmpdir.mkdir('subdir')
    filepath1 = subdir.join('file1.md')
    filepath1.write('')
    filepath2 = tmpdir.join('file2.txt')
    filepath2.write('')
    filepath3 = subdir.join('file2.txt')
    filepath3.write('')

    src_dir = os.path.abspath(tmpdir)  # old src dir, new dst dir
    dst_dir = os.path.join(tmpdir, 'subdir')  # old dst dir, new src dir

    history = History()

    with open(history.new(), 'w') as f:
        f.write(f'Moved {src_dir}/file1.md to {dst_dir}/file1.md\n'
                f'Moved {src_dir}/file2.txt to {dst_dir}/file2.txt\n')

    history.update()

    with open(history.get_latest()) as f:
        worker = ReverseClassifier(f, autoclean=True, duplicate='rename')
        worker.classify()

    assert set(os.listdir(tmpdir)) == {'file1.md', 'file2.txt', 'file2 (2).txt'}
