import requests_mock

from src.modules.discovery.apiserver import ApiServer, ApiServerDiscovery, ApiServerWithServiceAccountToken
from src.core.events.types import Event
from src.core.events import handler

def test_ApiServer():

    with requests_mock.Mocker() as m:
        m.get('https://mockOther:443', text='elephant')
        m.get('https://mockKubernetes:443', text='{"code":403}')

        e = Event()
        e.port = 443
        e.host = 'mockOther'

        a = ApiServerDiscovery(e)
        a.execute()
        
        e.host = 'mockKubernetes'
        a.execute()

def test_ApiServerWithServiceAccountToken():
    with requests_mock.Mocker() as m:
        m.get('https://mockKubernetes:443', text='{"code":403}')

        e = Event()
        e.port = 443
        e.host = 'mockKubernetes'
        e.auth_token = "very_secret"

        a = ApiServerDiscovery(e)
        a.execute()

# We should only generate an ApiServer event for a response that looks like it came from a Kubernetes node
@handler.subscribe(ApiServer)
class testApiServer(object):
    def __init__(self, event):
        assert event.host == 'mockKubernetes'

@handler.subscribe(ApiServerWithServiceAccountToken)
class testApiServerWithServiceAccountToken(object):
    def __init__(self, event):
        assert event.host == 'mockKubernetes'
        assert event.auth_token == "very_secret"
