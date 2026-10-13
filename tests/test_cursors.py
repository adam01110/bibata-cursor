import importlib.util
import json
import tempfile
import tomllib
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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

    def test_hyprcursor_frame_order_and_delay(self):
        editor = load_script("edit-hyprcursor-meta")
        result = editor.rewrite_metadata(
            "hotspot_x = 0.5\ndefine_size = 24, wait-01.png, 40\n"
            "define_size = 48, wait-01.png, 40\n",
            ["/tmp/wait-10.svg\n/tmp/wait-2.svg\n/tmp/wait-1.svg"],
        )
        self.assertEqual(
            result.splitlines(),
            [
                "hotspot_x = 0.5",
                "define_size = 0, wait-1.svg, 40",
                "define_size = 0, wait-2.svg, 40",
                "define_size = 0, wait-10.svg, 40",
            ],
        )
        with self.assertRaises(ValueError):
            editor.rewrite_metadata("hotspot_x = 0.5\n", ["wait.svg"])

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
