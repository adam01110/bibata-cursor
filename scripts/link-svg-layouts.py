#!/usr/bin/env python3

import os
from pathlib import Path


SVG_ROOT = Path(__file__).resolve().parent.parent / "svg"


def generate_symlinks(source_dirs: list[Path], destination: Path) -> None:
    destination.mkdir(exist_ok=True)

    for source_dir in source_dirs:
        for source in source_dir.iterdir():
            link = destination / source.name
            link.unlink(missing_ok=True)

            print(f"Creating symlink for {link.relative_to(SVG_ROOT)}")
            link.symlink_to(os.path.relpath(source, destination))


def main() -> None:
    layouts = {
        "modern": ["modern", "modern-arrow", "shared", "hand"],
        "modern-right": ["modern-right", "modern-arrow", "shared", "hand-right"],
        "original": ["original", "original-arrow", "shared", "hand"],
        "original-right": [
            "original-right",
            "original-arrow",
            "shared",
            "hand-right",
        ],
    }

    for destination, source_dirs in layouts.items():
        generate_symlinks(
            [SVG_ROOT / "groups" / source_dir for source_dir in source_dirs],
            SVG_ROOT / destination,
        )


if __name__ == "__main__":
    main()
