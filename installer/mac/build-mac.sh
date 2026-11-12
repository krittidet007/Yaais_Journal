#!/bin/sh
# Builds the macOS release: YaiisJournal.dmg containing YaiisJournal.app.
# Run ON a Mac, from the repo root:  installer/mac/build-mac.sh
#   - PyInstaller makes dist/YaiisJournal.app (windowed, with the icns icon)
#   - hdiutil wraps it into dist/YaiisJournal.dmg
#   - ad-hoc codesign so Gatekeeper shows a proper identity prompt
set -e
cd "$(dirname "$0")/../.."
VENV_PY=".venv/bin/python"
[ -x "$VENV_PY" ] || VENV_PY="python3"

echo "==> installing build tools (one-time)"
"$VENV_PY" -m pip install --quiet --upgrade pyinstaller pygame-ce

echo "==> building YaiisJournal.app"
rm -rf dist/YaiisJournal.app dist/YaiisJournal.dmg build/YaiisJournal
"$VENV_PY" -m PyInstaller --noconfirm --clean YaiisJournal.spec

APP="dist/YaiisJournal.app"
test -d "$APP"

# ad-hoc signature: no Apple developer account needed; the first run
# prompt will say "unidentified developer" - right-click > Open works.
codesign --force --deep --sign - "$APP" 2>/dev/null || true

echo "==> creating YaiisJournal.dmg"
rm -rf dist/dmg-stage
mkdir -p dist/dmg-stage
cp -R "$APP" dist/dmg-stage/
ln -s /Applications dist/dmg-stage/Applications
hdiutil create -volname "Yaiis Journal" \
    -srcfolder dist/dmg-stage \
    -ov -format UDZO dist/YaiisJournal.dmg
rm -rf dist/dmg-stage

echo ""
echo "  ###  DONE  ###"
echo "  dist/YaiisJournal.dmg - give this single file to any Mac player."
echo "  They open it and drag YaiisJournal.app into Applications."
