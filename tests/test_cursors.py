import importlib.util
import json
import sys
import tempfile
import tomllib
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CursorTests(unittest.TestCase):
    def test_scalable_themes(self):
        builder = load_script("build-scalable")
        renderers = json.loads((ROOT / "render.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            for name, renderer in renderers.items():
                theme = builder.build_theme(name, renderer, Path(directory))
                scalable = theme / "cursors_scalable"
                for alias in scalable.iterdir():
                    self.assertTrue(alias.exists(), alias)
                for metadata_file in scalable.glob("*/metadata.json"):
                    frames = json.loads(metadata_file.read_text())
                    for frame in frames:
                        svg = metadata_file.parent / frame["filename"]
                        ET.parse(svg)
                        self.assertEqual(frame["nominal_size"], 256)
                        self.assertNotIn('fill="#fe0000"', svg.read_text())
                    if metadata_file.parent.name in (
                        "wait",
                        "left_ptr_watch",
                        "progress",
                        "watch",
                    ):
                        self.assertEqual(len(frames), 54)
                        self.assertEqual(sum(frame["delay"] for frame in frames), 2160)
                self.assertEqual((scalable / "pointer").resolve(), scalable / "hand2")
                if name.endswith("-Right"):
                    for shape, x in (
                        ("pencil", 211),
                        ("zoom-in", 140),
                        ("zoom-out", 140),
                    ):
                        metadata = json.loads(
                            (scalable / shape / "metadata.json").read_text()
                        )
                        self.assertEqual(metadata[0]["hotspot_x"], x)
                # Regeneration must preserve existing Xcursor fallback assets.
                (theme / "cursors").mkdir(exist_ok=True)
                (theme / "cursors" / "sentinel").write_text("fallback")
                builder.build_theme(name, renderer, Path(directory))
                self.assertEqual(
                    (theme / "cursors" / "sentinel").read_text(), "fallback"
                )

    def test_hyprcursor_matches_scalable(self):
        scalable_builder = load_script("build-scalable")
        hypr_builder = load_script("build-hyprcursor")
        renderers = json.loads((ROOT / "render.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            for name, renderer in renderers.items():
                scalable = scalable_builder.build_theme(
                    name, renderer, Path(directory) / "svg"
                )
                hypr = hypr_builder.write_theme(
                    name, renderer, Path(directory) / "hypr", "2.0.3"
                )
                self.assertIn(f"name = {name}\n", (hypr / "manifest.hl").read_text())
                self.assertIn("version = 2.0.3\n", (hypr / "manifest.hl").read_text())
                for shape in (hypr / "hyprcursors").iterdir():
                    metadata = json.loads(
                        (
                            scalable / "cursors_scalable" / shape.name / "metadata.json"
                        ).read_text()
                    )
                    meta = (shape / "meta.hl").read_text().splitlines()
                    self.assertIn(f"hotspot_x = {metadata[0]['hotspot_x'] / 256}", meta)
                    self.assertIn(f"hotspot_y = {metadata[0]['hotspot_y'] / 256}", meta)
                    definitions = [
                        line for line in meta if line.startswith("define_size = ")
                    ]
                    self.assertEqual(len(definitions), len(metadata))
                    for entry, definition in zip(metadata, definitions, strict=True):
                        expected = f"define_size = 0, {entry['filename']}"
                        if "delay" in entry:
                            expected += f", {entry['delay']}"
                        self.assertEqual(definition, expected)
                        self.assertEqual(
                            (shape / entry["filename"]).read_text(),
                            (
                                scalable
                                / "cursors_scalable"
                                / shape.name
                                / entry["filename"]
                            ).read_text(),
                        )
                    for alias in (
                        line.split(" = ", 1)[1]
                        for line in meta
                        if line.startswith("define_override = ")
                    ):
                        self.assertEqual(
                            (scalable / "cursors_scalable" / alias).resolve().name,
                            shape.name,
                        )
                self.assertIn(
                    "define_override = pointer",
                    (hypr / "hyprcursors" / "hand2" / "meta.hl").read_text(),
                )

    def test_bitmap_sources_include_windows_shapes(self):
        from svg_cursors import load_cursors

        renderers = json.loads((ROOT / "render.json").read_text())
        name = "Bibata-Modern-Classic"
        cursors = load_cursors(name, renderers[name], include_windows=True)
        by_name = {cursor.name: cursor for cursor in cursors}
        self.assertEqual(len(by_name), 58)
        self.assertEqual(by_name["person"].frames[0].filename, "person.svg")
        self.assertEqual(by_name["pin"].frames[0].filename, "pin.svg")
        self.assertEqual(len(by_name["wait"].frames), 54)

    def test_numeric_frame_order(self):
        from svg_cursors import frame_order

        frames = [Path("wait-10.svg"), Path("wait-2.svg"), Path("wait-1.svg")]
        self.assertEqual(
            [frame.name for frame in sorted(frames, key=frame_order)],
            ["wait-1.svg", "wait-2.svg", "wait-10.svg"],
        )

    def test_layouts_and_hotspots(self):
        for layout in ("modern", "original", "modern-right", "original-right"):
            group = "misc-right" if layout.endswith("-right") else "misc"
            for shape in ("pencil", "zoom-in", "zoom-out"):
                self.assertEqual(
                    (ROOT / "svg" / layout / f"{shape}.svg").resolve(),
                    ROOT / "svg" / "groups" / group / f"{shape}.svg",
                )
        for config_name in ("build.toml", "build.right.toml"):
            config = tomllib.loads((ROOT / config_name).read_text())
            self.assertIn("pointer", config["cursors"]["hand2"]["x11_symlinks"])


if __name__ == "__main__":
    unittest.main()
