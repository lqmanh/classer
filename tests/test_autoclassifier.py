import os
import hjson as json
from . import *


def test_load_criteria(tmpdir):
    data = {'hello': 'world'}
    filepath = tmpdir.join('file.json')
    filepath.write(json.dumps(data))

    with open_lastrun_file('w') as f:
        worker = AutoClassifier(filepath, f)

        assert worker.criteria == data


def test_classify(tmpdir):
    criteria = {
        'targets': {
            'Documents': ['*.txt', '*.md'],
            'Music': ['*mp3']
        },
        'src': tmpdir,
        'dst': tmpdir,
        'autoclean': True,
        'recursive': True,
        'since': None,
        'until': None,
        'larger': None,
        'smaller': None,
        'exclusions': {
            'Documents': ['.ignore']
        }
    }

    filepath1 = tmpdir.join('file.txt')
    filepath1.write('')
    ignore = tmpdir.mkdir('.ignore')
    filepath2 = ignore.join('file.mp3')
    filepath2.write('')
    filepath3 = ignore.join('file.md')
    filepath3.write('')

    with open_lastrun_file('w') as f:
        worker = AutoClassifier('no_exist.json', f)
        # use criteria dict directly instead of reading from file
        worker.criteria = criteria
        worker.classify()

    assert set(os.listdir(tmpdir.join('Documents'))) == {'file.txt'}
    assert set(os.listdir(tmpdir.join('Music'))) == {'file.mp3'}
    assert set(os.listdir(tmpdir.join('.ignore'))) == {'file.md'}
