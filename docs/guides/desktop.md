# Run Selfproof as an app

Selfproof ships as a single-file binary. The simplest use needs no typing:
**double-click it and the dashboard opens in your browser.**

## Windows, macOS, Linux (native binary)

Each operating system builds its own binary — PyInstaller does not
cross-compile, so a Windows `.exe` is built on Windows, a macOS binary on macOS,
and a Linux binary on Linux.

- **From CI:** the `release-binaries` workflow builds all three on GitHub's
  runners and uploads them as artifacts (`selfproof-windows-latest`,
  `selfproof-macos-latest`, `selfproof-ubuntu-latest`).
- **Build it yourself** (on the target OS):

  ```bash
  pip install pyinstaller
  pyinstaller packaging/selfproof.spec --distpath dist --workpath build/pyi
  ```

  The binary lands in `dist/` (`selfproof.exe` on Windows, `selfproof`
  elsewhere).

Run it:

- Double-click, or run `selfproof` with no arguments, to open the dashboard.
- `selfproof status`, `selfproof build`, `selfproof dashboard export --out
  page.html` and the other commands work the same as the Python CLI.

Note on first launch: unsigned binaries trigger the OS's normal
"unknown developer" warning until they are code-signed. Signing is an owner
step, not scripted.

## Android and iOS (installable web app)

There is no Android APK or iOS app; a desktop binary targets desktop operating
systems only. Instead, Selfproof's dashboard is a self-contained web page that
installs like an app:

1. On a desktop, run `selfproof dashboard export --out dashboard.html`.
2. Put that file somewhere the phone can open it (a local web server, a shared
   folder, or your own hosting).
3. Open it in the phone's browser and choose **Add to Home Screen**. The page
   carries a web app manifest and icon name, so it gets its own launcher entry
   and opens full-screen.

The page contains no external resources and no scripts, so it works offline once
loaded and reveals nothing about your machine — it shows aggregated numbers only.
