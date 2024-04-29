import sys


def main():
    args = sys.argv[1:]
    metahl = args[0]
    theme_name = args[1]
    with open(metahl, 'r+') as f:
        content = f.readlines()
        f.seek(0)
        f.truncate()
        desc = "Hyprcursor version of bibata. "
        shape = "rounded" if theme_name.split("-")[1] == "Modern" else "sharp"
        if theme_name.endswith("-Amber"):
            desc += "Yellowish and " + shape + " edge Bibata cursors"
        elif theme_name.endswith("-Ice"):
            desc += "White and " + shape + " edge Bibata cursors"
        elif theme_name.endswith("-Classic"):
            desc += "Black and " + shape + " edge Bibata cursors"
        for line in content:
            if not line.startswith("name = Extracted Theme") and not line.startswith("description = Automatically extracted with hyprcursor-util"):
                f.write(line)
            else:
                if line.startswith("name = Extracted Theme"):
                    f.write("name = Hypr-" + theme_name + "\n")
                elif line.startswith("description = Automatically extracted with hyprcursor-util"):
                    f.write("description = " + desc + "\n")


if __name__ == '__main__':
    main()