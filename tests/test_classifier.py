import os
from pendulum import Pendulum
from . import Classifier


def test_match_name():
    worker = Classifier(['*.txt', '*.md'], '.', '.')

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

    worker = Classifier(['*.txt'], tmpdir, tmpdir,
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

    worker = Classifier(['*.txt'], tmpdir, tmpdir,
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

    worker = Classifier(['*.py'], tmpdir, tmpdir,
                        since='2016-12-31', until='2017-01-02', smaller=1024)

    assert worker.match_file(tmpdir, 'file1.py')
    assert not worker.match_file(tmpdir, 'file2.txt')
    assert not worker.match_file(tmpdir, 'file3.py')
    assert not worker.match_file(tmpdir, 'file4.py')


def test_filtered_files(tmpdir):
    filepath1 = tmpdir.join('file1.py')
    filepath1.write('')
    subdir1 = tmpdir.mkdir('subdir1')
    filepath2 = subdir1.join('file2.py')
    filepath2.write('')
    resultdir = tmpdir.mkdir('result')

    worker = Classifier(['*.py'], tmpdir, resultdir)
    filtered1 = list(worker.filtered_files(recursive=True))
    filtered2 = list(worker.filtered_files(recursive=False))

    assert filtered1 == [(filepath1, resultdir.join('file1.py')),
                         (filepath2, resultdir.join('file2.py'))]
    assert filtered2 == [(filepath1, resultdir.join('file1.py'))]


def test_filtered_files_with_exclude(tmpdir):
    filepath1 = tmpdir.join('file1.py')
    filepath1.write('')
    subdir1 = tmpdir.mkdir('subdir1')
    filepath2 = subdir1.join('file2.py')
    filepath2.write('')
    resultdir = tmpdir.mkdir('result')

    worker = Classifier(['*.py'], tmpdir, resultdir, exclude=['subdir?'])
    filtered = list(worker.filtered_files(recursive=True))

    assert filtered == [(filepath1, resultdir.join('file1.py'))]


def test_move_files(tmpdir):
    filepath1 = tmpdir.join('file1.py')
    filepath1.write('')
    subdir1 = tmpdir.mkdir('subdir1')
    filepath2 = subdir1.join('file2.py')
    filepath2.write('')
    resultdir = tmpdir.mkdir('result')

    worker = Classifier(['*.py'], tmpdir, resultdir, recursive=False)
    worker.move_files()

    assert os.listdir(resultdir) == ['file1.py']


def test_clean_dirs(tmpdir):
    tmpdir.mkdir('sub1')
    tmpdir.mkdir('sub2').mkdir('sub3')
    tmpdir.join('file.txt').write('')

    worker = Classifier(['*.py'], tmpdir, tmpdir)
    worker.clean_dirs()

    assert os.listdir(tmpdir) == ['file.txt']


def test_classify(tmpdir):
    tmpdir.mkdir('subdir').join('file.txt').write('')
    resultdir = tmpdir.join('result')

    worker = Classifier(['*.txt'], tmpdir, resultdir,
                        recursive=True, autoclean=True)
    worker.classify()

    assert os.listdir(tmpdir) == ['result']
    assert os.listdir(resultdir) == ['file.txt']
