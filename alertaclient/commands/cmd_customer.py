import sys

import click


@click.command('customer', short_help='Add customer lookup')
@click.option('--customer', help='customer name')
@click.option('--org', '--group', '--domain', '--role', 'match', help='Used to lookup customer')
@click.option('--delete', '-D', metavar='ID', help='Delete customer lookup using ID')
@click.pass_obj
def cli(obj, customer, match, delete):
    """Add group/org/domain/role-to-customer or delete lookup entry."""
    client = obj['client']
    if delete:
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
