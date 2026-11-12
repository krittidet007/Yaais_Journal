#!/bin/sh
# Builds the Linux release tarball with a self-contained installer.
# Run from the repo root:  installer/linux/build-linux.sh
set -e
cd "$(dirname "$0")/../.."
VENV_PY=".venv/bin/python"
[ -x "$VENV_PY" ] || VENV_PY="python3"

echo "==> building dist/YaiisJournal with PyInstaller"
"$VENV_PY" -m PyInstaller --noconfirm --clean YaiisJournal.spec

# onedir builds put the runnable folder in dist/YaiisJournal/
GAME_DIR="dist/YaiisJournal"
[ -d "$GAME_DIR" ] || { echo "!! PyInstaller produced no $GAME_DIR folder"; exit 1; }
[ -x "$GAME_DIR/YaiisJournal" ] || { echo "!! $GAME_DIR/YaiisJournal missing"; exit 1; }

STAGE="dist/linux-stage/YaiisJournal"
rm -rf "dist/linux-stage"
mkdir -p "$STAGE/game-bin"
cp -r "$GAME_DIR" "$STAGE/game-bin/YaiisJournal"
rm -f "$STAGE/game-bin/YaiisJournal/README.md" 2>/dev/null || true
cp installer/linux/install.sh "$STAGE/install.sh"
cp installer/linux/uninstall.sh "$STAGE/uninstall.sh"
cp installer/icons/icon-256.png "$STAGE/yaiis-journal.png"
cp README.md "$STAGE/README.md"
chmod +x "$STAGE/game-bin/YaiisJournal/YaiisJournal" "$STAGE/install.sh" "$STAGE/uninstall.sh"

echo "==> smoke test: the packaged game must boot and keep running"
rm -f dist/smoke.err
RC=0
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy timeout 20 \
    "$STAGE/game-bin/YaiisJournal/YaiisJournal" </dev/null >/dev/null 2>dist/smoke.err || RC=$?
if [ "$RC" != "124" ] || grep -q "Traceback" dist/smoke.err; then
    echo "!! packaged game did not run clean (rc=$RC):"; cat dist/smoke.err
    exit 1
fi
echo "    boots and runs clean"

cd dist/linux-stage
tar -czf ../YaiisJournal-Linux.tar.gz YaiisJournal
cd ../..
rm -rf dist/linux-stage
echo "==> wrote dist/YaiisJournal-Linux.tar.gz"
echo "    hand it to players:  tar xf YaiisJournal-Linux.tar.gz && cd YaiisJournal && ./install.sh"
