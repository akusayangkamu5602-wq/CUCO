import hashlib
import json
import time

MAX_SUPPLY = 21_000_000
DIFFICULTY = 4

class Block:
    def __init__(self, index, transactions, previous_hash,
                 timestamp=None, nonce=0):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def mine(self, difficulty=DIFFICULTY):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
        print("Blok berhasil ditambang:", self.hash)


class CUCOBlockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, [], "0")
        self.chain.append(genesis)

    def latest_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, receiver, amount):
        if amount <= 0:
            raise ValueError("Jumlah harus lebih dari nol")
        self.pending_transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        })

    def mine_pending(self):
        block = Block(
            len(self.chain),
            self.pending_transactions.copy(),
            self.latest_block().hash
        )
        block.mine()
        self.chain.append(block)
        self.pending_transactions = []

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        return True

    def show_chain(self):
        for block in self.chain:
            print(json.dumps(block.__dict__, indent=2))


if __name__ == "__main__":
    cuco = CUCOBlockchain()

    print("=== CUCO BLOCKCHAIN ===")
    print("Genesis block dibuat.")

    cuco.add_transaction("Andika", "Wallet-CUCO-001", 10)
    cuco.mine_pending()

    print("Jumlah blok:", len(cuco.chain))
    print("Blockchain valid:", cuco.is_valid())
    cuco.show_chain()
