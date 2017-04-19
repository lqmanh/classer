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
@click.option('--exclude')
def cli(expr, src, dst, **options):
    worker = Classifier(expr, src, dst, **options)
    worker.classify()
