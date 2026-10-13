#!/usr/bin/env python3

import argparse
import json
import shutil
from pathlib import Path

from svg_cursors import NOMINAL_SIZE, ROOT, load_cursors, selected_themes, write_frames


def build_theme(theme_name: str, renderer: dict, output_root: Path) -> Path:
    cursors = load_cursors(theme_name, renderer)
    theme = output_root / theme_name
    scalable = theme / "cursors_scalable"
    if scalable.exists():
        shutil.rmtree(scalable)
    scalable.mkdir(parents=True)
    for cursor in cursors:
        destination = scalable / cursor.name
        write_frames(cursor, destination)
        metadata = []
        for frame in cursor.frames:
            entry = {
                "filename": frame.filename,
                "hotspot_x": cursor.hotspot_x,
                "hotspot_y": cursor.hotspot_y,
                "nominal_size": NOMINAL_SIZE,
            }
            if frame.delay is not None:
                entry["delay"] = frame.delay
            metadata.append(entry)
        (destination / "metadata.json").write_text(
            json.dumps(metadata, indent=2) + "\n"
        )
        for alias in cursor.aliases:
            (scalable / alias).symlink_to(cursor.name)
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
    for name, renderer in selected_themes(parser, args.theme).items():
        build_theme(name, renderer, args.output)
        print(f"Built {name}/cursors_scalable")


if __name__ == "__main__":
    main()
