import json
from pathlib import Path

CHAIN_FILE = Path("blockchain/data/chain.json")
MAX_SUPPLY = 21_000_000

def get_balance(address):
    if not CHAIN_FILE.exists():
        return 0

    chain = json.loads(CHAIN_FILE.read_text())

    balance = 0

    for block in chain:
        for tx in block.get("transactions", []):
            if tx.get("type") == "coinbase" and tx.get("to") == address:
                balance += tx.get("amount", 0)

    return balance

def get_issued():
    if not CHAIN_FILE.exists():
        return 0

    chain = json.loads(CHAIN_FILE.read_text())

    return sum(
        tx.get("amount", 0)
        for block in chain
        for tx in block.get("transactions", [])
        if tx.get("type") == "coinbase"
    )

if __name__ == "__main__":
    print("=== CUCO BLOCKCHAIN WALLET ===")
    print("Total diterbitkan:", get_issued(), "CUCO")
