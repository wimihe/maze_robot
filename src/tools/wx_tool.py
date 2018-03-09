#coding:utf-8
#Created by weimi on 2018/3/9.

from src import settings
from . import network_tool

def code_to_session_key_openid(code):
    url = 'https://api.weixin.qq.com/sns/' \
          'jscode2session?appid=%s&secret=%s' \
          '&js_code=%s&grant_type=authorization_code' % (settings.APPID, settings.APPSECRET, code)
    res = network_tool.get(url=url)
    if res.status_code == 200:
        return res.json()
    return None

class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        import base64
        import json

        from Crypto.Cipher import AES
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

        json_b = self._unpad(cipher.decrypt(encryptedData))
        json_str = json_b.decode('utf-8')
        decrypted = json.loads(json_str)

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

def get_userinfo(code, encryptedData, iv):
    data = code_to_session_key_openid(code)
    if not data:
        return None
    session_key = data['session_key']
    # openid = data['openid']
    obj = WXBizDataCrypt(settings.APPID, session_key)
    try:
        userinfo = obj.decrypt(encryptedData=encryptedData, iv=iv)
        userinfo.update(data)
        return userinfo
    except Exception as e:
        print(e)
        return None