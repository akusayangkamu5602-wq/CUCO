import json
import hashlib
import subprocess
import sys
from pathlib import Path

PRIVATE = Path("wallet/data/private.pem")
PUBLIC = Path("wallet/data/public.pem")
MEMPOOL = Path("blockchain/data/mempool.json")
OUTPUT = Path("wallet/data/last_transaction.json")

def run(command):
    return subprocess.run(
        command,
        check=True,
        capture_output=True
    )

def stop(message):
    raise SystemExit(message)

if not PRIVATE.exists() or not PUBLIC.exists():
    stop("Wallet tidak ditemukan!")

if len(sys.argv) != 3:
    stop("Cara pakai: python wallet/transaction.py ALAMAT_TUJUAN JUMLAH")

receiver = sys.argv[1]

try:
    amount = int(sys.argv[2])
except ValueError:
    stop("Jumlah harus bilangan bulat!")

def valid_address(address):
    if not isinstance(address, str) or not address.startswith("CUCO"):
        return False
    key = address[4:]
    if len(key) != 64:
        return False
    try:
        bytes.fromhex(key)
        return True
    except ValueError:
        return False

if not valid_address(receiver):
    stop("Alamat penerima tidak valid!")

if amount <= 0:
    stop("Jumlah harus lebih dari nol!")

public_der = run([
    "openssl", "pkey", "-pubin",
    "-in", str(PUBLIC), "-outform", "DER"
]).stdout

sender = "CUCO" + hashlib.sha256(public_der).hexdigest()

if receiver == sender:
    stop("Alamat penerima sama dengan pengirim!")

message = {
    "type": "transfer",
    "sender": sender,
    "receiver": receiver,
    "amount": amount
}

raw = json.dumps(
    message,
    sort_keys=True,
    separators=(",", ":")
).encode()

message_file = Path("wallet/data/message.txt")
signature_file = Path("wallet/data/signature.bin")

message_file.write_bytes(raw)

run([
    "openssl", "dgst", "-sha256",
    "-sign", str(PRIVATE),
    "-out", str(signature_file),
    str(message_file)
])

signature = signature_file.read_bytes().hex()

run([
    "openssl", "dgst", "-sha256",
    "-verify", str(PUBLIC),
    "-signature", str(signature_file),
    str(message_file)
])

transaction = dict(message)
transaction["public_key"] = PUBLIC.read_text()
transaction["signature"] = signature

if MEMPOOL.exists():
    mempool = json.loads(MEMPOOL.read_text())
else:
    mempool = []

if not isinstance(mempool, list):
    stop("Format mempool rusak!")

mempool.append(transaction)

temp = MEMPOOL.with_suffix(".tmp")
temp.write_text(json.dumps(mempool, indent=2))
temp.replace(MEMPOOL)

OUTPUT.write_text(json.dumps(transaction, indent=2))

print("TRANSAKSI BERHASIL DITANDATANGANI!")
print("Pengirim:", sender)
print("Penerima:", receiver)
print("Jumlah:", amount, "CUCO")
print("Tanda tangan: VALID")
print("Status: MENUNGGU VALIDASI DAN MINING")
