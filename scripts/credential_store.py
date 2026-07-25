#!/usr/bin/env python3
"""Read and write imageavatarppt API keys without plaintext config files."""

from __future__ import annotations

import getpass
import os
import subprocess
import sys


KEYCHAIN_SERVICES = {
    "openai": "imageavatarppt.openai.api-key",
    "minimax": "imageavatarppt.minimax.api-key",
    "kimi": "imageavatarppt.kimi.api-key",
}

ENVIRONMENT_KEYS = {
    "openai": "OPENAI_API_KEY",
    "minimax": "MINIMAX_API_KEY",
    "kimi": "MOONSHOT_API_KEY",
}

ENVIRONMENT_ALIASES = {
    "kimi": ("KIMI_API_KEY", "MOONSHOT_API_KEY"),
}


def keychain_account() -> str:
    return os.environ.get("USER") or getpass.getuser()


def get_provider_secret(provider: str) -> str | None:
    for env_name in ENVIRONMENT_ALIASES.get(provider, (ENVIRONMENT_KEYS[provider],)):
        value = os.environ.get(env_name)
        if value:
            return value
    if sys.platform != "darwin":
        return None

    result = subprocess.run(
        [
            "/usr/bin/security",
            "find-generic-password",
            "-a",
            keychain_account(),
            "-s",
            KEYCHAIN_SERVICES[provider],
            "-w",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    secret = result.stdout.strip()
    return secret or None
