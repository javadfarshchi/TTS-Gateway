#!/usr/bin/env python3
"""Download Kokoro ONNX assets required by the gateway."""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Iterable
from urllib.request import urlopen

ASSETS = {
    "kokoro-v1.0.onnx": {
        "url": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
        "sha256": "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5",
    },
    "voices-v1.0.bin": {
        "url": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
        "sha256": "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
    },
}

DEFAULT_DEST = Path("models/kokoro")


def download_file(url: str, dest: Path) -> None:
    """Download *url* to *dest* streaming the response to disk."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url) as response, dest.open("wb") as handle:  # type: ignore[arg-type]
        chunk = response.read(1024 * 1024)
        while chunk:
            handle.write(chunk)
            chunk = response.read(1024 * 1024)


def verify_checksum(path: Path, expected_sha256: str) -> bool:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest() == expected_sha256


def ensure_assets(
    dest_root: Path, force: bool = False, assets: Iterable[str] | None = None
) -> None:
    targets = list(assets) if assets else list(ASSETS.keys())
    for name in targets:
        meta = ASSETS.get(name)
        if not meta:
            raise ValueError(f"Unknown asset '{name}'. Choose from: {', '.join(ASSETS)}")

        target = dest_root / name
        if target.exists() and not force:
            print(f"✔ {name} already exists at {target}")
        else:
            print(f"⬇ Downloading {name} → {target}")
            download_file(meta["url"], target)

        expected = meta.get("sha256")
        if expected:
            print(f"⏳ Verifying {name} checksum…", end=" ")
            if verify_checksum(target, expected):
                print("ok")
            else:
                raise RuntimeError(
                    f"Checksum mismatch for {name}. Remove the file and rerun the script."
                )

    print("Kokoro assets are ready.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download Kokoro ONNX model assets.")
    parser.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DEST,
        help="Directory to store the downloaded assets (default: models/kokoro).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download assets even if they already exist.",
    )
    parser.add_argument(
        "assets",
        nargs="*",
        help="Optional list of asset filenames to download (defaults to all).",
    )

    args = parser.parse_args(argv)

    try:
        ensure_assets(dest_root=args.dest, force=args.force, assets=args.assets)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
