{ pkgs ? import <nixos> {} }:

# Run nix-shell in this directory and it will pick up on default.nix and
# provide python + the packages required.

pkgs.mkShell {
  buildInputs = [
    pkgs.python39
    pkgs.python39Packages.matplotlib
    # Python formatting
    pkgs.black
    # CSS formatting
    pkgs.nodePackages.prettier
  ];
}
