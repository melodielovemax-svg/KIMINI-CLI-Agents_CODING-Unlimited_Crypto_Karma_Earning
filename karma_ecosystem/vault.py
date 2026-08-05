"""Private document vault — the encrypted subscriber account store.

All subscriber account data created by the automation system ("full new
information for subscribed plans") is saved into ONE private document:

    data/vault.karma      AES-256-GCM envelope (JSON inside)
    data/vault.sha256     integrity digest (tamper detection)

The master key is derived from the vault password with scrypt (N=2**15).
Every subscriber's keystore is additionally encrypted with their own
per-account password — two layers of encryption.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import scrypt

VAULT_VERSION = 1
SCRYPT_N = 2**15
SCRYPT_R = 8
SCRYPT_P = 1


def _derive_key(password: str, salt: bytes) -> bytes:
    return scrypt(
        password.encode("utf-8"),
        salt,
        32,  # AES-256
        N=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
    )


@dataclass
class VaultRecord:
    subscriber_id: str
    name: str
    email: str
    plan_id: int
    address: str
    keystore: dict
    created_at: float
    active_until: float = 0.0
    deeds: int = 0
    karma_balance: str = "0"

    def to_dict(self) -> dict:
        return {
            "subscriber_id": self.subscriber_id,
            "name": self.name,
            "email": self.email,
            "plan_id": self.plan_id,
            "address": self.address,
            "keystore": self.keystore,
            "created_at": self.created_at,
            "active_until": self.active_until,
            "deeds": self.deeds,
            "karma_balance": self.karma_balance,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "VaultRecord":
        return cls(**d)


@dataclass
class Vault:
    """Encrypted-at-rest document of all subscriber accounts."""

    path: str
    password: str
    data: dict = field(default_factory=dict)

    # ---------- load / save ----------
    @classmethod
    def open_or_create(cls, path: str, password: str) -> "Vault":
        v = cls(path=path, password=password)
        if os.path.exists(path):
            v._load()
        else:
            v.data = {
                "version": VAULT_VERSION,
                "created_at": time.time(),
                "subscribers": {},
            }
            v.save()
        return v

    def save(self) -> None:
        payload = json.dumps(self.data, sort_keys=True).encode("utf-8")
        salt = os.urandom(16)
        nonce = os.urandom(12)
        key = _derive_key(self.password, salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ct, tag = cipher.encrypt_and_digest(payload)
        envelope = {
            "version": VAULT_VERSION,
            "kdf": "scrypt",
            "scrypt_n": SCRYPT_N,
            "salt_hex": salt.hex(),
            "nonce_hex": nonce.hex(),
            "tag_hex": tag.hex(),
            "ciphertext_hex": ct.hex(),
        }
        raw = json.dumps(envelope, sort_keys=True).encode("utf-8")
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        with open(self.path, "wb") as f:
            f.write(raw)
        with open(self.path + ".sha256", "w") as f:
            f.write(SHA256.new(raw).hexdigest())
        # Wipe derived key material from memory.
        del key

    def _load(self) -> None:
        with open(self.path, "rb") as f:
            raw = f.read()
        # integrity check against the stored digest
        digest_path = self.path + ".sha256"
        if os.path.exists(digest_path):
            expected = open(digest_path).read().strip()
            actual = SHA256.new(raw).hexdigest()
            if actual != expected:
                raise ValueError("VAULT TAMPERED: sha256 digest mismatch — refusing to open")
        env = json.loads(raw.decode("utf-8"))
        if env.get("version") != VAULT_VERSION:
            raise ValueError(f"unsupported vault version {env.get('version')}")
        salt = bytes.fromhex(env["salt_hex"])
        nonce = bytes.fromhex(env["nonce_hex"])
        tag = bytes.fromhex(env["tag_hex"])
        ct = bytes.fromhex(env["ciphertext_hex"])
        key = _derive_key(self.password, salt)
        try:
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            payload = cipher.decrypt_and_verify(ct, tag)
        except ValueError:
            raise ValueError("VAULT LOCKED: wrong password or corrupted document") from None
        finally:
            del key
        self.data = json.loads(payload.decode("utf-8"))

    # ---------- record access ----------
    @property
    def subscribers(self) -> dict:
        return self.data.setdefault("subscribers", {})

    def upsert(self, record: VaultRecord) -> None:
        self.subscribers[record.subscriber_id] = record.to_dict()
        self.save()

    def get(self, subscriber_id: str) -> VaultRecord | None:
        d = self.subscribers.get(subscriber_id)
        return VaultRecord.from_dict(d) if d else None

    def list(self) -> list[VaultRecord]:
        return [VaultRecord.from_dict(d) for d in self.subscribers.values()]

    def export_document(self, out_path: str) -> str:
        """Copy the encrypted private document to a user-chosen location."""
        raw = open(self.path, "rb").read()
        with open(out_path, "wb") as f:
            f.write(raw)
        digest = SHA256.new(raw).hexdigest()
        with open(out_path + ".sha256", "w") as f:
            f.write(digest)
        return out_path
