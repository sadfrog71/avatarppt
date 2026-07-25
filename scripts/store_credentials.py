#!/usr/bin/env python3
"""Interactively store an imageavatarppt provider key in macOS Keychain."""

from __future__ import annotations

import argparse
import subprocess
import sys

from credential_store import KEYCHAIN_SERVICES, keychain_account


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider", choices=sorted(KEYCHAIN_SERVICES))
    args = parser.parse_args()

    if sys.platform != "darwin":
        raise SystemExit("Encrypted credential storage currently requires macOS Keychain")
    result = subprocess.run(
        [
            "/usr/bin/security",
            "add-generic-password",
            "-U",
            "-a",
            keychain_account(),
            "-s",
            KEYCHAIN_SERVICES[args.provider],
            "-w",
        ],
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    print(f"Stored {args.provider} credential in macOS Keychain.")


if __name__ == "__main__":
    main()
