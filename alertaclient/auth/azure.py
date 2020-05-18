import webbrowser
from uuid import uuid4

from alertaclient.auth.token import TokenHandler


def login(client, azure_tenant, client_id):
    xsrf_token = str(uuid4())
    redirect_uri = 'http://localhost:9004'

    url = (
        'https://login.microsoftonline.com/{azure_tenant}/oauth2/v2.0/authorize?'
        'response_type=code'
        '&client_id={client_id}'
        '&redirect_uri={redirect_uri}'
        '&scope=openid%20profile%20email'
        '&state={state}'
    ).format(
        azure_tenant=azure_tenant,
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
    return client.token('azure', data)
