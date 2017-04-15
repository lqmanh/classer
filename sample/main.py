import click
from sample.classifier import Classifier


@click.command()
@click.argument('expr')
@click.argument('src', type=click.Path(exists=True))
@click.argument('dst', type=click.Path())
@click.option('--autoclean', '-c', is_flag=True)
@click.option('--recursive/--no-recursive', '-r/-R', default=True)
@click.option('--since')
@click.option('--until')
def cli(expr, src, dst, autoclean, recursive, since, until):
    worker = Classifier(expr, src, dst, autoclean=autoclean,
                        recursive=recursive, since=since, until=until)
    worker.classify()
