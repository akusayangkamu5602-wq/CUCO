import json
from pathlib import Path

CHAIN_FILE = Path("blockchain/data/chain.json")

def get_state():
    if not CHAIN_FILE.exists():
        raise ValueError("Blockchain tidak ditemukan")

    chain = json.loads(CHAIN_FILE.read_text())
    balances = {}
    nonces = {}

    for block in chain:
        for tx in block.get("transactions", []):
            if tx.get("type") == "coinbase":
                address = tx.get("to")
                amount = tx.get("amount")

                if not isinstance(address, str):
                    raise ValueError("Alamat coinbase tidak valid")
                if type(amount) is not int or amount < 0:
                    raise ValueError("Reward tidak valid")

                balances[address] = balances.get(address, 0) + amount

            elif tx.get("type") == "transfer":
                sender = tx.get("sender")
                receiver = tx.get("receiver")
                amount = tx.get("amount")
                nonce = tx.get("nonce")

                if not isinstance(sender, str) or not isinstance(receiver, str):
                    raise ValueError("Alamat transfer tidak valid")
                if type(amount) is not int or amount <= 0:
                    raise ValueError("Jumlah transfer tidak valid")
                if type(nonce) is not int or nonce != nonces.get(sender, 0) + 1:
                    raise ValueError("Nonce transfer tidak valid")

                if balances.get(sender, 0) < amount:
                    raise ValueError("Saldo pengirim tidak cukup")

                balances[sender] -= amount
                balances[receiver] = balances.get(receiver, 0) + amount
                nonces[sender] = nonce

    return balances, nonces

if __name__ == "__main__":
    balances, nonces = get_state()

    print("=== CUCO ACCOUNT STATE ===")
    print("Jumlah alamat:", len(balances))

    for address, balance in balances.items():
        print(address, ":", balance, "CUCO")
        print("Nonce:", nonces.get(address, 0))
