#!/usr/bin/env python3

import argparse
from pathlib import Path


PALETTE_NAMES = {
    "Catppuccin-Frappe": "Catppuccin Frappé",
    "Catppuccin-Latte": "Catppuccin Latte",
    "Catppuccin-Macchiato": "Catppuccin Macchiato",
    "Catppuccin-Mocha": "Catppuccin Mocha",
    "Classic": "Classic",
    "Gruvbox-Dark": "Gruvbox Dark",
    "Gruvbox-Light": "Gruvbox Light",
    "Rosepine": "Rosé Pine",
    "Rosepine-Dawn": "Rosé Pine Dawn",
    "Rosepine-Moon": "Rosé Pine Moon",
}


def describe_theme(theme_name: str) -> str:
    parts = theme_name.split("-")
    if (
        len(parts) < 3
        or parts[0] != "Bibata"
        or parts[1]
        not in {
            "Modern",
            "Original",
        }
    ):
        raise ValueError(f"unsupported Bibata theme name: {theme_name}")

    shape = parts[1]
    palette_parts = parts[2:]
    if palette_parts[-1] == "Right":
        shape += " Right"
        palette_parts = palette_parts[:-1]

    palette_key = "-".join(palette_parts)
    palette = PALETTE_NAMES.get(palette_key, palette_key.replace("-", " "))
    return f"Hyprcursor version of Bibata. {palette} {shape} Bibata cursors"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("theme_name")
    args = parser.parse_args()

    description = describe_theme(args.theme_name)
    lines = args.manifest.read_text().splitlines(keepends=True)

    with args.manifest.open("w") as manifest:
        for line in lines:
            if line.startswith("name = Extracted Theme"):
                manifest.write(f"name = {args.theme_name}\n")
            elif line.startswith(
                "description = Automatically extracted with hyprcursor-util"
            ):
                manifest.write(f"description = {description}\n")
            else:
                manifest.write(line)


if __name__ == "__main__":
    main()
