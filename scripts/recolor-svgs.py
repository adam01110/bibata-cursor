#!/usr/bin/env python3

import json
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
RENDER_CONFIG = REPOSITORY_ROOT / "render.json"
OUTPUT_ROOT = REPOSITORY_ROOT / "hyprcursor-build" / "recolored_svgs"


def recolor_directory(
    source_directory: Path,
    output_directory: Path,
    colors: list[tuple[str, str]],
) -> None:
    for source in source_directory.iterdir():
        output = output_directory / source.name

        if source.is_dir():
            recolor_directory(source, output, colors)
        elif source.suffix == ".svg":
            output.parent.mkdir(parents=True, exist_ok=True)
            content = source.read_text()
            for source_color, output_color in colors:
                content = content.replace(source_color, output_color)
            output.write_text(content)


def main() -> None:
    renderers = json.loads(RENDER_CONFIG.read_text())

    for theme_name, renderer in renderers.items():
        source_directory = REPOSITORY_ROOT / renderer["dir"]
        output_directory = OUTPUT_ROOT / theme_name
        colors = [(color["match"], color["replace"]) for color in renderer["colors"]]
        recolor_directory(source_directory, output_directory, colors)


if __name__ == "__main__":
    main()
