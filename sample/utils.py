import os


def open_lastrun_file(mode='r'):
    '''Open and return lastrun file.'''

    # path to data directory
    data_dir = os.path.expanduser('~/.local/share/classer/')
    os.makedirs(data_dir, exist_ok=True)

    # path to lastrun file
    lastrun_path = os.path.join(data_dir, 'lastrun.txt')
    return open(lastrun_path, mode)
