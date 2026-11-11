import json
import hashlib
import subprocess
from pathlib import Path

MEMPOOL = Path("blockchain/data/mempool.json")

def stop(message):
    raise SystemExit(message)

def valid_address(address):
    if not isinstance(address, str):
        return False
    if not address.startswith("CUCO"):
        return False
    key = address[4:]
    if len(key) != 64:
        return False
    try:
        bytes.fromhex(key)
        return True
    except ValueError:
        return False

def validate_transaction(tx):
    if not isinstance(tx, dict):
        return False

    required = [
        "type", "sender", "receiver",
        "amount", "public_key", "signature"
    ]

    if not all(key in tx for key in required):
        return False

    if tx["type"] != "transfer":
        return False

    if not valid_address(tx["sender"]):
        return False

    if not valid_address(tx["receiver"]):
        return False

    if tx["sender"] == tx["receiver"]:
        return False

    if type(tx["amount"]) is not int or tx["amount"] <= 0:
        return False

    try:
        public_file = Path("blockchain/data/validator_public.pem")
        signature_file = Path("blockchain/data/validator_signature.bin")
        message_file = Path("blockchain/data/validator_message.json")

        public_file.write_text(tx["public_key"])

        public_der = subprocess.run(
            ["openssl", "pkey", "-pubin", "-in", str(public_file), "-outform", "DER"],
            check=True,
            capture_output=True
        ).stdout

        address = "CUCO" + hashlib.sha256(public_der).hexdigest()

        if address != tx["sender"]:
            return False

        message = {
            "type": tx["type"],
            "sender": tx["sender"],
            "receiver": tx["receiver"],
            "amount": tx["amount"]
        }

        raw = json.dumps(
            message,
            sort_keys=True,
            separators=(",", ":")
        ).encode()

        message_file.write_bytes(raw)
        signature_file.write_bytes(bytes.fromhex(tx["signature"]))

        result = subprocess.run(
            [
                "openssl", "dgst", "-sha256",
                "-verify", str(public_file),
                "-signature", str(signature_file),
                str(message_file)
            ],
            check=True,
            capture_output=True
        )

        return b"Verified OK" in result.stdout

    except Exception:
        return False

def main():
    if not MEMPOOL.exists():
        stop("Mempool tidak ditemukan!")

    try:
        transactions = json.loads(MEMPOOL.read_text())
    except Exception:
        stop("Format mempool rusak!")

    if not isinstance(transactions, list):
        stop("Mempool harus berupa daftar transaksi!")

    print("=== VALIDATOR TRANSAKSI CUCO ===")
    print("Jumlah transaksi:", len(transactions))

    for i, tx in enumerate(transactions, 1):
        status = validate_transaction(tx)
        print("Transaksi", i, ":", "VALID" if status else "TIDAK VALID")

if __name__ == "__main__":
    main()
