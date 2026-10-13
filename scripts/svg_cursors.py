import argparse
import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOMINAL_SIZE = 256


@dataclass
class Frame:
    filename: str
    content: str
    delay: int | None


@dataclass
class Cursor:
    name: str
    aliases: list[str]
    hotspot_x: int
    hotspot_y: int
    frames: list[Frame]


def frame_order(path: Path) -> list:
    return [
        int(part) if part.isdigit() else part for part in re.split(r"(\d+)", path.name)
    ]


def load_cursors(
    theme_name: str, renderer: dict, root: Path = ROOT, include_windows: bool = False
) -> list[Cursor]:
    config_name = "build.right.toml" if theme_name.endswith("-Right") else "build.toml"
    config = tomllib.loads((root / config_name).read_text())
    defaults = config["cursors"]["fallback_settings"]
    colors = {color["match"]: color["replace"] for color in renderer["colors"]}
    pattern = re.compile("|".join(re.escape(color) for color in colors))
    cursors = []
    for settings in config["cursors"].values():
        name = settings.get("x11_name")
        if not name:
            if not include_windows or "png" not in settings:
                continue
            name = Path(settings["png"]).stem
        source = root / renderer["dir"]
        png = settings["png"]
        animated = "*" in png
        if animated:
            source = source / png.split("-*")[0]
            sources = sorted(source.glob("*.svg"), key=frame_order)
        else:
            sources = [source / Path(png).with_suffix(".svg")]
        if not sources:
            raise ValueError(f"No SVG frames for {theme_name}/{name}")
        delay = settings.get("x11_delay", defaults["x11_delay"]) if animated else None
        if delay is not None and (not isinstance(delay, int) or delay <= 0):
            raise ValueError(f"Invalid frame delay for {theme_name}/{name}: {delay}")
        frames = [
            Frame(
                frame.name,
                pattern.sub(lambda match: colors[match.group()], frame.read_text()),
                delay,
            )
            for frame in sources
        ]
        cursors.append(
            Cursor(
                name,
                settings.get("x11_symlinks", []),
                settings.get("x_hotspot", defaults["x_hotspot"]),
                settings.get("y_hotspot", defaults["y_hotspot"]),
                frames,
            )
        )
    return cursors


def write_frames(cursor: Cursor, destination: Path) -> None:
    destination.mkdir(parents=True)
    for frame in cursor.frames:
        (destination / frame.filename).write_text(frame.content)


def selected_themes(parser: argparse.ArgumentParser, theme_name: str | None) -> dict:
    renderers = json.loads((ROOT / "render.json").read_text())
    if theme_name:
        if theme_name not in renderers:
            parser.error(f"Unknown theme: {theme_name}")
        return {theme_name: renderers[theme_name]}
    return renderers
