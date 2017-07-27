import os

from classer import History, ReverseClassifier


def test_move_file(tmpdir):
    filepath = tmpdir.join('file.txt')
    filepath.write('')
    resultdir = tmpdir.mkdir('result')

    worker = ReverseClassifier(None)
    worker.move_file(filepath, resultdir.join('file.txt'))

    assert set(os.listdir(resultdir)) == {'file.txt'}


def test_clean_dirs(tmpdir):
    subdir1 = tmpdir.mkdir('subdir1')
    subdir2 = subdir1.mkdir('subdir2')
    tmpdir.join('file.txt').write('')  # just to stop clean_dirs method at this level

    worker = ReverseClassifier(None)
    worker.clean_dirs(subdir2)

    assert set(os.listdir(tmpdir)) == {'file.txt'}


def test_move_files(tmpdir):
    filepath1 = tmpdir.join('file1.txt')
    filepath1.write('')
    filepath2 = tmpdir.join('file2.txt')
    filepath2.write('')
    resultdir = tmpdir.mkdir('resultdir')

    historypath = tmpdir.join('history')
    historypath.write(f"Moved {resultdir.join('file1.txt')} to {filepath1}\n"
                      f"Copied {resultdir.join('file2.txt')} to {filepath2}\n")

    with open(historypath) as f:
        worker = ReverseClassifier(f)
        worker.move_files()

    assert set(os.listdir(resultdir)) == {'file1.txt'}
    assert set(os.listdir(tmpdir)) == {'resultdir', 'history'}
