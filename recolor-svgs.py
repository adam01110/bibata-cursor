import os
import json


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
        data = json.load(f)
        for theme in data:
            if not theme.endswith("-Right"):
                    
                theme_name = theme
                svgs_dir = data[theme]["dir"]
                output = "hyprcursor-build/recolored_svgs/" + theme_name
                os.system("mkdir -p " + output)
                colors = []
                for color in data[theme]["colors"]:
                    colors.append((color["match"], color["replace"]))
                renderers.append(Renderer(svgs_dir, output, theme_name, colors))
        
        f.close()


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