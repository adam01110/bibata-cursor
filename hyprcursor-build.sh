# !/bin/bash

rm -rf hyprcursor-build

mkdir -p hyprcursor-build

for theme in $(find ./themes -maxdepth 1 -type d | grep "Bibata-*"); do
  theme_name=$(basename "$theme")
  hyprcursor-util --extract "$theme" --output "hyprcursor-build"
done

python3 recolor-svgs.py

for theme in $(find ./hyprcursor-build -maxdepth 1 -type d | grep "extracted_Bibata-*"); do
  theme_name=$(basename "$theme")
  for shape in $(find "$theme/hyprcursors" -maxdepth 2 -type d); do
    shape_name=$(basename "$shape")
    svg_file=$(find "./hyprcursor-build/recolored_svgs/$theme_base" -name "$shape_name.svg" | grep "$shape_name")
    theme_base=$(echo "$theme_name" | cut -d'_' -f2)
    if [ -z "$svg_file" ]; then
        if [ "$shape_name" == "wait" ]; then
            svg_file=$(find "./hyprcursor-build/recolored_svgs/$theme_base/wait/" -name "*.svg")
        elif [ "$shape_name" == "left_ptr_watch" ]; then
            svg_file=$(find "./hyprcursor-build/recolored_svgs/$theme_namebase/left_ptr_watch/" -name "*.svg")
        fi
    fi
    echo "$theme_base: $shape_name -> $svg_file"
    if [ -z "$svg_file" ]; then
        echo "No SVG file found for $theme_base: $shape_name"
        exit 1
    fi

    # TODO: edit the meta.hl file
    # TODO: copy the svg files to the extracted hyprcursor
    
  done
done