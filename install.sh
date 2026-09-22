#!/bin/sh
# Selfproof one-line installer for macOS and Linux.
#   curl -fsSL https://raw.githubusercontent.com/renker-industries/selfproof/main/install.sh | sh
# Downloads the latest release binary and installs it to ~/.local/bin (override
# with BINDIR). Requires the repository's releases to be reachable (public, or
# authenticated for a private repository).
set -eu

REPO="renker-industries/selfproof"
BINDIR="${BINDIR:-$HOME/.local/bin}"

os="$(uname -s)"
case "$os" in
  Linux) asset="selfproof-linux" ;;
  Darwin) asset="selfproof-macos" ;;
  *) echo "Unsupported OS: $os. Use the Windows installer or build from source." >&2; exit 1 ;;
esac

url="https://github.com/$REPO/releases/latest/download/$asset"
mkdir -p "$BINDIR"
echo "Downloading $asset from the latest release..."
if ! curl -fSL "$url" -o "$BINDIR/selfproof"; then
  echo "Download failed. If the repository is private, the release is not public yet." >&2
  exit 1
fi
chmod +x "$BINDIR/selfproof"
echo "Installed: $BINDIR/selfproof"

case ":$PATH:" in
  *":$BINDIR:"*) ;;
  *) echo "Add $BINDIR to your PATH, then run: selfproof" ;;
esac
echo "Run 'selfproof' to open the dashboard."
