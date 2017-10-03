import sys

import click


@click.command('customer', short_help='Add customer lookup')
@click.option('--customer', help='customer name')
@click.option('--org', '--group', '--domain', '--role', 'match', help='used to lookup customer')
@click.option('--delete', '-D', metavar='ID', help='delete customer')
@click.pass_obj
def cli(obj, customer, match, delete):
    """Add group/org/domain/role-to-customer or delete lookup entry."""
    client = obj['client']
    if delete:
        if customer or match:
            raise click.UsageError('Option "--delete" is mutually exclusive.')
        client.delete_customer(delete)
    else:
        if not customer:
            raise click.UsageError('Missing option "--customer".')
        if not match:
            raise click.UsageError('Missing option "--org" / "--group" / "--domain" / "--role".')
        try:
            customer = client.create_customer(customer, match)
        except Exception as e:
            click.echo('ERROR: {}'.format(e))
            sys.exit(1)
        click.echo(customer.id)
