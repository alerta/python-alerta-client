import click


@click.command('config', short_help='Display remote client config')
@click.pass_obj
def cli(obj):
    """Display client config downloaded from API server."""
    for k, v in obj.items():
        if isinstance(v, list):
            v = ', '.join(v)
        click.echo('{:20}: {}'.format(k, v))
