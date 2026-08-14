{inputs, ...}: {
  imports = [inputs.treefmt-nix.flakeModule];

  perSystem = {pkgs, ...}: {
    treefmt.programs = {
      biome = {
        enable = true;
        formatCommand = "format";
        includes = ["*.json"];
        settings.formatter = {
          indentStyle = "space";
          indentWidth = 2;
        };
      };

      xmllint = {
        enable = true;
        includes = ["*.xml"];
      };

      # keep-sorted start
      alejandra.enable = true;
      deadnix.enable = true;
      nixf-diagnose.enable = true;
      ruff-format.enable = true;
      rumdl-format.enable = true;
      shfmt.enable = true;
      statix.enable = true;
      taplo.enable = true;
      yamlfmt.enable = true;
      # keep-sorted end

      keep-sorted.enable = true;
    };

    treefmt.settings.formatter = {
      svgo = {
        command = "${pkgs.svgo}/bin/svgo";
        includes = ["*.svg"];
        options = [
          "--multipass"
          "--quiet"
        ];
      };
    };

    treefmt.settings.global.excludes = [
      # keep-sorted start
      "*.py[cod]"
      "__pycache__/*"
      "bin/*"
      "bitmaps/*"
      "dist/*"
      "hyprcursor-build/*"
      "node_modules/*"
      "result*"
      # keep-sorted end
    ];
  };
}
