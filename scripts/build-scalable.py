#!/usr/bin/env python3

import argparse
import json
import re
import shutil
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build_theme(theme_name: str, renderer: dict, output_root: Path) -> Path:
    config_name = "build.right.toml" if theme_name.endswith("-Right") else "build.toml"
    config = tomllib.loads((ROOT / config_name).read_text())
    defaults = config["cursors"]["fallback_settings"]
    theme = output_root / theme_name
    scalable = theme / "cursors_scalable"
    if scalable.exists():
        shutil.rmtree(scalable)
    scalable.mkdir(parents=True)
    colors = {color["match"]: color["replace"] for color in renderer["colors"]}
    pattern = re.compile("|".join(re.escape(color) for color in colors))
    aliases = {}
    for cursor in config["cursors"].values():
        name = cursor.get("x11_name")
        if not name:
            continue
        source = ROOT / renderer["dir"]
        png = cursor["png"]
        animated = "*" in png
        if animated:
            source = source / png.split("-*")[0]
            frames = sorted(source.glob("*.svg"))
        else:
            frames = [source / Path(png).with_suffix(".svg")]
        if not frames:
            raise ValueError(f"No SVG frames for {theme_name}/{name}")
        destination = scalable / name
        destination.mkdir()
        metadata = []
        for frame in frames:
            content = pattern.sub(
                lambda match: colors[match.group()], frame.read_text()
            )
            (destination / frame.name).write_text(content)
            entry = {
                "filename": frame.name,
                "hotspot_x": cursor.get("x_hotspot", defaults["x_hotspot"]),
                "hotspot_y": cursor.get("y_hotspot", defaults["y_hotspot"]),
                "nominal_size": 256,
            }
            if animated:
                entry["delay"] = cursor.get("x11_delay", defaults["x11_delay"])
            metadata.append(entry)
        (destination / "metadata.json").write_text(
            json.dumps(metadata, indent=2) + "\n"
        )
        for alias in cursor.get("x11_symlinks", []):
            aliases[alias] = name
    for alias, target in aliases.items():
        (scalable / alias).symlink_to(target)
    index = theme / "index.theme"
    if not index.exists():
        index.write_text(
            f"[Icon Theme]\nName={theme_name}\nComment=Scalable Bibata cursors\n"
        )
    return theme


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build KDE/GNOME scalable SVG cursor themes"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "bin")
    parser.add_argument("--theme", help="Build only this render.json theme")
    args = parser.parse_args()
    renderers = json.loads((ROOT / "render.json").read_text())
    if args.theme and args.theme not in renderers:
        parser.error(f"Unknown theme: {args.theme}")
    for name, renderer in renderers.items():
        if args.theme is None or name == args.theme:
            build_theme(name, renderer, args.output)
            print(f"Built {name}/cursors_scalable")


if __name__ == "__main__":
    main()
