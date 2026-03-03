# agents/tools/identity.py

import uuid
import json
import base64
from datetime import datetime, UTC

from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives import serialization

DEFAULT_KEY_TYPE = "ed25519"  # Можно поменять на "rsa" при необходимости


def generate_did():
    """Генерация уникального DiD на основе UUID v4"""
    return f"did:hmp:{uuid.uuid4()}"


def generate_keys(key_type=DEFAULT_KEY_TYPE):
    """Генерация пары ключей"""
    if key_type == "rsa":
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    elif key_type == "ed25519":
        private_key = ed25519.Ed25519PrivateKey.generate()
    else:
        raise ValueError(f"Неизвестный тип ключа: {key_type}")

    public_key = private_key.public_key()
    return private_key, public_key


def serialize_private_key(private_key, password=None):
    """Сериализация приватного ключа"""
    encryption = (
        serialization.BestAvailableEncryption(password.encode())
        if password else
        serialization.NoEncryption()
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    ).decode()


def serialize_public_key(public_key):
    """Сериализация публичного ключа"""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()


def create_identity(name="Core Identity", key_type=DEFAULT_KEY_TYPE, metadata=None, password=None):
    """Создание полной идентичности"""
    did = generate_did()
    priv_key, pub_key = generate_keys(key_type)

    identity = {
        "id": did,
        "name": name,
        "pubkey": serialize_public_key(pub_key),
        "privkey": serialize_private_key(priv_key, password),
        "metadata": json.dumps(metadata or {}),
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    return identity
