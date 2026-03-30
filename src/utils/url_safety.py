"""Безопасная валидация URL (SSRF guard)."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


def is_safe_public_url(url: str) -> bool:
    """Проверяет, что URL указывает на публичный http/https хост."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if not parsed.hostname:
            return False

        host = parsed.hostname
        if host in {"localhost", "127.0.0.1", "::1"}:
            return False

        # Если это literal IP
        try:
            ip = ipaddress.ip_address(host)
            return _is_public_ip(ip)
        except ValueError:
            pass

        # DNS resolve -> все адреса должны быть публичными
        infos = socket.getaddrinfo(host, None)
        for info in infos:
            raw_ip = info[4][0]
            ip = ipaddress.ip_address(raw_ip)
            if not _is_public_ip(ip):
                return False

        return True
    except Exception:
        return False


def _is_public_ip(ip: ipaddress._BaseAddress) -> bool:
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )
