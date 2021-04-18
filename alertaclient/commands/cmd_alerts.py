import json

import click
from tabulate import tabulate


@click.command('alerts', short_help='List environments, services, groups and tags')
@click.option('--environments', '-E', is_flag=True, help='List alert environments.')
@click.option('--services', '-S', is_flag=True, help='List alert services.')
@click.option('--groups', '-g', is_flag=True, help='List alert groups.')
@click.option('--tags', '-T', is_flag=True, help='List alert tags.')
@click.pass_obj
def cli(obj, environments, services, groups, tags):
    """List alert environments, services, groups and tags."""

    client = obj['client']

    if environments:
        if obj['output'] == 'json':
            r = client.http.get('/environments')
            click.echo(json.dumps(r['environments'], sort_keys=True, indent=4, ensure_ascii=False))
        else:
            headers = {'environment': 'ENVIRONMENT', 'count': 'COUNT', 'severityCounts': 'SEVERITY COUNTS', 'statusCounts': 'STATUS COUNTS'}
            click.echo(tabulate(client.get_environments(), headers=headers, tablefmt=obj['output']))
    elif services:
        if obj['output'] == 'json':
            r = client.http.get('/services')
            click.echo(json.dumps(r['services'], sort_keys=True, indent=4, ensure_ascii=False))
        else:
            headers = {'environment': 'ENVIRONMENT', 'service': 'SERVICE', 'count': 'COUNT', 'severityCounts': 'SEVERITY COUNTS', 'statusCounts': 'STATUS COUNTS'}
            click.echo(tabulate(client.get_services(), headers=headers, tablefmt=obj['output']))
    elif groups:
        if obj['output'] == 'json':
            r = client.http.get('/alerts/groups')
            click.echo(json.dumps(r['groups'], sort_keys=True, indent=4, ensure_ascii=False))
        else:
            headers = {'environment': 'ENVIRONMENT', 'group': 'GROUP', 'count': 'COUNT', 'severityCounts': 'SEVERITY COUNTS', 'statusCounts': 'STATUS COUNTS'}
            click.echo(tabulate(client.get_groups(), headers=headers, tablefmt=obj['output']))
    elif tags:
        if obj['output'] == 'json':
            r = client.http.get('/alerts/tags')
            click.echo(json.dumps(r['tags'], sort_keys=True, indent=4, ensure_ascii=False))
        else:
            headers = {'environment': 'ENVIRONMENT', 'tag': 'TAG', 'count': 'COUNT', 'severityCounts': 'SEVERITY COUNTS', 'statusCounts': 'STATUS COUNTS'}
            click.echo(tabulate(client.get_tags(), headers=headers, tablefmt=obj['output']))
    else:
        raise click.UsageError('Must choose an alert attribute to list.')
