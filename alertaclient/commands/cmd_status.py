
import click

from tabulate import tabulate


@click.command('status', short_help='display status and metrics')
@click.pass_obj
@click.pass_context
def cli(ctx, obj):
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
        } for m in metrics], headers=headers, tablefmt=ctx.parent.params['output_format']
    ))
