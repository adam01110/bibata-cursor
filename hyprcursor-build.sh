#!/usr/bin/env bash

rm -rf hyprcursor-build

mkdir -p hyprcursor-build

for theme in $(find ./bin -maxdepth 1 -type d | grep "Bibata-*"); do
  hyprcursor-util --extract "$theme" --output "hyprcursor-build"
done

python3 recolor-svgs.py

for theme in $(find ./hyprcursor-build -maxdepth 1 -type d | grep "extracted_Bibata-*"); do
  theme_name=$(basename "$theme")
  theme_base=$(echo "$theme_name" | cut -d'_' -f2)
  for shape in $(find "$theme/hyprcursors/" -maxdepth 1 -mindepth 1 -type d); do
    shape_name=$(basename "$shape")
    svg_files=$(find "./hyprcursor-build/recolored_svgs/$theme_base/" -name "$shape_name.svg" | grep "$shape_name")
    if [ -z "$svg_files" ]; then
        if [ "$shape_name" == "wait" ]; then
            svg_files=$(find "./hyprcursor-build/recolored_svgs/$theme_base/wait/" -name "*.svg")
        elif [ "$shape_name" == "left_ptr_watch" ]; then
            svg_files=$(find "./hyprcursor-build/recolored_svgs/$theme_base/left_ptr_watch/" -name "*.svg")
        fi
    fi
    echo "$theme_base: $shape_name -> $svg_files"
    if [ -z "$svg_files" ]; then
        # echo "No SVG file found for $theme_base: $shape_name"
        exit 1
    fi

    png_files=$(find "$shape" -name "*.png")
    for png_file in $png_files; do
      rm "$png_file"
    done
    meta_file=$(find "$shape" -name "meta.hl")
    python3 edit-meta.py "$meta_file" "$svg_files"
    for svg_file in $svg_files; do
      mv "$svg_file" "$shape"
    done
  done
done

for theme in $(find ./hyprcursor-build/ -maxdepth 1 -type d | grep "extracted_Bibata-*"); do
  manifest_file=$(find "$theme" -name "manifest.hl")
  python3 edit-manifest.py "$manifest_file" "$(basename "$theme" | cut -d'_' -f2)"
  hyprcursor-util --create "$theme" --output "hyprcursor-build"
done

for theme_dir in $(find ./hyprcursor-build -maxdepth 1 -type d | grep "theme_Bibata-*"); do
  theme_base_name=$(basename "$theme_dir" | cut -d'_' -f2)
  new_name="${theme_base_name}-hyprcursor"
  echo "Moving $theme_dir to bin/$new_name"
  cp -rf "$theme_dir" "bin/$new_name"
done
