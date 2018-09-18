
import click


@click.command('config', short_help='Display remote client config')
@click.pass_obj
def cli(obj):
    """Display client config downloaded from API server."""
    client = obj['client']
    config = client.config()
    for k, v in config.items():
        if isinstance(v, list):
            v = ', '.join(v)
        click.echo('{:20}: {}'.format(k, v))
