
import requests
import webbrowser

from uuid import uuid4

from alertaclient.auth.token import TokenHandler


def login(endpoint, client_id):
    xsrf_token = str(uuid4())
    redirect_uri = 'http://127.0.0.1:9004'
    url = (
        'https://github.com/login/oauth/authorize?'
        'client_id={client_id}&'
        'redirect_uri={redirect_uri}&'
        'scope=user:email%20read:org&'
        'state={state}&'
        'allow_signup=false'
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
    response = requests.post(endpoint+'/auth/github', json=data, headers={'Content-type': 'application/json'})
    return response.json()
