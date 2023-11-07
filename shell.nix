{ pkgs ? import <nixpkgs> { } }:
let
  fhs = pkgs.buildFHSUserEnv {
    name = "rgi";

    targetPkgs = _: [
      pkgs.glibc
      pkgs.micromamba
    ];

    # Note: The rgi environment has to be created earlier
    profile = ''
      eval "$(micromamba shell hook --shell=bash | sed 's/complete / # complete/g')"
      micromamba activate rgi
    '';
  };
in fhs.env
