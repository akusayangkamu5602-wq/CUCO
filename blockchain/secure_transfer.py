import json
import hashlib
import subprocess
from pathlib import Path

DATA = Path("wallet/data")
LEDGER = Path("blockchain/data/ledger.json")

def run(cmd):
    return subprocess.run(
        cmd, check=True, capture_output=True
    )

def stop(message):
    raise SystemExit(message)

if not (DATA / "last_transaction.json").exists():
    stop("Transaksi tidak ditemukan!")

if not (DATA / "public.pem").exists():
    stop("Wallet publik tidak ditemukan!")

if not LEDGER.exists():
    stop("Ledger tidak ditemukan!")

tx = json.loads(
    (DATA / "last_transaction.json").read_text()
)

public = run([
    "openssl", "pkey", "-pubin",
    "-in", str(DATA / "public.pem"),
    "-outform", "DER"
]).stdout

sender_address = "CUCO" + hashlib.sha256(public).hexdigest()

if tx["sender"] != sender_address:
    stop("Alamat pengirim tidak cocok!")

if not tx["receiver"].startswith("CUCO"):
    stop("Alamat penerima tidak valid!")

amount = tx["amount"]

if type(amount) is not int or amount <= 0:
    stop("Jumlah transaksi tidak valid!")

message = {
    "sender": tx["sender"],
    "receiver": tx["receiver"],
    "amount": amount
}

raw = json.dumps(
    message,
    sort_keys=True,
    separators=(",", ":")
).encode()

(DATA / "secure_message.txt").write_bytes(raw)
(DATA / "secure_signature.bin").write_bytes(
    bytes.fromhex(tx["signature"])
)

try:
    result = run([
        "openssl", "dgst", "-sha256",
        "-verify", str(DATA / "public.pem"),
        "-signature", str(DATA / "secure_signature.bin"),
        str(DATA / "secure_message.txt")
    ])
except subprocess.CalledProcessError:
    stop("Tanda tangan digital tidak valid!")

if b"Verified OK" not in result.stdout:
    stop("Tanda tangan digital tidak valid!")

ledger = json.loads(LEDGER.read_text())
balances = ledger["balances"]

if sum(balances.values()) != ledger["issued"]:
    stop("Ledger tidak konsisten!")

if balances.get(sender_address, 0) < amount:
    print("TANDA TANGAN VALID!")
    print("Tetapi saldo tidak mencukupi.")
    print("Transfer belum dilakukan.")
    raise SystemExit(0)

balances[sender_address] -= amount
balances[tx["receiver"]] = (
    balances.get(tx["receiver"], 0) + amount
)

temp = LEDGER.with_suffix(".tmp")
temp.write_text(json.dumps(ledger, indent=2))
temp.replace(LEDGER)

print("TRANSFER BERHASIL!")
print("Jumlah:", amount, "CUCO")
