import os


class Renderer:
    theme_name = None
    input_folder = None
    output_folder = None
    colors = []

    def __init__(self, input_folder, output_folder, theme_name, colors):
        self.theme_name = theme_name
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.colors = colors


def main():
    render_file = "render.json"
    renderers = []

    with open(render_file, "r") as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            if lines[i].strip().startswith("\"") and lines[i].strip().endswith("\": {"):
                theme_name = lines[i].strip().strip("\"").strip("\": {")
                if not theme_name.endswith("-Right"):
                    svgs_dir = lines[i + 1].replace("\"dir\": \"", "").replace("\",", "").strip()
                    output = "hyprcursor-build/recolored_svgs/" + theme_name
                    os.system("mkdir -p " + output)
                    colors = []
                    color_1_match = lines[i+4].replace("{ \"match\": \"", "").split("\", \"replace\": \"")[0].strip()
                    color_1_replace = lines[i+4].split("\", \"replace\": \"")[1].replace('" },\n', "")
                    color_2_match = lines[i+4].replace("{ \"match\": \"", "").split("\", \"replace\": \"")[0].strip()
                    color_2_replace = lines[i+4].split("\", \"replace\": \"")[1].replace('" },\n', "")
                    color_3_match = lines[i+4].replace("{ \"match\": \"", "").split("\", \"replace\": \"")[0].strip()
                    color_3_replace = lines[i+4].split("\", \"replace\": \"")[1].replace('" },\n', "")
                    colors.append((color_1_match, color_1_replace))
                    colors.append((color_2_match, color_2_replace))
                    colors.append((color_3_match, color_3_replace))
                    theme_type = theme_name.split("-")[2]
                    if theme_type == "Ice":
                        colors.append(("\"#0000FF\"", "\"#000000\""))
                    else:
                        colors.append(("\"#0000FF\"", "\"#FFFFFF\""))
                    renderers.append(Renderer(svgs_dir, output, theme_name, colors))

    for renderer in renderers:
        for root, dirsn, filesn in os.walk(renderer.input_folder):
            for file in filesn:
                if file.endswith(".svg"):
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        for color in renderer.colors:
                            content = content.replace(color[0], color[1])
                        with open(os.path.join(renderer.output_folder, file), "w") as f:
                            f.write(content)
        for root, dirsn, filesn in os.walk(renderer.input_folder + "/wait"):
            for file in filesn:
                if file.endswith(".svg"):
                    os.system("mkdir -p " + renderer.output_folder + "/wait")
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        for color in renderer.colors:
                            content = content.replace(color[0], color[1])
                        with open(os.path.join(renderer.output_folder + "/wait", file), "w") as f:
                            f.write(content)
        for root, dirsn, filesn in os.walk(renderer.input_folder + "/left_ptr_watch"):
            for file in filesn:
                if file.endswith(".svg"):
                    os.system("mkdir -p " + renderer.output_folder + "/left_ptr_watch")
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        for color in renderer.colors:
                            content = content.replace(color[0], color[1])
                        with open(os.path.join(renderer.output_folder + "/left_ptr_watch", file), "w") as f:
                            f.write(content)
            
    
            


if __name__ == "__main__":
    main()