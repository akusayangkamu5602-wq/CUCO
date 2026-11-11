import json
import hashlib
import subprocess
from pathlib import Path

DATA = Path("wallet/data")
TX_FILE = DATA / "last_transaction.json"
PUB_FILE = DATA / "public.pem"
SIG_FILE = DATA / "verify_signature.bin"
MSG_FILE = DATA / "verify_message.txt"

def run(command):
    return subprocess.run(
        command,
        check=True,
        capture_output=True
    )

if not TX_FILE.exists() or not PUB_FILE.exists():
    raise SystemExit("File transaksi atau wallet tidak ditemukan!")

tx = json.loads(TX_FILE.read_text())

required = ["sender", "receiver", "amount", "signature"]
if not all(k in tx for k in required):
    raise SystemExit("Data transaksi tidak lengkap!")

if not isinstance(tx["amount"], (int, float)) or tx["amount"] <= 0:
    raise SystemExit("Jumlah transaksi tidak valid!")

# Hitung alamat dari kunci publik wallet
public_der = run([
    "openssl", "pkey", "-pubin",
    "-in", str(PUB_FILE), "-outform", "DER"
]).stdout

address = "CUCO" + hashlib.sha256(public_der).hexdigest()

if tx["sender"] != address:
    raise SystemExit("Alamat pengirim tidak cocok!")

# Susun ulang pesan yang ditandatangani
message = {
    "sender": tx["sender"],
    "receiver": tx["receiver"],
    "amount": tx["amount"]
}

raw = json.dumps(
    message,
    sort_keys=True,
    separators=(",", ":")
).encode()

MSG_FILE.write_bytes(raw)
SIG_FILE.write_bytes(bytes.fromhex(tx["signature"]))

# Verifikasi tanda tangan
result = run([
    "openssl", "dgst", "-sha256",
    "-verify", str(PUB_FILE),
    "-signature", str(SIG_FILE),
    str(MSG_FILE)
])

if b"Verified OK" in result.stdout:
    print("TRANSAKSI CUCO VALID!")
    print("Alamat pengirim cocok.")
    print("Tanda tangan digital valid.")
    print("Jumlah:", tx["amount"], "CUCO")
else:
    print("TRANSAKSI TIDAK VALID!")

