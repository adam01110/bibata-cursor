{
  perSystem = {pkgs, ...}: {
    devShells.default = with pkgs;
      mkShellNoCC {
        packages = [
          # keep-sorted start
          bun
          git
          hyprcursor
          jq
          python3
          resvg
          xxd
          # keep-sorted end
        ];
      };
  };
}
