#!/usr/bin/env python3

import argparse
import subprocess
import tempfile
from pathlib import Path

from svg_cursors import NOMINAL_SIZE, ROOT, load_cursors, selected_themes, write_frames


def build_theme(theme_name: str, renderer: dict, output_root: Path) -> Path:
    cursors = load_cursors(theme_name, renderer, include_windows=True)
    output = output_root / theme_name
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bibata-bitmaps-") as directory:
        for cursor in cursors:
            source = Path(directory) / cursor.name
            write_frames(cursor, source)
            for frame in cursor.frames:
                subprocess.run(
                    [
                        "resvg",
                        "--width",
                        str(NOMINAL_SIZE),
                        "--height",
                        str(NOMINAL_SIZE),
                        str(source / frame.filename),
                        str(output / Path(frame.filename).with_suffix(".png")),
                    ],
                    check=True,
                )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render static SVG frames with resvg for ctgen"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "bitmaps")
    parser.add_argument("--theme", help="Build only this render.json theme")
    args = parser.parse_args()
    for name, renderer in selected_themes(parser, args.theme).items():
        build_theme(name, renderer, args.output)
        print(f"Rendered {name} bitmaps")


if __name__ == "__main__":
    main()
