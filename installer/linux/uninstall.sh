#!/bin/sh
# Removes Yaai's Journal (installed by install.sh).
set -e
PREFIX="${PREFIX:-$HOME/.local/share/yaiis-journal}"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
APPS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"

rm -rf "$PREFIX" 2>/dev/null || true
rm -f "$BIN_DIR/yaiis-journal" "$APPS_DIR/yaiis-journal.desktop" 2>/dev/null || true
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS_DIR" || true

# saves are kept separately in ~/.config/wicha — ask before nuking them
if [ -d "$HOME/.config/wicha" ]; then
    echo "Your journal saves live in ~/.config/wicha and were left alone."
fi
echo "Yaai's Journal uninstalled. Safe travels."
