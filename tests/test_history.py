from . import *


def test_update(tmpdir):
    filepath = tmpdir.join('file.txt')
    filepath.write('')

    history = History(tmpdir)
    history.update()

    assert history.entries == [filepath]


def test_get():
    history = History()
    # the same as the one built with update method
    history.entries = ['file1.txt', 'file2.txt']

    assert list(history.entries) == ['file1.txt', 'file2.txt']


def test_remove(tmpdir):
    filepath1 = tmpdir.join('file1.txt')
    filepath1.write('')
    filepath2 = tmpdir.join('file2.txt')
    filepath2.write('')
    filepath3 = tmpdir.join('file3.txt')
    filepath3.write('')

    history = History(tmpdir)
    # the same as the one built with update method
    history.entries = [filepath1, filepath2, filepath3]
    history.remove(2)

    assert history.entries == [filepath3]


def test_clear(tmpdir):
    filepath1 = tmpdir.join('file1.txt')
    filepath1.write('')
    filepath2 = tmpdir.join('file2.txt')
    filepath2.write('')
    filepath3 = tmpdir.join('file3.txt')
    filepath3.write('')

    history = History(tmpdir)
    # the same as the one built with update method
    history.entries = [filepath1, filepath2, filepath3]
    history.clear()

    assert history.entries == []
