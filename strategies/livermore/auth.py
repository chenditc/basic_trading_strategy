import hmac
import pytz
import random
import string
import sys
from datetime import datetime
from copy import deepcopy
from hashlib import sha256


def get_sign_content(all_params):
    sign_content = ""
    for (k, v) in sorted(all_params.items()):
        sign_content += v
    return sign_content


def sign(key, secret, params, nonce=None):
    if not nonce:
        nonce = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    ts = str(int(datetime.now(pytz.timezone("Asia/Hong_Kong")).timestamp()))
    sign_data = deepcopy(params)
    sign_data["LM-KEY"] = key
    sign_data["LM-TS"] = ts
    sign_data["LM-NONCE"] = nonce
    sign_str = get_sign_content(sign_data)
    ts_secret = ts + secret
    if sys.version_info.major == 3:
        # py3
        ts_secret = bytes(ts_secret, "utf-8")
        sign_str = bytes(sign_str, "utf-8")
    sign = hmac.new(ts_secret, sign_str, digestmod=sha256).hexdigest()
    return {
        "LM-KEY": key,
        "LM-TS": ts,
        "LM-NONCE": nonce,
        "LM-SIGN": sign,
        "LM-SIGNTYPE": "HMACSHA256",
    }
