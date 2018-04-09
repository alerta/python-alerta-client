import click


@click.command('housekeeping', short_help='Expired and clears old alerts.')
@click.option('--expired', metavar='EXPIRED_DELETE_HOURS', required=False,
              help='Delete expired/closed alertas after this many hours.')
@click.option('--info', metavar='INFO_DELETE_HOURS', required=False,
              help='Delete informational alerta after this many hours.')
@click.pass_obj
def cli(obj, expired=None, info=None):
    """Trigger the expiration and deletion of alerts."""
    client = obj['client']
    client.housekeeping(expired_delete_hours=expired, info_delete_hours=info)
