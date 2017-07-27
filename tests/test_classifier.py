import os

from classer import Classifier, History
from pendulum import Pendulum


def test_match_name():
    worker = Classifier([], '.', '.', None)

    assert worker.match_name(['*.txt'], 'file.txt')
    assert worker.match_name(['*.txt', '*.md'], 'file.md')
    assert not worker.match_name(['*.txt'], 'file.py')


def test_match_time(tmpdir):
    # file 1: match
    filepath1 = tmpdir.join('file1.txt')
    filepath1.write('')
    filepath1.setmtime(Pendulum(2017, 1, 1).timestamp())
    # file 2: not match
    filepath2 = tmpdir.join('file2.txt')
    filepath2.write('')
    filepath2.setmtime(Pendulum(2018, 1, 1).timestamp())

    worker = Classifier([], '.', '.', None, since='2016-12-31', until='2017-01-02')

    assert worker.match_time(filepath1)
    assert not worker.match_time(filepath2)


def test_match_size(tmpdir):
    # file 1: match
    filepath1 = tmpdir.join('file1.txt')
    with filepath1.open(mode='wb') as f:
        f.truncate(1000)
    # file 2: not match
    filepath2 = tmpdir.join('file2.txt')
    with filepath2.open(mode='wb') as f:
        f.truncate(1024)

    worker = Classifier([], '.', '.', None, larger=999, smaller=1023)

    assert worker.match_size(filepath1)
    assert not worker.match_size(filepath2)


def test_match_file(tmpdir):
    # file 1: match
    filepath1 = tmpdir.join('file1.py')
    filepath1.write('')
    filepath1.setmtime(Pendulum(2017, 1, 1).timestamp())
    # file 2: not match name
    filepath2 = tmpdir.join('file2.txt')
    filepath2.write('')
    filepath2.setmtime(Pendulum(2017, 1, 1).timestamp())
    # file 3: not match time
    filepath3 = tmpdir.join('file3.py')
    filepath3.write('')
    filepath3.setmtime(Pendulum(2018, 1, 1).timestamp())
    # file 4: not match size
    filepath4 = tmpdir.join('file4.py')
    with filepath4.open(mode='wb') as f:
        f.truncate(1025)
    filepath4.setmtime(Pendulum(2017, 1, 1).timestamp())

    worker = Classifier(['*.py'], '.', '.', None,
                        since='2016-12-31', until='2017-01-02',
                        smaller=1024)
    assert worker.match_file(tmpdir, 'file1.py')
    assert not worker.match_file(tmpdir, 'file2.txt')
    assert not worker.match_file(tmpdir, 'file3.py')
    assert not worker.match_file(tmpdir, 'file4.py')


def test_filtered(tmpdir):
    filepath1 = tmpdir.join('file1.py')
    filepath1.write('')
    subdir1 = tmpdir.mkdir('subdir1')
    filepath2 = subdir1.join('file2.py')
    filepath2.write('')
    resultdir = tmpdir.mkdir('result')

    worker = Classifier(['*.py'], tmpdir, resultdir, None)
    filtered1 = set(worker.filtered(recursive=True))
    filtered2 = set(worker.filtered(recursive=False))

    assert filtered1 == {(filepath1, resultdir.join('file1.py'), 'file1.py'),
                         (filepath2, resultdir.join('file2.py'), 'file2.py')}
    assert filtered2 == {(filepath1, resultdir.join('file1.py'), 'file1.py')}


def test_filtered_with_exclude(tmpdir):
    filepath1 = tmpdir.join('file1.py')
    filepath1.write('')
    subdir1 = tmpdir.mkdir('subdir1')
    filepath2 = subdir1.join('file2.py')
    filepath2.write('')
    resultdir = tmpdir.mkdir('result')

    worker = Classifier(['*.py'], tmpdir, resultdir, None, exclude=['subdir?'])
    filtered = set(worker.filtered(recursive=True))

    assert filtered == {(filepath1, resultdir.join('file1.py'), 'file1.py')}


def test_move_file(tmpdir):
    filepath = tmpdir.join('file.py')
    filepath.write('')
    resultdir = tmpdir.mkdir('result')

    with open(tmpdir.join('history.txt'), 'w') as f:
        worker = Classifier(['*.py'], '.', '.', f)
        worker.move_file(filepath, os.path.join(resultdir, 'file.py'))

    assert set(os.listdir(resultdir)) == {'file.py'}


def test_copy_file(tmpdir):
    filepath = tmpdir.join('file.py')
    filepath.write('')
    resultdir = tmpdir.mkdir('result')

    with open(tmpdir.join('history.txt'), 'w') as f:
        worker = Classifier(['*.py'], '.', '.', f)
        worker.copy_file(filepath, os.path.join(resultdir, 'file.py'))

    assert set(os.listdir(resultdir)) == {'file.py'}
    assert set(os.listdir(tmpdir)) == {'result', 'file.py', 'history.txt'}


def test_rename_on_dup(tmpdir):
    filepath1 = tmpdir.join('file.py')
    filepath1.write('')
    subdir = tmpdir.mkdir('subdir')
    filepath2 = subdir.join('file.py')
    filepath2.write('')

    with open(tmpdir.join('history.txt'), 'w') as f:
        worker = Classifier(['*.py'], '.', '.', f)
        worker.rename_on_dup(filepath2, str(tmpdir.join('file.py')), 'file.py')

    assert set(os.listdir(subdir)) == set()
    assert set(os.listdir(tmpdir)) == {'subdir', 'file.py', 'file (2).py',
                                       'history.txt'}


def test_overwrite_on_dup(tmpdir):
    filepath1 = tmpdir.join('file.py')
    filepath1.write('')
    subdir = tmpdir.mkdir('subdir')
    filepath2 = subdir.join('file.py')
    filepath2.write('')

    with open(tmpdir.join('history.txt'), 'w') as f:
        worker = Classifier(['*.py'], '.', '.', f)
        worker.overwrite_on_dup(filepath2, str(tmpdir.join('file.py')), 'file.py')

    assert set(os.listdir(subdir)) == set()
    assert set(os.listdir(tmpdir)) == {'subdir', 'file.py', 'history.txt'}


def test_clean_dirs(tmpdir):
    tmpdir.mkdir('subdir1')
    tmpdir.mkdir('subdir2').mkdir('subdir3')
    tmpdir.join('file.txt').write('')

    worker = Classifier(['*.py'], tmpdir, '.', None)
    worker.clean_dirs()

    assert set(os.listdir(tmpdir)) == {'file.txt'}
