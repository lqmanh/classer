import os
import hjson as json
from . import AutoClassifier


def test_load_criteria(tmpdir):
    data = {'hello': 'world'}
    filepath = tmpdir.join('file.json')
    filepath.write(json.dumps(data))

    worker = AutoClassifier(filepath)  # load_criteria is executed when initialized
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

    worker = AutoClassifier('')
    # use criteria directly instead of reading from file
    worker.criteria = criteria
    worker.classify()

    assert os.listdir(tmpdir.join('Documents')) == ['file.txt']
    assert os.listdir(tmpdir.join('Music')) == ['file.mp3']
    assert os.listdir(tmpdir.join('.ignore')) == ['file.md']
