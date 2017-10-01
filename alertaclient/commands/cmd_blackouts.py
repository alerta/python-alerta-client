

import click

from tabulate import tabulate


@click.command('blackouts', short_help='list alert suppressions')
@click.option('--purge', is_flag=True)
@click.pass_obj
@click.pass_context
def cli(ctx, obj, purge):
    """List alert suppressions."""
    client = obj['client']
    timezone = obj['timezone']
    headers = {
        'id': 'ID', 'priority': 'P', 'environment': 'ENVIRONMENT', 'service': 'SERVICE', 'resource': 'RESOURCE',
        'event': 'EVENT', 'group': 'GROUP', 'tags': 'TAGS', 'startTime': 'START', 'endTime': 'END',
        'duration': 'DURATION', 'status': 'STATUS', 'remaining': 'REMAINING', 'customer': 'CUSTOMER'
    }
    blackouts = client.get_blackouts()
    click.echo(tabulate([b.serialize(timezone) for b in blackouts], headers=headers, tablefmt=ctx.parent.params['output_format']))

    expired = [b for b in blackouts if b.status == 'expired']
    if purge:
        with click.progressbar(expired, label='Purging {} blackouts'.format(len(expired))) as bar:
            for b in bar:
                client.delete_blackout(b.id)
