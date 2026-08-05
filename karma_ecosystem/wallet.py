"""Web3 wallet creation & key custody for the Karma Ecosystem.

Every subscriber gets a real EVM wallet (secp256k1). The private key is
immediately encrypted twice before ever touching disk:

  1. into a standard Web3 JSON keystore (password-derived AES-128-CTR), and
  2. the whole account record is stored inside the AES-256-GCM vault document.

No plaintext private key is ever written to disk.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

from eth_account import Account

PASSWORD_MIN_LEN = 8


@dataclass
class Wallet:
    address: str          # checksummed 0x address
    private_key: str      # hex — kept in memory only
    keystore: dict        # Web3 JSON keystore (password encrypted)


def create_wallet(password: str, name: str = "subscriber") -> Wallet:
    """Generate a fresh EVM wallet and encrypt its key into a JSON keystore."""
    if len(password) < PASSWORD_MIN_LEN:
        raise ValueError(f"password must be at least {PASSWORD_MIN_LEN} characters")
    acct = Account.create()
    keystore = Account.encrypt(acct.key, password)
    keystore.setdefault("karma_meta", {"name": name})
    return Wallet(
        address=acct.address,
        private_key=acct.key.hex(),
        keystore=keystore,
    )


def address_from_keystore(keystore: dict, password: str) -> str:
    """Recover the address (and prove password) from an encrypted keystore."""
    acct = Account.decrypt(keystore, password)
    return Account.from_key(acct).address


def random_passphrase(bits: int = 256) -> str:
    """Generate a cryptographically random passphrase for a new subscriber."""
    return secrets.token_hex(bits // 8)


def short_hash(data: bytes, length: int = 16) -> str:
    return hashlib.sha256(data).hexdigest()[:length]
