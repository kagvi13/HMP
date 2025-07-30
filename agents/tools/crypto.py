# tools/crypto.py

from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import os
import base64

backend = default_backend()

# ========== 🔐 RSA KEYS ==========

def generate_rsa_key_pair(key_size=2048):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=backend
    )
    public_key = private_key.public_key()
    return private_key, public_key

# ========== 🌀 ED25519 KEYS ==========

def generate_ed25519_key_pair():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

# ========== 💾 SERIALIZATION ==========

def serialize_private_key(private_key, password: str = None):
    if password:
        encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
    else:
        encryption_algorithm = serialization.NoEncryption()
    
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )

def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def load_private_key(pem_data, password: str = None):
    return serialization.load_pem_private_key(
        pem_data,
        password=password.encode() if password else None,
        backend=backend
    )

def load_public_key(pem_data):
    return serialization.load_pem_public_key(
        pem_data,
        backend=backend
    )

def generate_keypair(method="rsa", password: bytes = None):
    """
    Создаёт пару ключей (приватный, публичный) с заданным методом.
    method: "rsa" или "ed25519"
    password: если указан, приватный ключ будет зашифрован
    Возвращает (private_key_pem: bytes, public_key_pem: bytes)
    """
    if method == "rsa":
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
    elif method == "ed25519":
        private_key = ed25519.Ed25519PrivateKey.generate()
    else:
        raise ValueError("Unsupported key generation method")

    encryption_algorithm = (
        serialization.BestAvailableEncryption(password)
        if password
        else serialization.NoEncryption()
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm,
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_pem, public_pem

# ========== 🔐 ENCRYPT / DECRYPT PRIVATE KEY BY SYMMETRIC KEY ==========

def derive_key(password: str, salt: bytes = None):
    if not salt:
        salt = os.urandom(16)
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=backend
    )
    key = kdf.derive(password.encode())
    return key, salt

def encrypt_data(data: bytes, password: str):
    key, salt = derive_key(password)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, data, None)
    return {
        'ciphertext': base64.b64encode(encrypted).decode(),
        'salt': base64.b64encode(salt).decode(),
        'nonce': base64.b64encode(nonce).decode()
    }

def decrypt_data(encrypted_data: dict, password: str):
    ciphertext = base64.b64decode(encrypted_data['ciphertext'])
    salt = base64.b64decode(encrypted_data['salt'])
    nonce = base64.b64decode(encrypted_data['nonce'])
    key, _ = derive_key(password, salt=salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)

# ========== ✅ TESTING ==========

if __name__ == "__main__":
    priv, pub = generate_ed25519_key_pair()
    priv_pem = serialize_private_key(priv)
    pub_pem = serialize_public_key(pub)

    print("PRIVATE PEM:")
    print(priv_pem.decode())
    print("PUBLIC PEM:")
    print(pub_pem.decode())

    encrypted = encrypt_data(priv_pem, "secret-password")
    decrypted = decrypt_data(encrypted, "secret-password")
    assert decrypted == priv_pem
    print("✅ Encryption/decryption OK")
