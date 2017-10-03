import sys

import click


@click.command('blackout', short_help='Suppress alerts')
@click.option('--environment', '-E', metavar='ENVIRONMENT')
@click.option('--service', '-S', metavar='SERVICE', multiple=True)
@click.option('--resource', '-r', metavar='RESOURCE')
@click.option('--event', '-e', metavar='EVENT')
@click.option('--group', '-g', metavar='GROUP')
@click.option('--tag', '-T', 'tags', metavar='TAG', multiple=True)
@click.option('--start', metavar='DATETIME')
@click.option('--duration', metavar='EXPIRES')
@click.option('--delete', '-D', help='Delete blackout using ID')
@click.pass_obj
def cli(obj, environment, service, resource, event, group, tags, start, duration, delete):
    """Suppress alerts for specified duration based on alert attributes."""
    client = obj['client']
    if delete:
        if environment or service or resource or event or group or tags or start or duration:
            raise click.UsageError('Option "--delete" is mutually exclusive.')
        client.delete_blackout(delete)
    else:
        if not environment:
            raise click.UsageError('Missing option "--environment" / "-E".')
        try:
            blackout = client.create_blackout(environment, service, resource, event, group, tags, start, duration)
        except Exception as e:
            click.echo('ERROR: {}'.format(e))
            sys.exit(1)
        click.echo(blackout.id)
