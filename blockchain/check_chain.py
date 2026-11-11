import json
import hashlib
from pathlib import Path

FILE = Path("blockchain/data/chain.json")

DIFFICULTY = 4
MAX_SUPPLY = 21_000_000
INITIAL_REWARD = 50
HALVING_INTERVAL = 210_000

def calculate_hash(block):
    data = {
        "index": block["index"],
        "timestamp": block["timestamp"],
        "transactions": block["transactions"],
        "previous_hash": block["previous_hash"],
        "nonce": block["nonce"]
    }
    raw = json.dumps(data, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()

def block_reward(height):
    halvings = height // HALVING_INTERVAL

    if halvings >= 64:
        return 0

    return INITIAL_REWARD >> halvings

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

def check():
    if not FILE.exists():
        print("File blockchain tidak ditemukan!")
        return

    try:
        chain = json.loads(FILE.read_text())
    except Exception:
        print("File blockchain rusak!")
        return

    if not isinstance(chain, list) or not chain:
        print("Blockchain kosong atau format salah!")
        return

    issued = 0

    try:
        for i, block in enumerate(chain):

            if block["index"] != i:
                raise ValueError(f"Index blok salah: {i}")

            if not isinstance(block["transactions"], list):
                raise ValueError(f"Format transaksi salah: {i}")

            if calculate_hash(block) != block["hash"]:
                raise ValueError(f"Hash blok tidak valid: {i}")

            if i == 0:
                if block["previous_hash"] != "0":
                    raise ValueError("Genesis tidak valid!")
            else:
                previous = chain[i - 1]

                if block["previous_hash"] != previous["hash"]:
                    raise ValueError(f"Hubungan hash rusak: {i}")

                if not block["hash"].startswith("0" * DIFFICULTY):
                    raise ValueError(f"Proof of Work gagal: {i}")

            rewards = [
                tx for tx in block["transactions"]
                if isinstance(tx, dict)
                and tx.get("type") == "coinbase"
            ]

            if len(rewards) > 1:
                raise ValueError(f"Coinbase ganda pada blok {i}")

            if rewards:
                tx = rewards[0]
                expected = min(
                    block_reward(i),
                    MAX_SUPPLY - issued
                )

                if not valid_address(tx.get("to")):
                    raise ValueError(f"Alamat reward salah: {i}")

                amount = tx.get("amount")

                if type(amount) is not int or amount != expected or amount <= 0:
                    raise ValueError(f"Reward tidak sesuai: {i}")

                issued += amount

            if issued > MAX_SUPPLY:
                raise ValueError("Suplai maksimum terlampaui!")

    except (KeyError, TypeError, ValueError) as error:
        print("BLOCKCHAIN TIDAK VALID!")
        print("Alasan:", error)
        return

    print("================================")
    print("CUCO BLOCKCHAIN VALID!")
    print("Jumlah blok:", len(chain))
    print("Tinggi blok:", len(chain) - 1)
    print("Total reward:", issued, "CUCO")
    print("Sisa batas suplai:", MAX_SUPPLY - issued, "CUCO")
    print("Hash terakhir:", chain[-1]["hash"])
    print("Proof of Work: VALID")
    print("================================")

if __name__ == "__main__":
    check()
