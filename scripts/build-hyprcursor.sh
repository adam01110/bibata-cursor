#!/usr/bin/env bash

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(dirname "$script_dir")
cd "$repo_root" || exit 1

rm -rf hyprcursor-build
mkdir -p hyprcursor-build

while IFS= read -r theme; do
  hyprcursor-util --extract "$theme" --output hyprcursor-build
done < <(find ./bin -maxdepth 1 -type d -name "Bibata-*")

python3 "$script_dir/recolor-svgs.py"

while IFS= read -r theme; do
  theme_name=$(basename "$theme")
  theme_base=${theme_name#*_}

  while IFS= read -r shape; do
    shape_name=$(basename "$shape")
    svg_files=$(find "./hyprcursor-build/recolored_svgs/$theme_base/" -name "$shape_name.svg")

    if [[ -z $svg_files ]]; then
      case "$shape_name" in
      wait | left_ptr_watch)
        svg_files=$(find "./hyprcursor-build/recolored_svgs/$theme_base/$shape_name/" -name "*.svg")
        ;;
      esac
    fi

    echo "$theme_base: $shape_name -> $svg_files"
    if [[ -z $svg_files ]]; then
      exit 1
    fi

    while IFS= read -r png_file; do
      rm "$png_file"
    done < <(find "$shape" -name "*.png")

    meta_file=$(find "$shape" -name "meta.hl")
    python3 "$script_dir/edit-hyprcursor-meta.py" "$meta_file" "$svg_files"

    while IFS= read -r svg_file; do
      mv "$svg_file" "$shape"
    done <<<"$svg_files"
  done < <(find "$theme/hyprcursors/" -maxdepth 1 -mindepth 1 -type d)
done < <(find ./hyprcursor-build -maxdepth 1 -type d -name "extracted_Bibata-*")

while IFS= read -r theme; do
  manifest_file=$(find "$theme" -name "manifest.hl")
  theme_name=$(basename "$theme")
  python3 "$script_dir/edit-hyprcursor-manifest.py" "$manifest_file" "${theme_name#*_}"
  hyprcursor-util --create "$theme" --output hyprcursor-build
done < <(find ./hyprcursor-build -maxdepth 1 -type d -name "extracted_Bibata-*")

while IFS= read -r theme_dir; do
  theme_name=$(basename "$theme_dir")
  theme_base_name=${theme_name#*_}
  new_name="${theme_base_name}-hyprcursor"
  echo "Moving $theme_dir to bin/$new_name"
  cp -rf "$theme_dir" "bin/$new_name"
done < <(find ./hyprcursor-build -maxdepth 1 -type d -name "theme_Bibata-*")
