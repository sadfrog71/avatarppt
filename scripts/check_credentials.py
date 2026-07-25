#!/usr/bin/env python3
"""Check provider credential availability without printing secret values."""

from __future__ import annotations

import argparse

from credential_store import KEYCHAIN_SERVICES, get_provider_secret


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "providers",
        nargs="*",
        choices=sorted(KEYCHAIN_SERVICES),
        default=sorted(KEYCHAIN_SERVICES),
    )
    args = parser.parse_args()

    missing = []
    for provider in args.providers:
        available = bool(get_provider_secret(provider))
        print(f"{provider}: {'available' if available else 'missing'}")
        if not available:
            missing.append(provider)
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
