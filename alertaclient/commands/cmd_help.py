
import click


@click.command('help', short_help='Show this help')
@click.pass_context
def cli(ctx):
    click.echo(ctx.parent.get_help())
