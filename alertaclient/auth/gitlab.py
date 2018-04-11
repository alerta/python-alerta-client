
import requests
import webbrowser

from uuid import uuid4

from alertaclient.auth.token import TokenHandler


def login(endpoint, client_id):
    xsrf_token = str(uuid4())
    redirect_uri = 'http://127.0.0.1:9004'
    url = (
        'https://gitlab.com/oauth/authorize?'
        'response_type=code&'
        'client_id={client_id}&'
        'redirect_uri={redirect_uri}&'
        'scope=openid%20api&'
        'state={state}'
    ).format(
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=xsrf_token
    )

    webbrowser.open(url, new=0, autoraise=True)
    auth = TokenHandler()
    access_token = auth.get_access_token(xsrf_token)

    data = {
        "code": access_token,
        "clientId": client_id,
        "redirectUri": redirect_uri
    }
    response = requests.post(endpoint+'/auth/gitlab', json=data, headers={'Content-type': 'application/json'})
    return response.json()
