import json
import sys
sys.path.insert(0, "src")

from cuco import CUCOBlockchain

cuco = CUCOBlockchain()
cuco.add_transaction("Andika", "Wallet-CUCO-001", 10)
cuco.mine_pending()

data = [block.__dict__ for block in cuco.chain]

with open("blockchain/data/chain.json", "w") as f:
    json.dump(data, f, indent=2)

print("CUCO BLOCKCHAIN TERSIMPAN!")
print("Total blok:", len(data))
print("Valid:", cuco.is_valid())
