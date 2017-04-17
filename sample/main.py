import click
from sample.classifier import Classifier


@click.command()
@click.argument('expr')
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
@click.option('--larger', type=click.INT)
@click.option('--smaller', type=click.INT)
def cli(expr, src, dst, autoclean, recursive, since, until, larger, smaller):
    worker = Classifier(expr, src, dst, autoclean=autoclean,
                        recursive=recursive, since=since, until=until,
                        larger=larger, smaller=smaller)
    worker.classify()
