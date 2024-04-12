import sys

def main():
    args = sys.argv[1:]
    metahl = args[0]
    svg_files = args[1:]

    with open(metahl, 'r+') as f:
        content = f.readlines()
        f.seek(0)
        f.truncate()
        has_written = False
        for line in content:
            if not line.startswith("define_size = "):
                f.write(line)
            elif not has_written:
                content_to_write = ""
                for svg_file in svg_files:
                    for svg in svg_file.split("\n"):
                        content_to_write += "define_size = 0, " + svg.split("/")[len(svg.split("/")) - 1] + "\n"
                f.write(content_to_write)
                has_written = True

if __name__ == '__main__':
    main()