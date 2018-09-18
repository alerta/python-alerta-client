
import webbrowser
from uuid import uuid4

from alertaclient.auth.token import TokenHandler


def login(client, username, client_id):
    xsrf_token = str(uuid4())
    redirect_uri = 'http://127.0.0.1:9004'
    url = (
        'https://accounts.google.com/o/oauth2/v2/auth?'
        'scope=email%20profile&'
        'response_type=code&'
        'client_id={client_id}&'
        'redirect_uri={redirect_uri}&'
        'state={state}&'
        'login_hint={username}'
    ).format(
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=xsrf_token,
        username=username
    )

    webbrowser.open(url, new=0, autoraise=True)
    auth = TokenHandler()
    access_token = auth.get_access_token(xsrf_token)

    data = {
        'code': access_token,
        'clientId': client_id,
        'redirectUri': redirect_uri
    }
    return client.token('google', data)
