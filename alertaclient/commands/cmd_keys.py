import json
from datetime import datetime, timedelta

import click
from tabulate import tabulate

from alertaclient.utils import origin


@click.command('keys', short_help='List API keys')
@click.option('--alert', is_flag=True, help='Alert on expiring and expired keys')
@click.option('--maxage', metavar='DAYS', default=7, type=int, help='Max remaining days before alerting')
@click.option('--timeout', metavar='SECONDS', default=86400, type=int, help='Seconds before expired key alerts will be expired')
@click.option('--severity', '-s', metavar='SEVERITY', default='warning', help='Severity for expiring and expired alerts')
@click.pass_obj
def cli(obj, alert, maxage, severity, timeout):
    """List API keys."""
    client = obj['client']

    if obj['output'] == 'json':
        r = client.http.get('/keys')
        click.echo(json.dumps(r['keys'], sort_keys=True, indent=4, ensure_ascii=False))
    else:
        timezone = obj['timezone']
        headers = {
            'id': 'ID', 'key': 'API KEY', 'user': 'USER', 'scopes': 'SCOPES', 'text': 'TEXT',
            'expireTime': 'EXPIRES', 'count': 'COUNT', 'lastUsedTime': 'LAST USED', 'customer': 'CUSTOMER'
        }
        click.echo(tabulate([k.tabular(timezone) for k in client.get_keys()], headers=headers, tablefmt=obj['output']))

    if alert:
        keys = r['keys']
        service = ['Alerta']
        group = 'System'
        environment = 'Production'
        with click.progressbar(keys, label=f'Analysing {len(keys)} keys') as bar:
            for b in bar:
                if b['status'] == 'expired':
                    client.send_alert(
                        resource=b['id'],
                        event='ApiKeyExpired',
                        environment=environment,
                        severity=severity,
                        correlate=['ApiKeyExpired', 'ApiKeyExpiring', 'ApiKeyOK'],
                        service=service,
                        group=group,
                        value='Expired',
                        text=f"Key expired on {b['expireTime']}",
                        origin=origin(),
                        type='apiKeyAlert',
                        timeout=timeout,
                        customer=b['customer']
                    )
                elif b['status'] == 'active':
                    expiration = datetime.fromisoformat(b['expireTime'].split('.')[0])
                    remaining_validity = expiration - datetime.now()
                    if remaining_validity < timedelta(days=maxage):
                        client.send_alert(
                            resource=b['id'],
                            event='ApiKeyExpiring',
                            environment=environment,
                            severity=severity,
                            correlate=['ApiKeyExpired', 'ApiKeyExpiring', 'ApiKeyOK'],
                            service=service,
                            group=group,
                            value=str(remaining_validity),
                            text=f"Key is active and expires on {b['expireTime']}",
                            origin=origin(),
                            type='apiKeyAlert',
                            timeout=timeout,
                            customer=b['customer']
                        )
                    else:
                        client.send_alert(
                            resource=b['id'],
                            event='ApiKeyOK',
                            environment=environment,
                            severity='ok',
                            correlate=['ApiKeyExpired', 'ApiKeyExpiring', 'ApiKeyOK'],
                            service=service,
                            group=group,
                            value=str(remaining_validity),
                            text=f"Key is active and expires on {b['expireTime']}",
                            origin=origin(),
                            type='apiKeyAlert',
                            timeout=timeout,
                            customer=b['customer']
                        )
