<!-- rumdl-disable MD023 MD033 MD041 -->

<div align="center">
  <img src="./assets/modern-classic.png" alt="Bibata Modern Classic" width="96" />
  <img src="./assets/modern-rosepine.png" alt="Bibata Modern Rosé Pine" width="96" />
  <img src="./assets/modern-gruvbox-dark.png" alt="Bibata Modern Gruvbox Dark" width="96" />

# Bibata Cursor

  Custom Bibata color variants and source layouts for my Nix cursor packages.

  [![Release](https://img.shields.io/github/v/release/adam01110/bibata-cursor?style=flat-square&label=Release&labelColor=504945&color=cc241d)](https://github.com/adam01110/bibata-cursor/releases/latest)
  [![Build](https://img.shields.io/github/actions/workflow/status/adam01110/bibata-cursor/build.yml?branch=main&style=flat-square&label=Build&labelColor=504945&color=cc241d)](https://github.com/adam01110/bibata-cursor/actions/workflows/build.yml)
  [![Repo Size](https://img.shields.io/github/repo-size/adam01110/bibata-cursor?style=flat-square&label=repo%20size&labelColor=504945&color=3c3836)](https://github.com/adam01110/bibata-cursor)
  <br />
  [![Nix](https://img.shields.io/badge/Nix-flakes-689d6a?style=flat-square&labelColor=504945&logo=nixos&logoColor=ebdbb2)](https://nixos.wiki/wiki/Flakes)
  [![Bun](https://img.shields.io/badge/Bun-1.3-fb4934?style=flat-square&labelColor=504945&logo=bun&logoColor=ebdbb2)](https://bun.sh)
  [![License](https://img.shields.io/github/license/adam01110/bibata-cursor?style=flat-square&labelColor=504945&color=b16286)](LICENSE)

  [Overview](#overview) - [Variants](#variants) - [Usage](#usage)
  <br />
  [Building](#building) - [Packaging](#packaging) - [Layout](#layout) - [Credits](#credits)
</div>

I keep this fork because I want a small set of Bibata variants that match the
rest of my setup, while keeping the cursor sources reusable for XCursor and
Hyprcursor packages. The release workflow renders the color variants once, and
my NUR packages turn those bitmap archives into the final cursor themes.

The repository is a fork of
[`LOSEARDES77/Bibata-Cursor-hyprcursor`](https://github.com/LOSEARDES77/Bibata-Cursor-hyprcursor),
which is itself a fork of the original
[`ful1e5/Bibata_Cursor`](https://github.com/ful1e5/Bibata_Cursor).

## Overview

- Renders reproducible Bibata bitmap sets from the original SVG sources.
- Keeps Modern, Modern Right, Original, and Original Right source layouts.
- Publishes each configured color variant as a separate release archive.
- Provides the `ctgen` and Hyprcursor conversion files used by my NUR packages.
- Includes a Nix development shell and treefmt checks for repository tooling.

## Variants

| Variant | Base | Outline | Activity |
| --- | --- | --- | --- |
| Bibata Modern Classic | `#000000` | `#FFFFFF` | `#000000` |
| Bibata Modern Rosé Pine | `#26233A` | `#E0DEF4` | `#191724` |
| Bibata Modern Gruvbox Dark | `#504945` | `#FBF1C7` | `#282828` |

The SVG source tree also contains the Original and right-handed layouts so more
combinations can be added without importing the artwork again. The current
[`render.json`](render.json) only generates the three Modern variants above.

## Usage

Rendered PNG archives are available from
[GitHub Releases](https://github.com/adam01110/bibata-cursor/releases/latest).
They are build inputs rather than directly installable cursor themes.

The finished Gruvbox Dark XCursor and Hyprcursor packages are available from my
[NUR repository](https://github.com/adam01110/nur). Add it as a flake input:

```nix
{
  inputs.adam0-nur.url = "github:adam01110/nur";
}
```

Then select either package for the current system:

```nix
{
  inputs,
  pkgs,
  ...
}: let
  nurPkgs = inputs.adam0-nur.packages.${pkgs.stdenv.hostPlatform.system};
in {
  home.packages = [
    nurPkgs.bibata-modern-cursors-gruvbox-dark
    nurPkgs.bibata-modern-cursors-gruvbox-dark-hyprcursor
  ];
}
```

## Building

Enter the development shell and install the locked JavaScript dependencies:

```bash
nix develop
bun install --frozen-lockfile
```

Render every variant configured in `render.json`:

```bash
bun run generate
```

The generated PNG assets are written to `bitmaps/<variant>`.

To change or add a color variant, add another entry to `render.json`. Each color
mapping replaces the source SVG's base, outline, or activity color during
rendering.

The source layout symlinks can be regenerated after changing files under
`svg/groups`:

```bash
bun run link
```

## Packaging

The downstream packages in
[`adam01110/nur`](https://github.com/adam01110/nur) fetch both this source tree
and a rendered bitmap archive. They use [`build.toml`](build.toml) with `ctgen`
to build an XCursor theme:

```bash
ctgen build.toml \
  -d bitmaps/Bibata-Modern-Gruvbox-Dark \
  -n Bibata-Modern-Gruvbox-Dark \
  -c "Gruvbox dark Bibata modern XCursors"
```

The Hyprcursor package then converts the generated theme:

```bash
bash scripts/build-hyprcursor.sh
```

The build script uses the Python helpers beside it to recolor SVGs and update
Hyprcursor metadata during conversion. These files are part of the package
build interface and should remain in sync with the source and manifest naming.

## Layout

| Path | Contents |
| --- | --- |
| `svg/groups/` | Canonical artwork grouped by shape and handedness |
| `svg/modern*/` | Modern source layouts assembled from grouped SVG symlinks |
| `svg/original*/` | Original source layouts assembled from grouped SVG symlinks |
| `render.json` | Color variants rendered by `cbmp` |
| `build.toml` | Cursor names, hotspots, sizes, and `ctgen` build settings |
| `scripts/` | SVG layout, recoloring, metadata, and Hyprcursor build utilities |
| `nix/` | Development shell and treefmt flake modules |
| `.github/workflows/build.yml` | Release rendering and archive upload workflow |

## Credits

- [Bibata Cursor](https://github.com/ful1e5/Bibata_Cursor), designed by
  [Abdulkaiz Khatri](https://github.com/ful1e5)
- [Bibata Cursor Hyprcursor](https://github.com/LOSEARDES77/Bibata-Cursor-hyprcursor)
- [Wedge Loading Animation](https://loading.io/spinner/wedges/-pie-wedge-pizza-circle-round-rotate)
- [Adwaita](https://github.com/GNOME/adwaita-icon-theme)
- [DMZ](https://github.com/GalliumOS/dmz-cursor-theme)
- [Yaru](https://github.com/ubuntu/yaru)
