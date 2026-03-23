"""Security middleware for Wealth API."""

import time
import hashlib
import ipaddress
from typing import Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import asyncio
from loguru import logger

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse


class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10


@dataclass
class ClientInfo:
    client_id: str
    ip_address: str
    first_seen: datetime
    request_count: int = 0
    minute_count: int = 0
    hour_count: int = 0
    blocked: bool = False
    threat_level: ThreatLevel = ThreatLevel.LOW
    suspicious_patterns: int = 0
    last_request: datetime = field(default_factory=datetime.now)


class RateLimiter:
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self._clients: Dict[str, ClientInfo] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    def get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        user_agent = request.headers.get("user-agent", "")
        return hashlib.sha256(f"{ip}:{user_agent}".encode()).hexdigest()[:16]

    def check_rate_limit(self, client_id: str) -> tuple[bool, Optional[str]]:
        now = datetime.now()
        client = self._clients.get(client_id)

        if not client:
            self._clients[client_id] = ClientInfo(
                client_id=client_id,
                ip_address=client_id,
                first_seen=now,
            )
            return True, None

        if client.blocked:
            return False, "Client is blocked"

        time_since_last = (now - client.last_request).total_seconds()

        if time_since_last < 0.1:
            client.suspicious_patterns += 1
            if client.suspicious_patterns > 5:
                client.threat_level = ThreatLevel.HIGH
            return False, "Too many concurrent requests"

        client.minute_count += 1
        client.hour_count += 1
        client.last_request = now

        if client.minute_count > self.config.requests_per_minute:
            client.threat_level = ThreatLevel.MEDIUM
            return False, f"Rate limit exceeded: {client.minute_count} requests/minute"

        if client.hour_count > self.config.requests_per_hour:
            client.threat_level = ThreatLevel.HIGH
            return False, f"Rate limit exceeded: {client.hour_count} requests/hour"

        return True, None

    async def cleanup_old_clients(self):
        while True:
            await asyncio.sleep(300)
            now = datetime.now()
            to_remove = []

            for client_id, client in self._clients.items():
                if (now - client.last_request).total_seconds() > 3600:
                    if not client.blocked:
                        to_remove.append(client_id)

            for client_id in to_remove:
                del self._clients[client_id]

            logger.debug(f"Cleaned up {len(to_remove)} inactive clients")


class AntiScrapMiddleware(BaseHTTPMiddleware):
    SUSPICIOUS_PATTERNS = [
        "python-requests",
        "curl",
        "wget",
        "scrapy",
        "bot",
        "crawler",
        "spider",
        "httpx",
    ]

    def __init__(self, app, rate_limiter: RateLimiter = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()

    async def dispatch(self, request: Request, call_next):
        client_id = self.rate_limiter.get_client_id(request)

        allowed, reason = self.rate_limiter.check_rate_limit(client_id)
        if not allowed:
            logger.warning(f"Rate limit exceeded for client {client_id}: {reason}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please slow down."}
            )

        user_agent = request.headers.get("user-agent", "").lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern in user_agent and "python" in user_agent:
                client = self.rate_limiter._clients.get(client_id)
                if client:
                    client.suspicious_patterns += 1
                    if client.suspicious_patterns > 10:
                        client.blocked = True
                        logger.warning(f"Blocked suspicious client {client_id}")

        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"

        return response


class IPBlocklist:
    def __init__(self):
        self._blocked_ips: Set[str] = set()
        self._suspicious_ips: Dict[str, int] = defaultdict(int)

    def block_ip(self, ip: str, reason: str = ""):
        self._blocked_ips.add(ip)
        logger.warning(f"Blocked IP {ip}: {reason}")

    def unblock_ip(self, ip: str):
        self._blocked_ips.discard(ip)

    def is_blocked(self, ip: str) -> bool:
        return ip in self._blocked_ips

    def add_suspicious(self, ip: str, threat_level: int = 1):
        self._suspicious_ips[ip] += threat_level
        if self._suspicious_ips[ip] > 10:
            self.block_ip(ip, "Exceeded suspicious activity threshold")

    def get_threat_level(self, ip: str) -> ThreatLevel:
        score = self._suspicious_ips.get(ip, 0)
        if score < 3:
            return ThreatLevel.LOW
        elif score < 6:
            return ThreatLevel.MEDIUM
        elif score < 10:
            return ThreatLevel.HIGH
        return ThreatLevel.CRITICAL


class SecurityMonitor:
    def __init__(self):
        self.ip_blocklist = IPBlocklist()
        self.rate_limiter = RateLimiter()
        self._request_log: list = []
        self._max_log_size = 10000

    def log_request(self, client_id: str, path: str, method: str, status_code: int):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "client_id": client_id,
            "path": path,
            "method": method,
            "status": status_code,
        }
        self._request_log.append(entry)

        if len(self._request_log) > self._max_log_size:
            self._request_log = self._request_log[-self._max_log_size:]

        if status_code >= 500:
            self.ip_blocklist.add_suspicious(client_id, 3)
        elif status_code >= 400:
            self.ip_blocklist.add_suspicious(client_id, 1)

    def get_stats(self) -> dict:
        total_requests = len(self._request_log)
        blocked_ips = len(self.ip_blocklist._blocked_ips)

        status_codes = defaultdict(int)
        for entry in self._request_log:
            status_codes[entry["status"]] += 1

        return {
            "total_requests": total_requests,
            "blocked_ips": blocked_ips,
            "active_rate_limiters": len(self.rate_limiter._clients),
            "status_codes": dict(status_codes),
            "recent_requests": self._request_log[-10:],
        }


security_monitor = SecurityMonitor()
