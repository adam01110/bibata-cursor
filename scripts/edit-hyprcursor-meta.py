import os.path
import re
import sys


def rewrite_metadata(content: str, svg_files: list[str]) -> str:
    definitions = [
        line for line in content.splitlines() if line.startswith("define_size = ")
    ]
    if not definitions:
        raise ValueError("No define_size entries in Hyprcursor metadata")
    fields = definitions[0].split("=", 1)[1].split(",")
    delay = fields[2].strip() if len(fields) > 2 else None
    filenames = sorted(
        (
            os.path.basename(svg)
            for argument in svg_files
            for svg in argument.splitlines()
        ),
        key=lambda name: [
            int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)
        ],
    )
    if not filenames:
        raise ValueError("No SVG frames supplied")
    replacement = "".join(
        f"define_size = 0, {name}" + (f", {delay}" if delay else "") + "\n"
        for name in filenames
    )
    result = []
    written = False
    for line in content.splitlines(keepends=True):
        if not line.startswith("define_size = "):
            result.append(line)
        elif not written:
            result.append(replacement)
            written = True
    return "".join(result)


def main():
    metahl, *svg_files = sys.argv[1:]
    with open(metahl) as source:
        content = rewrite_metadata(source.read(), svg_files)
    with open(metahl, "w") as destination:
        destination.write(content)


if __name__ == "__main__":
    main()
