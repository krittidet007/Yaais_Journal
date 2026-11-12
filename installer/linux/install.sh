#!/bin/sh
# Installs Yaai's Journal for the current user (no sudo needed).
#   ./install.sh                        install to ~/.local (menu + PATH entry)
#   PREFIX=~/Games ./install.sh         fully self-contained install inside
#                                        ~/Games (nothing written to ~ elsewhere)
set -e
cd "$(dirname "$0")"

if [ -z "${PREFIX:-}" ]; then
    # default: follow the XDG conventions so the app shows in menus
    PREFIX="$HOME/.local/share/yaiis-journal"
    DEST="$PREFIX/share/YaiisJournal"
    BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
    APPS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
else
    # custom prefix: everything stays inside it, nothing else is touched
    PREFIX="$(cd "$(dirname "$PREFIX")" && mkdir -p "$(basename "$PREFIX")" && cd "$(basename "$PREFIX")" && pwd)"
    DEST="$PREFIX/YaiisJournal"
    BIN_DIR="$PREFIX/bin"
    APPS_DIR="$PREFIX/share/applications"
fi

mkdir -p "$DEST" "$BIN_DIR" "$APPS_DIR"

# copy the game (a runnable PyInstaller folder - launches instantly)
cp -r game-bin/YaiisJournal "$DEST/"
cp yaiis-journal.png "$DEST/"
cp README.md "$DEST/" 2>/dev/null || true
chmod +x "$DEST/YaiisJournal/YaiisJournal"

# launcher on PATH
cat > "$BIN_DIR/yaiis-journal" <<EOF
#!/bin/sh
cd "$DEST/YaiisJournal"
exec ./YaiisJournal "\$@"
EOF
chmod +x "$BIN_DIR/yaiis-journal"

# desktop entry so it shows in the app menu / launcher
cat > "$APPS_DIR/yaiis-journal.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Yaai's Journal
GenericName=A Southern Thailand Adventure
Comment=Explore southern Thailand and learn Python with Yaai and Noi
Exec=$BIN_DIR/yaiis-journal
Icon=$DEST/yaiis-journal.png
Terminal=false
Categories=Game;Education;
Keywords=game;python;thailand;pixel;journal;
StartupNotify=true
EOF

# refresh the menu (best effort; never fatal)
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS_DIR" || true

echo ""
echo "  Installed! Play it either way:"
echo "    - from your app menu:  'Yaai's Journal'"
echo "    - from a terminal:     yaiis-journal"
echo ""
echo "  Uninstall anytime with:  $PREFIX/uninstall.sh"
echo "  (or ./uninstall.sh from this folder again)"
# leave a copy of the uninstaller next to the install
cp uninstall.sh "$PREFIX/uninstall.sh"
chmod +x "$PREFIX/uninstall.sh"
