import click
from sample.classifier import Classifier


@click.group(invoke_without_command=True)
@click.argument('expr')
@click.argument('src', type=click.Path(exists=True))
@click.argument('dst', type=click.Path())
def cli(expr, src, dst):
    worker = Classifier(expr, src, dst)
    worker.classify()
