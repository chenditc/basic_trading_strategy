import requests
from .auth import sign
from .exception import HTTPException
from .constant import TRADE_HOST, TEST_TRADE_HOST


class HttpClient(object):

    def __init__(self, key, secret, test):
        self.key = key
        self.secret = secret
        self.test = test
        self.session = requests.session()

    def get_headers(self, params):
        headers = sign(self.key, self.secret, params, nonce=None)
        return headers

    def get(self, path, params):
        if self.test:
            url = TEST_TRADE_HOST + path
        else:
            url = TRADE_HOST + path
        resp = self.session.get(url, params=params, headers=self.get_headers(params), timeout=10)
        if resp.status_code == 200:
            resp_json = resp.json()
            return resp_json
        else:
            raise HTTPException("status code = {status_code}".format(
                status_code=resp.status_code,
            ))

    def post(self, path, data):
        if self.test:
            url = TEST_TRADE_HOST + path
        else:
            url = TRADE_HOST + path

        resp = self.session.post(url, data=data, headers=self.get_headers(data), timeout=10)
        if resp.status_code == 200:
            resp_json = resp.json()
            return resp_json
        else:
            raise HTTPException("status code = {status_code}".format(
                status_code=resp.status_code,
            ))
