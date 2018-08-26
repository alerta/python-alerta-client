import sys

import click


@click.command('blackout', short_help='Suppress alerts')
@click.option('--environment', '-E', metavar='ENVIRONMENT', help='Environment eg. Production, Development')
@click.option('--service', '-S', metavar='SERVICE', multiple=True, help='List of affected services eg. app name, Web, Network, Storage, Database, Security')
@click.option('--resource', '-r', metavar='RESOURCE', help='Resource under alarm')
@click.option('--event', '-e', metavar='EVENT', help='Event name')
@click.option('--group', '-g', metavar='GROUP', help='Group event by type eg. OS, Performance')
@click.option('--tag', '-T', 'tags', multiple=True, metavar='TAG', help='List of tags eg. London, os:linux, AWS/EC2')
@click.option('--customer', metavar='STRING', help='Customer (Admin only)')
@click.option('--start', metavar='DATETIME', help='Start time in ISO8601 eg. 2018-02-01T12:00:00.000Z')
@click.option('--duration', metavar='SECONDS', type=int, help='Blackout period in seconds')
@click.option('--text', help='Reason for blackout')
@click.option('--delete', '-D', help='Delete blackout using ID')
@click.pass_obj
def cli(obj, environment, service, resource, event, group, tags, customer, start, duration, text, delete):
    """Suppress alerts for specified duration based on alert attributes."""
    client = obj['client']
    if delete:
        client.delete_blackout(delete)
    else:
        if not environment:
            raise click.UsageError('Missing option "--environment" / "-E".')
        try:
            blackout = client.create_blackout(
                environment=environment,
                service=service,
                resource=resource,
                event=event,
                group=group,
                tags=tags,
                customer=customer,
                start=start,
                duration=duration,
                text=text
            )
        except Exception as e:
            click.echo('ERROR: {}'.format(e))
            sys.exit(1)
        click.echo(blackout.id)
