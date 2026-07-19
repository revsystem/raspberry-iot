"""SwitchBot API v1.1 からデバイスステータスを取得する。

ref. https://github.com/OpenWonderLabs/SwitchBotAPI
"""

import base64
import hashlib
import hmac
import time
import uuid

import requests

TIMEOUT = 10  # seconds


def get_data(token: str, api_url: str, secret: str) -> dict:
    """デバイスステータス (レスポンスの body) を dict で返す。"""
    nonce = str(uuid.uuid4())
    t = str(int(time.time() * 1000))
    sign = base64.b64encode(
        hmac.new(secret.encode(), f'{token}{t}{nonce}'.encode(), hashlib.sha256).digest()
    ).decode()

    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
        'charset': 'utf8',
        't': t,
        'sign': sign,
        'nonce': nonce,
    }

    response = requests.get(api_url, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()['body']
