import base64
from Crypto.Cipher import AES


class MessageEncryption:
    secret_key = b'1234567890123456'
    cipher = AES.new(secret_key, AES.MODE_ECB)

    @staticmethod
    def encrypt(plaintext):
        return base64.b64encode(cipher.encrypt(plaintext))

    def decrypt(self, encrypted_text):
        return base64.b64encode(cipher.decrypt(encrypted_text))


if __name__ == "__main__":

    secret_key = b'1234567890123456'
    msg_text = b'test some plain text here'.rjust(32)

    cipher = AES.new(secret_key, AES.MODE_ECB)
    encoded = base64.b64encode(cipher.encrypt(msg_text))
    decoded = cipher.decrypt(base64.b64decode(encoded))

    print(encoded)
    print(decoded)
