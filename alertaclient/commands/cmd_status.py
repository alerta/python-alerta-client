import click
from tabulate import tabulate


@click.command('status', short_help='Display status and metrics')
@click.pass_obj
def cli(obj):
    """Display API server switch status and usage metrics."""
    client = obj['client']
    metrics = client.mgmt_status()['metrics']
    headers = {'title': 'METRIC', 'type': 'TYPE', 'name': 'NAME', 'value': 'VALUE', 'average': 'AVERAGE'}
    click.echo(tabulate([{
        'title': m['title'],
        'type': m['type'],
        'name': '{}.{}'.format(m['group'], m['name']),
        'value': m.get('value', None) or m.get('count', 0),
        'average': int(m['totalTime']) * 1.0 / int(m['count']) if m['type'] == 'timer' else None
    } for m in metrics], headers=headers, tablefmt=obj['output']))
