#!/usr/bin/env python

import logging

import requests

ALERTA_URL = 'http://localhost:8080'

LOG = logging.getLogger()


def main():

    try:
        r = requests.get(ALERTA_URL + '/alerts?status=open')
        print(r)
        if r.status_code == requests.codes.ok:
            alerta_obj = r.json()
            print(alerta_obj)
        else:
            LOG.error('error status code while fetching alerts: %d', r.status_code)
            r.raise_for_status()
    except Exception as e:
        LOG.info('Could not establish connection to Alerta: %s', e)

    alerts_to_resend = alerta_obj['alerts']
    # for now just want to resend everything to check if code works
    for each_alert in alerts_to_resend:
        print(each_alert)
        print(type(each_alert))

        try:
            myheaders = {}
            myheaders['Content-type'] = 'application/json'
            r = requests.post(ALERTA_URL + '/api/alert', data=each_alert, headers=myheaders)
            if r.status_code == requests.codes.ok:
                alerta_obj = r.json()
                print(alerta_obj)
            else:
                LOG.error('error status code while post call: %d', r.status_code)
                r.raise_for_status()
        except Exception as e:
            print(e)


main()
