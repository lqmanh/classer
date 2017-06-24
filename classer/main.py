import click
from classer.classifiers import *
from classer.history import History


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

    history = History()

    with open(history.new(), 'w') as f:
        worker = Classifier(exprs, src, dst, f, **options)
        worker.classify()


@cli.command()
@click.argument('path', type=click.Path(exists=True))
def auto(path):
    '''Automatically classify files based on a criteria file.'''

    history = History()

    with open(history.new(), 'w') as f:
        worker = AutoClassifier(path, f)
        worker.classify()


@cli.command()
@click.otion('--n', default=1)
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

    history = History()
    history.update()
    entries = list(history.get())

    for i in range(options.pop(n)):
        try:
            with open(entries[-i - 1]) as f:
                worker = ReverseClassifier(f, **options)
                worker.classify()
        except IndexError:
            return


@cli.command()
@click.option('--n', default=0)
@click.option('--remove', default=1)
@click.option('--clear', '-c', is_flag=True)
def histoire(**options):
    history = History()
    history.update()

    if options.get('remove'):
        history.remove(options['remove'])
    elif options.get('clear'):
        history.clear()
    else:
        history.print(options.get('n'))
