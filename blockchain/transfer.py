import json
from pathlib import Path

FILE = Path("blockchain/data/ledger.json")

def load_ledger():
    if not FILE.exists():
        raise SystemExit("Ledger belum dibuat!")
    return json.loads(FILE.read_text())

def save_ledger(data):
    FILE.write_text(json.dumps(data, indent=2))

def transfer(sender, receiver, amount):
    data = load_ledger()

    if not sender.startswith("CUCO") or not receiver.startswith("CUCO"):
        raise ValueError("Alamat tidak valid")

    if sender == receiver:
        raise ValueError("Pengirim dan penerima sama")

    if not isinstance(amount, int) or amount <= 0:
        raise ValueError("Jumlah harus bilangan bulat positif")

    balances = data["balances"]
    sender_balance = balances.get(sender, 0)

    if sender_balance < amount:
        raise ValueError("Saldo tidak mencukupi")

    balances[sender] = sender_balance - amount
    balances[receiver] = balances.get(receiver, 0) + amount

    save_ledger(data)

    print("TRANSFER BERHASIL!")
    print("Pengirim:", sender)
    print("Penerima:", receiver)
    print("Jumlah:", amount, "CUCO")
    print("Sisa saldo:", balances[sender])

if __name__ == "__main__":
    print("CUCO TRANSFER ENGINE SIAP")
    print("Ledger:", FILE)
