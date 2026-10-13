#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from svg_cursors import NOMINAL_SIZE, ROOT, load_cursors, selected_themes, write_frames


def write_theme(
    theme_name: str, renderer: dict, output_root: Path, version: str
) -> Path:
    cursors = load_cursors(theme_name, renderer)
    theme = output_root / theme_name
    theme.mkdir(parents=True)
    (theme / "manifest.hl").write_text(
        f"name = {theme_name}\n"
        f"description = SVG Hyprcursor version of {theme_name}\n"
        f"version = {version}\ncursors_directory = hyprcursors\n"
    )
    for cursor in cursors:
        destination = theme / "hyprcursors" / cursor.name
        write_frames(cursor, destination)
        lines = [
            "resize_algorithm = bilinear",
            f"hotspot_x = {cursor.hotspot_x / NOMINAL_SIZE}",
            f"hotspot_y = {cursor.hotspot_y / NOMINAL_SIZE}",
        ]
        lines.extend(f"define_override = {alias}" for alias in cursor.aliases)
        for frame in cursor.frames:
            definition = f"define_size = 0, {frame.filename}"
            if frame.delay is not None:
                definition += f", {frame.delay}"
            lines.append(definition)
        (destination / "meta.hl").write_text("\n".join(lines) + "\n")
    return theme


def build_theme(
    theme_name: str,
    renderer: dict,
    output_root: Path,
    version: str,
    utility: str = "hyprcursor-util",
) -> Path:
    with tempfile.TemporaryDirectory(prefix="bibata-hyprcursor-") as directory:
        workspace = Path(directory)
        source = write_theme(theme_name, renderer, workspace / "source", version)
        compiled = workspace / "compiled"
        compiled.mkdir()
        subprocess.run(
            [utility, "--create", str(source), "--output", str(compiled)],
            stdin=subprocess.DEVNULL,
            check=True,
        )
        output = output_root / f"{theme_name}-hyprcursor"
        if output.exists():
            shutil.rmtree(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(compiled / f"theme_{theme_name}", output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Hyprcursor themes directly from SVG"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "bin")
    parser.add_argument("--theme", help="Build only this render.json theme")
    parser.add_argument("--version", default="1.0")
    args = parser.parse_args()
    for name, renderer in selected_themes(parser, args.theme).items():
        build_theme(name, renderer, args.output, args.version)
        print(f"Built {name}-hyprcursor")


if __name__ == "__main__":
    main()
