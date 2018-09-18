
import webbrowser
from uuid import uuid4

from alertaclient.auth.token import TokenHandler


def login(client, gitlab_url, client_id):
    xsrf_token = str(uuid4())
    redirect_uri = 'http://127.0.0.1:9004'
    url = (
        '{gitlab_url}/oauth/authorize?'
        'response_type=code&'
        'client_id={client_id}&'
        'redirect_uri={redirect_uri}&'
        'scope=openid&'
        'state={state}'
    ).format(
        gitlab_url=gitlab_url,
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=xsrf_token
    )

    webbrowser.open(url, new=0, autoraise=True)
    auth = TokenHandler()
    access_token = auth.get_access_token(xsrf_token)

    data = {
        'code': access_token,
        'clientId': client_id,
        'redirectUri': redirect_uri
    }
    return client.token('gitlab', data)
