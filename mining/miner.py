import json
import hashlib
import time
import os
from pathlib import Path
from reward import block_reward, MAX_SUPPLY

CHAIN_FILE = Path("blockchain/data/chain.json")
DIFFICULTY = 4

WALLET = "CUCOa6bd286b9543e0dab29dbc7ffe34562e9f563f158e75f250b0d74d239ea3ffbf"

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

def validate_chain(chain):
    if not chain:
        return False

    issued = 0

    for i, block in enumerate(chain):
        if block["index"] != i:
            return False

        if calculate_hash(block) != block["hash"]:
            return False

        if i == 0:
            if block["previous_hash"] != "0":
                return False
        else:
            previous = chain[i - 1]

            if block["previous_hash"] != previous["hash"]:
                return False

            if not block["hash"].startswith("0" * DIFFICULTY):
                return False

        rewards = [
            tx for tx in block["transactions"]
            if tx.get("type") == "coinbase"
        ]

        if len(rewards) > 1:
            return False

        if rewards:
            tx = rewards[0]
            expected = min(
                block_reward(i),
                MAX_SUPPLY - issued
            )

            if tx.get("to", "").startswith("CUCO") is False:
                return False

            if tx.get("amount") != expected or expected <= 0:
                return False

            issued += expected

        if issued > MAX_SUPPLY:
            return False

    return True

def mine_block(index, transactions, previous_hash):
    block = {
        "index": index,
        "timestamp": time.time(),
        "transactions": transactions,
        "previous_hash": previous_hash,
        "nonce": 0
    }

    target = "0" * DIFFICULTY
    print("Mining blok", index, "...")

    while True:
        block_hash = calculate_hash(block)

        if block_hash.startswith(target):
            block["hash"] = block_hash
            print("Blok berhasil ditambang!")
            print("Hash:", block_hash)
            print("Nonce:", block["nonce"])
            return block

        block["nonce"] += 1

def main():
    if not CHAIN_FILE.exists():
        raise SystemExit("Blockchain tidak ditemukan!")

    chain = json.loads(CHAIN_FILE.read_text())

    if not validate_chain(chain):
        raise SystemExit("Blockchain tidak valid!")

    issued = sum(
        tx["amount"]
        for block in chain
        for tx in block["transactions"]
        if tx.get("type") == "coinbase"
    )

    reward = min(block_reward(len(chain)), MAX_SUPPLY - issued)

    if reward <= 0:
        raise SystemExit("Reward sudah habis!")

    print("Alamat penerima:", WALLET)
    print("Reward blok:", reward, "CUCO")

    transaction = {
        "type": "coinbase",
        "to": WALLET,
        "amount": reward
    }

    new_block = mine_block(
        len(chain),
        [transaction],
        chain[-1]["hash"]
    )

    chain.append(new_block)

    temp = CHAIN_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(chain, indent=2))
    os.replace(temp, CHAIN_FILE)

    print("Blockchain berhasil diperbarui!")
    print("Total blok:", len(chain))
    print("Valid:", validate_chain(chain))

if __name__ == "__main__":
    main()
