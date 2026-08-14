{
  perSystem = {pkgs, ...}: {
    devShells.default = with pkgs;
      mkShellNoCC {
        packages = [
          bun
          python3
        ];
      };
  };
}
