import sys


def main():
    args = sys.argv[1:]
    metahl = args[0]
    theme_name = args[1]
    with open(metahl, 'r+') as f:
        content = f.readlines()
        f.seek(0)
        f.truncate()
        for line in content:
            if not line.startswith("name = Extracted Theme") and not line.startswith("description = Automatically extracted with hyprcursor-util"):
                f.write(line)
            else:
                if line.startswith("name = Extracted Theme"):
                    f.write("name = " + theme_name + "\n")
                elif line.startswith("description = Automatically extracted with hyprcursor-util"):
                    f.write("description = Generated Bibata repository\n")


if __name__ == '__main__':
    main()