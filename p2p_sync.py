import asyncio
import base64
import hashlib
import os
import secrets
import socket
import json
import uuid
import time
import platform
import logging
import aiohttp
from cryptography.fernet import Fernet, InvalidToken
from typing import Dict, List, Callable, Optional

from app_paths import KEY_FILE

logger = logging.getLogger("P2PSync")

DISCOVERY_PORT = 45678
BROADCAST_INTERVAL = 2.0
PEER_TIMEOUT = 8.0
MESSAGE_TTL = 120  # seconds; sealed messages older than this are rejected (replay protection)
SYNC_TIMEOUT = aiohttp.ClientTimeout(total=90.0)  # file payloads need far longer than the 3s ping timeout, but under MESSAGE_TTL
MIN_KEY_LENGTH = 16


def save_sync_key(key: str):
    KEY_FILE.write_text(key + "\n", encoding="utf-8")


def load_sync_key() -> str:
    """Shared pairing secret: CLIPBOARD_SYNC_KEY env var, else sync.key (generated on first run)."""
    key = os.environ.get("CLIPBOARD_SYNC_KEY", "").strip()
    if key:
        return key
    if KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
        if key:
            return key
    key = secrets.token_urlsafe(32)
    save_sync_key(key)
    logger.warning(f"Generated new pairing key {KEY_FILE} - pair other devices from the dashboard.")
    return key


def get_local_broadcast_ips() -> List[str]:
    """Finds standard broadcast targets for the local network."""
    targets = ["255.255.255.255"]
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        # Add subnet broadcast (e.g. 10.0.1.255 or 192.168.1.255)
        parts = local_ip.split(".")
        if len(parts) == 4:
            targets.append(f"{parts[0]}.{parts[1]}.{parts[2]}.255")
    except Exception:
        pass
    return list(set(targets))


class PeerNode:
    def __init__(self, node_id: str, name: str, host: str, port: int, system: str):
        self.node_id = node_id
        self.name = name
        self.host = host
        self.port = port
        self.system = system
        self.last_seen = time.time()

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def to_dict(self) -> dict:
        return {
            "id": self.node_id,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "system": self.system,
            "last_seen": self.last_seen,
            "url": self.url,
        }


class UDPDiscoveryProtocol(asyncio.DatagramProtocol):
    def __init__(self, p2p_manager: "P2PManager"):
        self.manager = p2p_manager
        self.transport: Optional[asyncio.DatagramTransport] = None

    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = transport
        sock = transport.get_extra_info("socket")
        if sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def datagram_received(self, data: bytes, addr: tuple):
        try:
            msg = self.manager.unseal(data)
            if msg.get("app") != "hermes-clip-sync":
                return
            sender_id = msg.get("id")
            if sender_id == self.manager.node_id:
                return

            host = addr[0]
            port = msg.get("port", 7890)
            name = msg.get("name", "Unknown")
            system = msg.get("system", "unknown")

            self.manager.handle_peer_beacon(sender_id, name, host, port, system)
        except InvalidToken:
            logger.debug(f"Ignoring beacon from {addr[0]} with a different pairing key")
        except Exception as e:
            logger.debug(f"Discovery packet error: {e}")


class P2PManager:
    def __init__(self, local_http_port: int, on_peer_change: Optional[Callable[[List[dict]], None]] = None):
        self.node_id = str(uuid.uuid4())[:8]
        self.local_http_port = local_http_port
        self.system = platform.system()
        self.hostname = socket.gethostname()
        self.peers: Dict[str, PeerNode] = {}
        self.on_peer_change = on_peer_change
        self._running = False
        self._udp_transport: Optional[asyncio.DatagramTransport] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._broadcast_targets = get_local_broadcast_ips()
        self._apply_key(load_sync_key())

    def _apply_key(self, key: str):
        self.sync_key = key
        secret = hashlib.sha256(key.encode("utf-8")).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(secret))

    def set_sync_key(self, key: str):
        """Re-pairs at runtime: peers on the old key stop decrypting and drop out after PEER_TIMEOUT."""
        key = key.strip()
        if len(key) < MIN_KEY_LENGTH:
            raise ValueError(f"Pairing key must be at least {MIN_KEY_LENGTH} characters")
        save_sync_key(key)
        self._apply_key(key)
        self.peers.clear()
        if self.on_peer_change:
            self.on_peer_change([])

    def seal(self, payload: dict) -> bytes:
        """Encrypts + authenticates a message for peers sharing the same pairing key."""
        return self._fernet.encrypt(json.dumps(payload).encode("utf-8"))

    def unseal(self, token: bytes) -> dict:
        """Raises InvalidToken if the message was not sealed with our key or is expired."""
        return json.loads(self._fernet.decrypt(token, ttl=MESSAGE_TTL))

    def handle_peer_beacon(self, node_id: str, name: str, host: str, port: int, system: str):
        peer = self.peers.get(node_id)
        if not peer:
            peer = PeerNode(node_id, name, host, port, system)
            self.peers[node_id] = peer
            logger.info(f"Discovered peer: {name} ({system}) at {host}:{port}")
            # Mutual handshake: immediately notify this peer directly via HTTP
            asyncio.create_task(self._send_handshake(peer))
        else:
            peer.host = host
            peer.port = port
            peer.last_seen = time.time()

        if self.on_peer_change:
            self.on_peer_change(self.get_active_peers_list())

    def get_active_peers_list(self) -> List[dict]:
        now = time.time()
        active = [p.to_dict() for p in self.peers.values() if (now - p.last_seen) < PEER_TIMEOUT]
        return active

    async def _send_handshake(self, peer: PeerNode):
        """Direct unicast ping to ensure 2-way connection even if broadcast was 1-way."""
        if not self._session:
            return
        payload = {
            "app": "hermes-clip-sync",
            "id": self.node_id,
            "name": self.hostname,
            "system": self.system,
            "port": self.local_http_port,
        }
        try:
            async with self._session.post(f"{peer.url}/api/ping", data=self.seal(payload)) as resp:
                if resp.status == 200:
                    logger.info(f"Mutual handshake confirmed with {peer.name}")
        except Exception as e:
            logger.debug(f"Handshake to {peer.name} failed: {e}")

    async def start(self):
        self._running = True
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3.0))

        loop = asyncio.get_running_loop()

        # Start UDP listener
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                try:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except Exception:
                    pass
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.bind(("", DISCOVERY_PORT))
            sock.setblocking(False)

            self._udp_transport, _ = await loop.create_datagram_endpoint(
                lambda: UDPDiscoveryProtocol(self),
                sock=sock
            )
            logger.info(f"P2P UDP Discovery listening on port {DISCOVERY_PORT}")
        except Exception as e:
            logger.warning(f"Could not bind UDP discovery socket: {e}")

        # Start background broadcaster & cleaner
        asyncio.create_task(self._beacon_loop())
        asyncio.create_task(self._peer_cleanup_loop())

    async def stop(self):
        self._running = False
        if self._udp_transport:
            self._udp_transport.close()
        if self._session:
            await self._session.close()

    async def _beacon_loop(self):
        """Broadcasts identity packet to all detected LAN broadcast targets."""
        beacon = {
            "app": "hermes-clip-sync",
            "id": self.node_id,
            "name": self.hostname,
            "system": self.system,
            "port": self.local_http_port,
        }

        while self._running:
            try:
                if self._udp_transport:
                    beacon_data = self.seal(beacon)  # re-sealed each round so the timestamp stays fresh
                    for target in self._broadcast_targets:
                        try:
                            self._udp_transport.sendto(beacon_data, (target, DISCOVERY_PORT))
                        except Exception:
                            pass
            except Exception as e:
                logger.debug(f"Broadcast error: {e}")
            await asyncio.sleep(BROADCAST_INTERVAL)

    async def _peer_cleanup_loop(self):
        """Removes expired peers."""
        while self._running:
            now = time.time()
            expired = [pid for pid, peer in self.peers.items() if (now - peer.last_seen) > PEER_TIMEOUT]
            if expired:
                for pid in expired:
                    del self.peers[pid]
                if self.on_peer_change:
                    self.on_peer_change(self.get_active_peers_list())
            await asyncio.sleep(2.0)

    async def broadcast_to_peers(self, payload: dict):
        """Sends new clipboard item to all active peers in parallel."""
        active_peers = [p for p in self.peers.values() if (time.time() - p.last_seen) < PEER_TIMEOUT]
        if not active_peers:
            logger.info("No active peers found to broadcast clipboard data.")
            return

        tasks = []
        for peer in active_peers:
            tasks.append(self._send_payload(peer, payload))
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_payload(self, peer: PeerNode, payload: dict):
        if not self._session:
            return
        target_url = f"{peer.url}/api/sync"
        try:
            async with self._session.post(target_url, data=self.seal(payload), timeout=SYNC_TIMEOUT) as resp:
                if resp.status == 200:
                    logger.info(f"Successfully synced item {payload.get('hash', '')[:8]} to {peer.name}")
                else:
                    logger.warning(f"Peer {peer.name} responded with status {resp.status}")
        except Exception as e:
            logger.debug(f"Failed to sync to {peer.name} ({peer.url}): {e}")
