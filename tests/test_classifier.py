import os
from pendulum import Pendulum
from . import Classifier
from . import open_lastrun_file


def test_match_name():
    with open_lastrun_file('w') as f:
        worker = Classifier(['*.txt', '*.md'], '.', '.', f)

        assert worker.match_name(worker.exprs, 'file.txt')
        assert worker.match_name(worker.exprs, 'file.md')
        assert not worker.match_name(worker.exprs, 'file.py')


def test_match_time(tmpdir):
    # file 1: match
    filepath1 = tmpdir.join('file1.txt')
    filepath1.write('')
    filepath1.setmtime(Pendulum(2017, 1, 1).timestamp())
    # file 2: not match
    filepath2 = tmpdir.join('file2.txt')
    filepath2.write('')
    filepath2.setmtime(Pendulum(2018, 1, 1).timestamp())

    with open_lastrun_file('w') as f:
        worker = Classifier(['*.txt'], tmpdir, tmpdir, f,
                            since='2016-12-31', until='2017-01-02')

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

    with open_lastrun_file('w') as f:
        worker = Classifier(['*.txt'], tmpdir, tmpdir, f,
                            larger=999, smaller=1023)

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

    with open_lastrun_file('w') as f:
        worker = Classifier(['*.py'], tmpdir, tmpdir, f,
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

    with open_lastrun_file('w') as f:
        worker = Classifier(['*.py'], tmpdir, resultdir, f)
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

    with open_lastrun_file('w') as f:
        worker = Classifier(['*.py'], tmpdir, resultdir, f,
                            exclude=['subdir?'])
        filtered = set(worker.filtered(recursive=True))

    assert filtered == {(filepath1, resultdir.join('file1.py'), 'file1.py')}


def test_move_file(tmpdir):
    filepath = tmpdir.join('file.py')
    filepath.write('')
    resultdir = tmpdir.mkdir('result')

    with open_lastrun_file('w') as f:
        worker = Classifier(['*.py'], tmpdir, tmpdir, f)
        worker.move_file(filepath, os.path.join(resultdir, 'file.py'))

    assert set(os.listdir(resultdir)) == {'file.py'}


def test_rename_on_dup(tmpdir):
    filepath1 = tmpdir.join('file1.py')
    filepath1.write('')
    subdir1 = tmpdir.mkdir('subdir1')
    filepath2 = subdir1.join('file1.py')
    filepath2.write('')

    with open_lastrun_file('w') as f:
        worker = Classifier(['*.py'], tmpdir, tmpdir, f)
        worker.rename_on_dup(filepath2, str(tmpdir.join('file1.py')), 'file1.py')

    assert set(os.listdir(subdir1)) == set()
    assert set(os.listdir(tmpdir)) == {'file1.py', 'file1 (2).py', 'subdir1'}


def test_overwrite_on_dup(tmpdir):
    filepath1 = tmpdir.join('file1.py')
    filepath1.write('')
    subdir1 = tmpdir.mkdir('subdir1')
    filepath2 = subdir1.join('file1.py')
    filepath2.write('')

    with open_lastrun_file('w') as f:
        worker = Classifier(['*.py'], tmpdir, tmpdir, f)
        worker.overwrite_on_dup(filepath2, str(tmpdir.join('file1.py')), 'file1.py')

    assert set(os.listdir(subdir1)) == set()
    assert set(os.listdir(tmpdir)) == {'file1.py', 'subdir1'}


def test_move_files(tmpdir):
    filepath1 = tmpdir.join('file1.py')
    filepath1.write('')
    subdir1 = tmpdir.mkdir('subdir1')
    filepath2 = subdir1.join('file2.py')
    filepath2.write('')
    resultdir = tmpdir.mkdir('result')

    with open_lastrun_file('w') as f:
        worker = Classifier(['*.py'], tmpdir, resultdir, f, recursive=False)
        worker.move_files()

    assert set(os.listdir(resultdir)) == {'file1.py'}


def test_clean_dirs(tmpdir):
    tmpdir.mkdir('sub1')
    tmpdir.mkdir('sub2').mkdir('sub3')
    tmpdir.join('file.txt').write('')

    with open_lastrun_file('w') as f:
        worker = Classifier(['*.py'], tmpdir, tmpdir, f)
        worker.clean_dirs()

    assert set(os.listdir(tmpdir)) == {'file.txt'}


def test_classify(tmpdir):
    tmpdir.mkdir('subdir').join('file.txt').write('')
    resultdir = tmpdir.join('result')

    with open_lastrun_file('w') as f:
        worker = Classifier(['*.txt'], tmpdir, resultdir, f,
                            recursive=True, autoclean=True)
        worker.classify()

    assert set(os.listdir(tmpdir)) == {'result'}
    assert set(os.listdir(resultdir)) == {'file.txt'}
