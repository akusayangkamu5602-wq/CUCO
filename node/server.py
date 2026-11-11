from flask import Flask, jsonify, request
import json
from pathlib import Path
from urllib.parse import urlparse
from threading import Lock

app = Flask(__name__)

CHAIN_FILE = Path("blockchain/data/chain.json")
PEER_FILE = Path("node/data/peers.json")
NETWORK_FILE = Path("node/network.json")
LOCK = Lock()

PEER_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_json(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default

def load_peers():
    data = load_json(PEER_FILE, [])
    return data if isinstance(data, list) else []

def save_peers(peers):
    temp = PEER_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(peers, indent=2))
    temp.replace(PEER_FILE)

def load_chain():
    data = load_json(CHAIN_FILE, [])
    return data if isinstance(data, list) else []

def network_config():
    return load_json(NETWORK_FILE, {})

def valid_peer(url):
    if not isinstance(url, str) or len(url) > 200:
        return False
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.hostname)
            and parsed.port is not None
            and 1 <= parsed.port <= 65535
            and not parsed.username
            and not parsed.password
            and parsed.path in ("", "/")
            and not parsed.query
            and not parsed.fragment
        )
    except ValueError:
        return False

@app.route("/")
def home():
    config = network_config()
    return jsonify({
        "name": config.get("network_name", "CUCO Blockchain"),
        "symbol": config.get("symbol", "CUCO"),
        "network": "CUCO-P2P",
        "network_id": config.get("network_id"),
        "status": "running",
        "version": "0.3.0"
    })

@app.route("/status")
def status():
    chain = load_chain()
    config = network_config()
    peers = load_peers()

    return jsonify({
        "network": "CUCO-P2P",
        "network_id": config.get("network_id"),
        "status": "running",
        "block_height": len(chain) - 1,
        "total_blocks": len(chain),
        "peer_count": len(peers),
        "latest_hash": chain[-1].get("hash") if chain else None
    })

@app.route("/handshake")
def handshake():
    config = network_config()
    chain = load_chain()

    if not config.get("network_id"):
        return jsonify({"error": "Konfigurasi jaringan tidak ditemukan"}), 500

    return jsonify({
        "network_id": config["network_id"],
        "protocol_version": config.get("protocol_version"),
        "symbol": config.get("symbol"),
        "status": "ready",
        "block_height": len(chain) - 1,
        "total_blocks": len(chain),
        "latest_hash": chain[-1].get("hash") if chain else None
    })

@app.route("/blocks")
def blocks():
    return jsonify(load_chain())

@app.route("/peers", methods=["GET"])
def get_peers():
    return jsonify({"peers": load_peers()})

@app.route("/peers/register", methods=["POST"])
def register_peer():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON diperlukan"}), 400

    url = data.get("url")

    if not valid_peer(url):
        return jsonify({"error": "URL peer tidak valid"}), 400

    url = url.rstrip("/")

    with LOCK:
        peers = load_peers()

        if url not in peers:
            peers.append(url)
            save_peers(peers)

    return jsonify({
        "message": "Peer tersimpan",
        "peer_count": len(peers)
    }), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
