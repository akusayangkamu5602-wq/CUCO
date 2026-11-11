import json
import urllib.request
import urllib.error
from pathlib import Path

PEERS_FILE = Path("node/data/peers.json")

def check_peers():
    if not PEERS_FILE.exists():
        print("Belum ada peer terdaftar.")
        return

    peers = json.loads(PEERS_FILE.read_text())

    for peer in peers:
        try:
            url = peer.rstrip("/") + "/status"
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "CUCO-Node/0.3"}
            )

            with urllib.request.urlopen(request, timeout=5) as response:
                data = json.loads(response.read().decode())

            if data.get("network") != "CUCO-P2P":
                print(peer, "DITOLAK: jaringan berbeda")
                continue

            print("PEER AKTIF:", peer)
            print("Tinggi blok:", data.get("block_height"))
            print("Jumlah blok:", data.get("total_blocks"))

        except Exception as error:
            print("PEER TIDAK TERJANGKAU:", peer)
            print("Alasan:", error)

if __name__ == "__main__":
    check_peers()
