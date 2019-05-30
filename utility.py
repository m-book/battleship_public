import json
from Crypto import Random
from Crypto.Cipher import AES
import base64, hashlib
import netifaces
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import random, string
from Crypto.Hash import SHA
from Crypto import Random as c_random


def make_send_data(user_id, status, data):
    body = {'user_id': user_id, 'status': status, 'data': data}
    body_json = json.dumps(body).encode('utf-8')
    return body_json


def receive_data(received_data):
    data_dict = json.loads(received_data.decode('utf-8'))
    return data_dict['user_id'], data_dict['status'], data_dict['data']


def get_own_address(port, upnp=None):
    return 'localhost'
    address = get_sglobal_address(upnp, port)
    if address is None:
        address = get_local_address()
    if address is None:
        address = 'localhost'
    print(address)
    return address


def get_local_address():
    for iface_name in netifaces.interfaces():
        iface_data = netifaces.ifaddresses(iface_name)
        if iface_data.get(netifaces.AF_INET) is None:
            continue
        address_dict = iface_data.get(netifaces.AF_INET)[0]
        if address_dict['addr'] != '127.0.0.1':
            print('address is {0}'.format(address_dict['addr']))
            return address_dict['addr']
    return None


def get_global_address(upnp, port):
    if upnp is None:
        return None
    try:
        upnp.confirm_wan()
        upnp.confirm_mapping()
        local_address = get_local_address()
        if local_address is None:
            return None
        return upnp.get_public_address(local_address, port)
    except:
        return None


class AESCipher:
    def __init__(self, key=None, block_size=32):
        if key is None:
            key = str(''.join([random.choice(string.ascii_letters + string.digits) for i in range(128)]))
        self.bs = block_size
        if len(key) >= len(str(block_size)):
            self.key = key[:block_size]
        else:
            self.key = self._pad(key)

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


class RSACipher:
    def __init__(self, rsa_length):
        # 鍵ペアの作成
        rsa = RSA.generate(rsa_length)
        self.random_password = str(''.join([random.choice(string.ascii_letters + string.digits) for i in range(128)]))

        # 秘密鍵の作成
        self.private_pem = rsa.exportKey(format='PEM', passphrase=self.random_password)

        # 公開鍵の作成
        self.public_pem = rsa.publickey().exportKey()

    def encrypt(self, plain_text, pem=None):
        public_pem = pem
        if public_pem is None:
            public_pem = self.public_pem
        public_key = RSA.importKey(public_pem)
        cipher = PKCS1_v1_5.new(public_key)
        cipher_text = cipher.encrypt(plain_text.encode('utf-8'))
        cipher_text = base64.b64encode(cipher_text)
        return cipher_text

    def decrypt(self, encrypted):
        encrypted = base64.b64decode(encrypted)
        password = self.random_password
        private_key = RSA.importKey(self.private_pem, passphrase=password)
        dsize = SHA.digest_size
        sentinel = c_random.new().read(15+dsize)
        cipher = PKCS1_v1_5.new(private_key)
        decoded = cipher.decrypt(encrypted, sentinel)
        return decoded.decode('utf-8')
