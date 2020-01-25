import click


@click.command('whoami', short_help='Display current logged in user')
@click.option('--show-userinfo', '-u', is_flag=True, help='Display userinfo')
@click.pass_obj
def cli(obj, show_userinfo):
    """Display logged in user or full userinfo."""
    client = obj['client']
    userinfo = client.userinfo()
    if show_userinfo:
        for k, v in userinfo.items():
            if isinstance(v, list):
                v = ', '.join(v)
            click.echo('{:20}: {}'.format(k, v))
    else:
        click.echo(userinfo['preferred_username'])
