import Crypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA512
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
    def __encrypt(text: str, key: RSA.RsaKey) -> str:
        encryptor = PKCS1_OAEP.new(key, SHA512)
        ciphertext = encryptor.encrypt(text.encode())
        return b64encode(ciphertext).decode()

    @staticmethod
    def __decrypt(text: str, key: RSA.RsaKey) -> str:
        decrypter = PKCS1_OAEP.new(key, SHA512)
        ciphertext = b64decode(text.encode())
        return decrypter.decrypt(ciphertext).decode()

    def get_max_message_length(self) -> int:
        return self.__max_len

    def get_public_key(self) -> Union[str, None]:
        if self.private_key:
            return self.private_key.public_key().export_key().decode()
        return None

    def generate_keys(self, length: int = 2048):
        self.private_key = RSA.generate(length)
        self.__max_len = int(length / 8 - (2 * 512 / 8) - 2)

    def encrypt(self, text: str, *, key: Union[RSA.RsaKey, str] = None, chunk_length: int = None, separator: str = None, chunk_func=None) -> str:
        if not key:
            key = self.private_key.public_key()
        elif type(key) is str:
            try:
                key = RSA.import_key(key)
            except (ValueError, IndexError, TypeError):
                key = None

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
                out_text += self.__encrypt(chunk, key)
            else:
                out_text += b64encode(text.encode()).decode()
            out_text += separator

        return out_text[:-2]

    def decrypt(self, text: str, *, key: Union[RSA.RsaKey, str] = None, separator: str = None):
        if not key:
            key = self.private_key
        elif type(key) is str:
            try:
                key = RSA.import_key(key)
            except (ValueError, IndexError, TypeError):
                key = None

        if not key:
            raise Exception("Keys are not generated, neither key was provided to function or it was incorrect!")

        if not separator:
            separator = self.separator

        out = ""
        for chunk in (chunk for chunk in text.split(separator)):
            try:
                out += self.__decrypt(chunk, key)
            except ValueError:
                out += b64decode(chunk.encode()).decode()

        return out
