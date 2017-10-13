import click

from .cmd_key import cli as revoke


@click.command('revoke', short_help='Revoke API key')
@click.option('--api-key', '-K', required=True, help='API Key or UUID')
@click.pass_context
def cli(ctx, api_key):
    ctx.invoke(revoke, delete=api_key)
