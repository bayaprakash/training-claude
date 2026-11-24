"""Collect Linux metrics over SSH using fixed remote commands only."""
from __future__ import annotations

import re
import time
from typing import Any

import paramiko

CMD_CPU = (
    "A=$(awk '/^cpu /{print $2+$3+$4+$5+$6+$7+$8,$5}' /proc/stat); "
    "sleep 0.5; "
    "B=$(awk '/^cpu /{print $2+$3+$4+$5+$6+$7+$8,$5}' /proc/stat); "
    "echo \"$A|$B\""
)
CMD_MEMORY = "free -b | awk '/Mem:/{print $2,$3,$4}'"
CMD_NETWORK = (
    "awk -F'[: ]+' 'NR>2 {rx+=$3; tx+=$11} END {print rx+0, tx+0}' /proc/net/dev"
)
CMD_PORTS = "ss -tlnH 2>/dev/null || netstat -tln 2>/dev/null"


def _unreachable(hostname: str, error: str) -> dict[str, Any]:
    return {
        "status": "unreachable",
        "hostname": hostname,
        "error": error,
        "cpu": {"percent": None},
        "memory": {"total": 0, "used": 0, "free": 0, "percent": None},
        "network": {"bytes_recv": 0, "bytes_sent": 0},
        "ports": [],
        "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _connect(
    hostname: str,
    port: int,
    username: str,
    auth_type: str,
    credential: str,
    timeout: int = 8,
) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    kwargs: dict[str, Any] = {
        "hostname": hostname,
        "port": port,
        "username": username,
        "timeout": timeout,
        "allow_agent": False,
        "look_for_keys": False,
    }
    if auth_type == "key":
        kwargs["key_filename"] = credential
    else:
        kwargs["password"] = credential
    client.connect(**kwargs)
    return client


def _exec(client: paramiko.SSHClient, command: str, timeout: int = 12) -> str:
    _stdin, stdout, _stderr = client.exec_command(command, timeout=timeout)
    return stdout.read().decode(errors="ignore").strip()


def parse_cpu(sample: str) -> float:
    parts = sample.split("|")
    if len(parts) != 2:
        return 0.0
    try:
        a_total, a_idle = [int(x) for x in parts[0].split()]
        b_total, b_idle = [int(x) for x in parts[1].split()]
    except ValueError:
        return 0.0
    delta_total = b_total - a_total
    delta_idle = b_idle - a_idle
    if delta_total <= 0:
        return 0.0
    return round(max(0.0, (delta_total - delta_idle) / delta_total * 100.0), 1)


def parse_memory(output: str) -> dict[str, Any]:
    parts = output.split()
    if len(parts) < 3:
        return {"total": 0, "used": 0, "free": 0, "percent": 0.0}
    total, used, free = int(parts[0]), int(parts[1]), int(parts[2])
    percent = round(used / total * 100, 1) if total else 0.0
    return {"total": total, "used": used, "free": free, "percent": percent}


def parse_network(output: str) -> dict[str, int]:
    parts = output.split()
    if len(parts) < 2:
        return {"bytes_recv": 0, "bytes_sent": 0}
    try:
        return {"bytes_recv": int(parts[0]), "bytes_sent": int(parts[1])}
    except ValueError:
        return {"bytes_recv": 0, "bytes_sent": 0}


def parse_ports(output: str) -> list[dict[str, Any]]:
    ports: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in output.splitlines():
        match = re.search(r"(\S+):(\d+)\s", line + " ")
        if match:
            address = f"{match.group(1)}:{match.group(2)}"
            if address in seen:
                continue
            seen.add(address)
            ports.append(
                {"port": int(match.group(2)), "address": address, "state": "LISTEN"}
            )
            continue
        if "LISTEN" in line.upper():
            port_match = re.search(r":(\d+)\s", line)
            if not port_match:
                continue
            key = port_match.group(1)
            if key in seen:
                continue
            seen.add(key)
            ports.append({"port": int(key), "address": f"*:{key}", "state": "LISTEN"})
    return ports


def collect_ssh_metrics(server: dict[str, Any]) -> dict[str, Any]:
    hostname = server["hostname"]
    try:
        client = _connect(
            hostname=hostname,
            port=int(server["ssh_port"]),
            username=server["ssh_username"],
            auth_type=server.get("auth_type") or "password",
            credential=server.get("credential") or "",
        )
    except (OSError, paramiko.SSHException, ValueError):
        return _unreachable(hostname, "SSH connection failed")

    try:
        try:
            cpu_raw = _exec(client, CMD_CPU)
            mem_raw = _exec(client, CMD_MEMORY)
            net_raw = _exec(client, CMD_NETWORK)
            ports_raw = _exec(client, CMD_PORTS)
        except (OSError, paramiko.SSHException, TimeoutError):
            return _unreachable(hostname, "SSH command failed")
    finally:
        client.close()

    return {
        "status": "online",
        "hostname": hostname,
        "cpu": {"percent": parse_cpu(cpu_raw)},
        "memory": parse_memory(mem_raw),
        "network": parse_network(net_raw),
        "ports": parse_ports(ports_raw),
        "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
