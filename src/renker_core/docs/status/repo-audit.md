# Current-state audit of the Renker product repos

- **Date:** 2026-08-10
- **Owner:** `sebastianrenker`
- **Method:** README, manifest, and folder tree read to depth 2. `rencora` and `continuum` shallow-cloned (read-only), `renkervault` present locally (read-only). Where anything remained unclear, it is marked as such below.

> An honest inventory, not an evaluation of the code itself. "Present" means: a module/folder exists that thematically corresponds to the primitive — not that it already fulfills the renker-core interface.

## rencora — ACT (Agent Runtime)

- **State:** present remotely (public), **not** locally → shallow-cloned for inspection.
- **Language/stack:** Python. `requirements.txt`, `main.py`, `ui.py`, `setup.py`. Windows build via **PyInstaller** (`main.spec`, `build.bat` → `dist/RENCORA/RENCORA.exe`). GitHub Actions workflow `build.yml` present (builds the EXE on tag `v*`, uploads it as an **artifact** — **no** GitHub release, **no** installer).
- **Maturity:** significantly advanced. `core/` (incl. `policy.py`, `secrets.py`, `llm_client.py`, `logging_config.py`, `dpapi.py`, `tunnel.py`), `agents/` (`planner_agent`, `qa_agent`, `router`), an extensive `actions/` (OS control: files, browser, system, gesture control, and much more), `tests/`, `dashboard/`, `database/`.

| Primitive | Status in rencora |
|---|---|
| Identity | unclear, check manually (no dedicated module discernible) |
| Permissions | **partial** — `core/policy.py` present; coverage of the capability model unclear, check manually |
| Memory | **partial** — `actions/second_brain.py` suggests memory; check manually |
| Events | unclear, check manually (`core/logging_config.py` as neighborhood) |
| Tasks | **partial** — `agents/planner_agent.py`, `actions/task_planner.py` |
| Experiments | not discernible |
| Evidence | not discernible |
| Security | **partial** — `core/secrets.py`, `core/dpapi.py`, `SECURITY.md` |
| Audit | unclear, check manually (logging present, append-only/hash-chain unclear) |

## continuum — LEARN (Research Engine)

- **State:** present remotely (public), **not** locally → shallow-cloned for inspection.
- **Language/stack:** Python. `pyproject.toml`, `src/continuum/`. CI workflow `ci.yml` present. README badge names the **MIT license** (a deviation from the proprietary default recommendation — deliberately so by the owner).
- **Maturity:** a cleanly structured phase-0 prototype; the README expressly marks the status as "concept/architecture prototype, not a validated result". Submodules: `data`, `eval`, `hypothesis`, `learning`, `llm`, `memory`, `safety`, `verification`, `worldmodel`.

| Primitive | Status in continuum |
|---|---|
| Identity | not discernible |
| Permissions | not discernible |
| Memory | **present** — `src/continuum/memory/` |
| Events | unclear, check manually |
| Tasks | unclear, check manually |
| Experiments | **present** — `hypothesis/` + `worldmodel/` + `learning/` form the experiment pipeline |
| Evidence | **present** — `verification/` + `eval/` correspond to the evidence-status model |
| Security | **partial** — `src/continuum/safety/` |
| Audit | unclear, check manually |

## renkervault — SECURE (Identity / Secure Communication)

- **State:** present **locally** (sibling folder) **and** remotely (public) → read-only.
- **Language/stack:** TypeScript/React + **Tauri** (Rust) for the desktop client (`client/` with `src-tauri`, `vite.config.ts`, `@noble/*` crypto, `@noble/post-quantum`), **Node.js** relay server (`server/`). **No** `.github/workflows`.
- **Maturity:** a working E2E prototype with a crypto focus. `client/src/`: `crypto/`, `net/`, `state/`, `ui/`. `deploy/` (Caddyfile, systemd unit, Tor snippet), `installer/` (Inno Setup script), `docs/`.

| Primitive | Status in renkervault |
|---|---|
| Identity | **partial** — device identity/sessions in the crypto client; check manually |
| Permissions | not discernible |
| Memory | not discernible |
| Events | not discernible |
| Tasks | not discernible |
| Experiments | not discernible |
| Evidence | not discernible |
| Security | **present (focus)** — `client/src/crypto/` (`@noble/ciphers`, `@noble/curves`, `@noble/post-quantum`), `SECURITY.md` |
| Audit | not discernible |

## Windows installer — finding (Vision, step 5.1)

Targeted inspection of `renkervault`'s Windows release route:

- **Build configuration:** Tauri client (`client/src-tauri`). The Tauri bundler itself produces Windows installers on `tauri build` (NSIS `-setup.exe` and WiX `.msi`). Additionally, the repo contains an **Inno Setup script** `installer/RenkerVault.iss`, which packages the built `renkervault.exe` (plus optionally the relay server) into a setup (`ISCC.exe installer\RenkerVault.iss`).
- **CI workflow:** **none** — `renkervault` has no `.github/workflows`. The installer is built locally and published manually.
- **GitHub release:** present — `v0.1.0` "RenkerVault 0.1.0" with real, downloadable assets:
  - `RenkerVault_0.1.0_x64-setup.exe` (1,974,745 bytes) — Tauri/NSIS installer
  - `RenkerVault_0.1.0_x64_en-US.msi` (2,977,792 bytes) — Tauri/WiX installer
  - `SHA256SUMS.txt`

**Conclusion for the transfer to rencora (step 5.2):** The *actually shipped* installer comes from the Tauri bundler — this is bound to the Tauri framework and **cannot** be transferred to a Python/PyInstaller app. The framework-**neutral** installer tooling also present in the renkervault repo is **Inno Setup** (`.iss`, compiled with `ISCC.exe`). This is transferred to rencora: an Inno Setup `.iss` that packages the existing PyInstaller output (`dist/RENCORA/`), plus a CI release workflow that builds on a `v*` tag, compiles the setup, and attaches it as an asset to a GitHub release. rencora's existing `build.yml` stays untouched; only additive changes are made.

### Result of the transfer to rencora (steps 5.2–5.4)

- **Adopted tooling:** Inno Setup (`ISCC.exe`), analogous to `renkervault/installer/RenkerVault.iss`.
- **Added (additive only, no existing file changed):** `installer/Rencora.iss` and `.github/workflows/release-windows.yml` in the rencora repo.
- **Release/asset status:** ✅ **successful.** CI run "Release Windows Installer" (windows-latest) green in ~4 min: PyInstaller build → `choco install innosetup` → `ISCC.exe installer\Rencora.iss` → `gh release create`. Release **rencora v0.1.0** contains the asset `Rencora-Setup-0.1.0.exe` (121,483,173 bytes ≈ 116 MB). URL: https://github.com/sebastianrenker/rencora/releases/tag/v0.1.0
