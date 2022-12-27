from math import log
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from typing import Optional, Union
from base64 import b64encode, b64decode


class Cipher:
    def __init__(self, separator: str = "@@", generate_keys: bool = True):
        self.private_key: Optional[RSA.RsaKey] = None
        self.separator: str = separator
        self.__max_len: Optional[int] = None
        if generate_keys:
            self.generate_keys()

    @staticmethod
    def __import_key(key: Union[str, RSA.RsaKey, None], default_key: RSA.RsaKey) -> Union[RSA.RsaKey, None]:
        if not key:
            return default_key
        elif type(key) is str:
            try:
                return RSA.import_key(key)
            except (ValueError, IndexError, TypeError):
                raise Exception("Invalid PEM key!")

    @staticmethod
    def __encrypt(key: RSA.RsaKey, text: str) -> str:
        encryptor = PKCS1_OAEP.new(key, SHA256)
        ciphertext = encryptor.encrypt(text.encode())
        return b64encode(ciphertext).decode('utf-8')

    @staticmethod
    def __decrypt(key: RSA.RsaKey, encoded: str) -> str:
        decrypter = PKCS1_OAEP.new(key, SHA256)
        ciphertext = b64decode(encoded)
        return decrypter.decrypt(ciphertext).decode('utf-8')

    def generate_keys(self, length: int = 2048):
        if log(length, 2) % 1 != 0 or length < 512 or length > 4096:
            raise Exception("Key length must be power of two between 512 and 4096!")
        self.private_key = RSA.generate(length)
        self.__max_len = int(length / 8 - (2 * 256 / 8) - 2)

    def get_max_message_length(self) -> int:
        return self.__max_len

    def get_public_key(self) -> Union[str, None]:
        if self.private_key:
            return self.private_key.public_key().export_key().decode('utf-8')
        return None

    def encrypt(self, text: str, *, key: Union[RSA.RsaKey, str] = None, chunk_length: int = None, separator: str = None, chunk_func=None) -> str:
        key = self.__import_key(key, self.private_key.public_key() if self.private_key else None)

        if not key:
            raise Exception("Keys are not generated, neither key was provided to function or it was incorrect!")

        if not chunk_length:
            chunk_length = self.__max_len

        if not separator:
            separator = self.separator

        if not chunk_func:
            def chunk_func(to_split, length) -> (str, bool):
                return [(to_split[i:i+length], True) for i in range(0, len(to_split), length)]

        chunks = chunk_func(text, chunk_length)
        out_text = ""
        for chunk, encrypt in chunks:
            if encrypt:
                out_text += self.__encrypt(key, chunk)
            else:
                out_text += b64encode(text.encode()).decode('utf-8')
            out_text += separator

        return out_text[:-2]

    def decrypt(self, text: str, *, key: Union[RSA.RsaKey, str] = None, separator: str = None):
        key = self.__import_key(key, self.private_key if self.private_key else None)

        if not key:
            raise Exception("Keys are not generated, neither key was provided to function or it was incorrect!")

        if not separator:
            separator = self.separator

        out = ""
        for chunk in (chunk for chunk in text.split(separator)):
            try:
                out += self.__decrypt(key, chunk)
            except ValueError:
                out += b64decode(chunk.encode()).decode('utf-8')

        return out
