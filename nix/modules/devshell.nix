{
  perSystem = {pkgs, ...}: {
    devShells.default = with pkgs;
      mkShellNoCC {
        packages = [
          bun
          git
          hyprcursor
          jq
          python3
          resvg
          xxd
        ];
      };
  };
}
