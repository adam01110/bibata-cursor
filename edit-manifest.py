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
        shape = "Modern" if theme_name.split("-")[1] == "Modern" else "Original"
        if theme_name.endswith("-Classic"):
            desc += "Black and " + shape + " Bibata cursors"
        elif theme_name.endswith("-RosePine"):
            desc += "Rose Pine and " + shape + " Bibata cursors"
        elif theme_name.endswith("-Gruvbox"):
            desc += "Gruvbox and " + shape + " Bibata cursors"
        for line in content:
            if not line.startswith("name = Extracted Theme") and not line.startswith("description = Automatically extracted with hyprcursor-util"):
                f.write(line)
            else:
                if line.startswith("name = Extracted Theme"):
                    f.write("name = " + theme_name + "\n")
                elif line.startswith("description = Automatically extracted with hyprcursor-util"):
                    f.write("description = " + desc + "\n")

if __name__ == '__main__':
    main()
