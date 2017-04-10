import click
from sample.classifier import Classifier


@click.group(invoke_without_command=True)
@click.argument('expr')
@click.argument('src', type=click.Path(exists=True))
@click.argument('dst', type=click.Path())
@click.option('--autoclean', '-c', is_flag=True)
def cli(expr, src, dst, autoclean):
    worker = Classifier(expr, src, dst, autoclean=autoclean)
    worker.classify()
