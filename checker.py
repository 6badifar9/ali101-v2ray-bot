"""Structural V2Ray share-link checks and optional TCP port reachability.

IMPORTANT: a reachable TCP port is NOT proof that a V2Ray tunnel works.
"""

from __future__ import annotations

import base64
import json
import re
import socket
from dataclasses import dataclass
from urllib.parse import unquote, urlsplit

SUPPORTED_SCHEMES = ("vless", "vmess", "trojan")
MAX_CONFIG_LENGTH = 3500  # A single config must fit inside a Telegram message.


@dataclass(frozen=True)
class ConfigInfo:
    uri: str
    protocol: str
    host: str
    port: int


def _decode_vmess(payload: str) -> dict:
    if not payload or len(payload) > 10000:
        raise ValueError("Invalid VMess payload")
    try:
        raw = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        obj = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("VMess must contain base64-encoded JSON") from exc
    if not isinstance(obj, dict):
        raise ValueError("VMess payload must be an object")
    return obj


def _valid_host(host: str) -> bool:
    return bool(host) and len(host) <= 253 and not re.search(r"[\s<>\\/]", host)


def _port(value: object) -> int:
    try:
        port = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid port") from exc
    if not 1 <= port <= 65535:
        raise ValueError("Port outside 1-65535")
    return port


def parse_config(uri: str) -> ConfigInfo:
    if not isinstance(uri, str):
        raise ValueError("URI is not a string")
    uri = uri.strip()
    if not uri or len(uri) > MAX_CONFIG_LENGTH or any(ch.isspace() for ch in uri):
        raise ValueError("Empty, oversized or whitespace-containing URI")
    if "://" not in uri:
        raise ValueError("Not a share link")
    scheme, rest = uri.split("://", 1)
    scheme = scheme.lower()
    if scheme not in SUPPORTED_SCHEMES:
        raise ValueError("Unsupported scheme")

    if scheme == "vmess" and "@" not in rest:
        obj = _decode_vmess(rest.split("#", 1)[0])
        host = str(obj.get("add", "")).strip()
        port = _port(obj.get("port"))
        if not _valid_host(host) or not obj.get("id"):
            raise ValueError("Missing VMess host or ID")
    else:
        try:
            parts = urlsplit(uri)
            host = parts.hostname or ""
            port = _port(parts.port)
            user = unquote(parts.username or "")
        except (ValueError, AttributeError) as exc:
            raise ValueError("Invalid URL host or port") from exc
        if not _valid_host(host) or not user:
            raise ValueError("Missing host or credentials")
    return ConfigInfo(uri=uri, protocol=scheme.upper(), host=host, port=port)


def tcp_reachable(info: ConfigInfo, timeout: float = 2.0) -> bool:
    """Probe only if the server TCP port accepts a connection (not VPN health)."""
    try:
        with socket.create_connection((info.host, info.port), timeout=timeout):
            return True
    except (OSError, TimeoutError):
        return False


def select_configs(lines: list[str], check_tcp: bool = False, timeout: float = 2.0) -> tuple[list[ConfigInfo], dict[str, int]]:
    valid: list[ConfigInfo] = []
    seen: set[str] = set()
    stats = {"invalid": 0, "duplicates": 0, "unreachable": 0}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            info = parse_config(line)
        except ValueError:
            stats["invalid"] += 1
            continue
        if info.uri in seen:
            stats["duplicates"] += 1
            continue
        seen.add(info.uri)
        if check_tcp and not tcp_reachable(info, timeout):
            stats["unreachable"] += 1
            continue
        valid.append(info)
    return valid, stats


# Compatible convenience function for old imports.
def test_config(config: str) -> bool:
    try:
        parse_config(config)
        return True
    except ValueError:
        return False
