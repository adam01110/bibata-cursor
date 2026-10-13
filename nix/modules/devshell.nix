{
  perSystem = {pkgs, ...}: {
    devShells.default = with pkgs;
      mkShellNoCC {
        packages = [
          bun
          hyprcursor
          python3
          resvg
        ];
      };
  };
}
