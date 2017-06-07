import click
from sample.classifier import *


def open_lastrun_file(mode='r'):
    '''Open and return lastrun file.'''

    # path to data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)

    # path to lastrun file
    lastrun_path = os.path.join(data_dir, 'lastrun.txt')
    return open(lastrun_path, mode)


@click.group()
def cli():
    '''Organize a directory by classifying files into different places.'''

    pass


@cli.command()
@click.argument('exprs', nargs=-1)
@click.argument('src', type=click.Path(exists=True))
@click.argument('dst', type=click.Path())
@click.option('--autoclean', '-c', is_flag=True,
              help='Automatically remove empty directories.')
@click.option('--recursive/--no-recursive', '-r/-R', default=True,
              help='Recursively/No-recursively scan directories.')
@click.option('--since',
              help='Oldest modification time.')
@click.option('--until',
              help='Latest modification time.')
@click.option('--larger', type=click.INT,
              help='Minimum size in bytes.')
@click.option('--smaller', type=click.INT,
              help='Maximum size in bytes.')
@click.option('--exclude', '-x', multiple=True,
              help='Glob pattern to exclude directories.')
@click.option('--ask', 'duplicate', flag_value='ask', default=True,
              help='Ask for action on duplicate.')
@click.option('--rename', 'duplicate', flag_value='rename',
              help='Always rename on duplicate.')
@click.option('--overwrite', 'duplicate', flag_value='overwrite',
              help='Always overwrite on duplicate.')
@click.option('--ignore', 'duplicate', flag_value='ignore',
              help='Always ignore on duplicate.')
def manuel(exprs, src, dst, **options):
    '''Manually classify files.'''

    with open_lastrun_file('w') as f:
        worker = Classifier(exprs, src, dst, f, **options)
        worker.classify()


@cli.command()
@click.argument('path', type=click.Path(exists=True))
def auto(path):
    '''Automatically classify files based on a criteria file.'''

    with open_lastrun_file('w') as f:
        worker = AutoClassifier(path, f)
        worker.classify()


@cli.command()
@click.option('--autoclean', '-c', is_flag=True,
              help='Automatically remove empty directories.')
@click.option('--ask', 'duplicate', flag_value='ask', default=True,
              help='Ask for action on duplicate.')
@click.option('--rename', 'duplicate', flag_value='rename',
              help='Always rename on duplicate.')
@click.option('--overwrite', 'duplicate', flag_value='overwrite',
              help='Always overwrite on duplicate.')
@click.option('--ignore', 'duplicate', flag_value='ignore',
              help='Always ignore on duplicate.')
def undo(**options):
    '''Undo the last run of classer.'''

    try:
        with open_lastrun_file('r') as f:
            worker = ReverseClassifier(f, **options)
            worker.classify()
    except FileNotFoundError:
        print('There is no history')
