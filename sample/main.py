import click
from sample.classifier import Classifier, AutoClassifier


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
def manuel(exprs, src, dst, **options):
    '''Manually classify files.'''

    worker = Classifier(exprs, src, dst, **options)
    worker.classify()


@cli.command()
@click.argument('path', type=click.Path(exists=True))
def auto(path):
    '''Automatically classify files based on a criteria file.'''

    worker = AutoClassifier(path)
    worker.classify()
