import base64
import hashlib
import hmac
import secrets


def hash_secret(secret: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt, 100_000)
    return f"pbkdf2_sha256${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_secret(secret: str, encoded: str) -> bool:
    algorithm, salt_b64, digest_b64 = encoded.split("$", 2)
    if algorithm != "pbkdf2_sha256":
        return False
    salt = base64.b64decode(salt_b64)
    expected = base64.b64decode(digest_b64)
    actual = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt, 100_000)
    return hmac.compare_digest(actual, expected)


def new_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_urlsafe(16)}"


def new_api_key() -> str:
    return f"sk_{secrets.token_urlsafe(32)}"
