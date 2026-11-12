# Installing / distributing Yaai's Journal

The game itself is plain Python (`pygame-ce`), so three kinds of installers
exist, one per platform. Everything installs **per user — no admin/sudo**,
and saves always live outside the game (`%APPDATA%\wicha` on Windows,
`~/.config/wicha` on Linux/macOS), so they survive updates.

```
installer/
├── make_icons.py          regenerates icons from in-game art (optional)
├── icons/                 icon.ico · icon.icns · icon-*.png
├── linux/
│   ├── build-linux.sh     (dev, on Linux)  → dist/YaiisJournal-Linux.tar.gz
│   ├── install.sh         (player)         per-user install + menu entry
│   └── uninstall.sh
├── windows/
│   ├── install.bat        (player, source) installs with its own venv
│   ├── build-setup.bat    (dev, on Windows)→ dist/YaiisJournal-Setup.exe
│   ├── setup.sed          IExpress recipe used by the setup above
│   ├── setup-install.cmd  runs inside the Setup.exe
│   ├── make-shortcuts.ps1 shortcut + uninstall-registry helper
│   └── uninstall.bat
└── mac/
    └── build-mac.sh       (dev, on a Mac) → dist/YaiisJournal.dmg
```

## Linux (build here, test here)

```sh
./installer/linux/build-linux.sh          # → dist/YaiisJournal-Linux.tar.gz
```

Players then:

```sh
tar xf YaiisJournal-Linux.tar.gz
cd YaiisJournal
./install.sh                              # or: PREFIX=~/Games ./install.sh
```

`install.sh` copies the game to `~/.local/share/yaiis-journal`, puts
`yaiis-journal` on `~/.local/bin`, and adds a menu entry
("Yaai's Journal"). `uninstall.sh` removes it all (saves are kept).

## Windows

**Option A — zero-build, from source (any Windows 10/11):**

Double-click `installer\windows\install.bat`, or run it from a terminal.
It finds Python (installs it via `winget` if missing), creates the game's
own venv in `%LOCALAPPDATA%\Programs\YaiisJournal`, and adds Desktop +
Start menu shortcuts and an uninstaller. Only needs internet once.

**Option B — single-file Setup.exe (build on a Windows machine):**

Run `build_windows.bat` (or `installer\windows\build-setup.bat`) on a
Windows box. It uses PyInstaller for the exe and **IExpress — a tool
that ships with Windows** — to wrap it into `dist\YaiisJournal-Setup.exe`.
Hand that one file to players; it installs with shortcuts + an
"Add or remove programs" entry, no admin needed.

## macOS (build on a Mac)

```sh
./installer/mac/build-mac.sh              # → dist/YaiisJournal.dmg
```

Players open the `.dmg` and drag **YaiisJournal.app** into Applications.
The app is ad-hoc codesigned, so the first launch may need
right-click → *Open* (no paid Apple developer account is used).

## Icons

`installer/icons` is generated from the game's own pixel art:

```sh
.venv/bin/python installer/make_icons.py
```

`icon.ico` and `icon.icns` are written in pure Python (PNG-embedded
containers), so no Pillow is required.
