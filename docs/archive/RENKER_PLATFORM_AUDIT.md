# RENKER_PLATFORM_AUDIT

- **Datum:** 2026-08-10
- **Phase:** Phase 2, Schritt 1–2 (Audit + Gap-Report). **Kein Anwendungscode wurde in diesem Schritt geändert.**
- **Methode:** Quell-Inspektion aller vier Repos (README, Wiki, ADRs, Tests, CI, Manifeste, Quellstruktur, Sicherheits- und Release-Konfiguration). Dokumentation wurde **nicht** mit Implementierung gleichgesetzt.

Legende: **IMPLEMENTED** (Code vorhanden + benutzt) · **PARTIAL** (Teil-Code) · **EXPERIMENTAL** (Prototyp, ausdrücklich unfertig) · **DOC-ONLY** (nur beschrieben) · **PLANNED** (nur Roadmap).

---

## Portfolio-Map

### renker-core (privat)
```
renker-core
├── implemented   : Paketgerüst; 10 importierbare Primitive als Konstanten-Platzhalter;
│                   crypto_interface als reine Protocol-Typen; CI (ruff+pytest); ein Smoke-Test
├── tested        : nur Smoke-Test (Import + Konstanten). Keine Logik getestet, weil keine Logik da ist.
├── experimental  : —
└── planned/doc   : Identity, Capabilities, Permissions, Policy, Audit, Events, Memory, Tasks,
                    Experiments, Evidence, protocol — alle DOC-ONLY (Vision + Wiki), keine Logik
```
**Reifegrad: Skelett.** Der Wert liegt bisher in Struktur und Dokumentation, nicht in Funktion.

### rencora (public) — ACT
```
rencora
├── implemented   : PyQt6-Desktop-Agent; Tool-Dispatch (agents/router.py); ~25 actions/;
│                   core/policy.py (Risikostufen 0..6, Bestätigungs-Gate, sicherer Default);
│                   Prompt-Injection-Trust-Boundary (wrap_external); Audit-Log (core/policy.audit,
│                   logs/audit.log mit Rotation); Path-Traversal-Schutz (file_controller._is_safe_path,
│                   Home-Root-basiert); DPAPI-Secret-Verschlüsselung (core/dpapi.py, core/secrets.py);
│                   verschlüsselte Fernsteuerung (AES-256-GCM), Login-Rate-Limit, Firewall-Pinning
├── tested        : 7 Sicherheits-Tests: test_permissions, test_filesystem_security,
│                   test_audit_rotation, test_desktop_sandbox, test_prompt_boundary,
│                   test_upload_filename, test_tunnel_integrity; CI build.yml (+ neuer release-windows.yml)
├── experimental  : RencoraLM v3 Anbindung, Gestensteuerung, proaktive Engine
└── planned/doc   : feinkörnige, akteurgebundene Capabilities mit Scope/Expiry/Revocation (fehlt)
```
**Reifegrad: das stärkste, produktivnächste Repo.** Sicherheit ist real, getestet und ehrlich dokumentiert.

### renkervault (public + lokal) — SECURE
```
renkervault
├── implemented   : Tauri-Desktop-Client (TS/React); E2E-Krypto auf @noble/* (primitives, ratchet,
│                   pq/post-quantum, padding, vault, safety); Node-Relay-Server; Deploy (Caddy/systemd/Tor);
│                   Inno-Setup-Installer; ausgelieferter Release v0.1.0 (NSIS+MSI)
├── tested        : client/tests/security, server/tests/security
├── experimental  : Prototyp-Status laut README (kein extern auditiertes Produkt)
└── planned/doc   : versioniertes Protokoll v1, Fuzzing, externes Krypto-Review
```
**Reifegrad: funktionierender Krypto-Prototyp mit Sicherheits-Schwerpunkt.**

### continuum (public, MIT) — LEARN
```
continuum
├── implemented   : Phase-0-Forschungspipeline in src/continuum/ (memory, worldmodel, hypothesis,
│                   learning, verification, eval, safety, llm, data); Demo-Loop-Skript
├── tested        : 10 Tests (hypothesis, verification, worldmodel, memory_store, eval_metrics,
│                   governance, consolidation, simulated_lab, speed1); CI ci.yml (ruff+pytest+Demo-Smoke)
├── experimental  : gesamte „Forschung" läuft gegen eine SIMULIERTE Zielfunktion, nicht echte Hardware
└── planned/doc   : reale Experimente, unabhängige Reproduktion, validierte Ergebnisse
```
**Reifegrad: sauberer, ehrlich als Prototyp markierter Phase-0-Stand.**

---

## Die 12 Fragen

**1. Was tut jedes Repo heute wirklich?**
- renker-core: nichts Funktionales — importierbares Gerüst + Doku.
- rencora: ein lauffähiger Desktop-KI-Agent, der reale Systemaktionen ausführt, mit tool-risikobasierter Freigabe, Trust-Boundary, Audit-Log und Home-Root-Pfadschutz.
- renkervault: E2E-verschlüsselter Chat-Client + Relay, mit geprüften Krypto-Bibliotheken.
- continuum: eine reproduzierbare, aber simulierte Forschungs-Lernschleife.

**2. Stärkste bestehende Funktionalität?**
rencoras Sicherheitsschicht (`core/policy.py` + die 7 Sicherheits-Tests). Sie ist real, getestet und ehrlich. Sie ist der natürliche Andockpunkt der Plattform-Sicherheit.

**3. Welche Teile von renker-core sind tatsächlich wiederverwendbar?**
Aktuell: die **Struktur und Namensgebung** der Primitive und die `crypto_interface`-Protocols. **Kein** Logikcode ist wiederverwendbar, weil keiner existiert. Die Konstanten (`RISK_TIERS`, `APPROVAL_POLICIES`, `CHAIN_HASH_ALGORITHM` …) sind als Vokabular brauchbar.

**4. Welche vorgeschlagenen Core-Abstraktionen sind verfrüht?**
`memory`, `tasks`, `events`, `experiments`, `evidence`, `protocol` (Wire-Format). Sie lösen heute kein reales Problem von rencora. `capabilities`, `permissions`, `policy`, `audit`, `identity` sind gerechtfertigt, weil rencora genau die feinkörnige, akteurgebundene Autorisierung fehlt.

**5. Architektur-Grenzen?**
- renker-core: sprach-/prozessneutrales Autorisierungs-Fundament, stdlib-only, **keine** App-Logik, **keine** Krypto-Implementierung.
- rencora: Ausführung + UI + LLM; konsumiert Autorisierung.
- renkervault: Transport-/Identitäts-Krypto; einziger Ort für Krypto-Implementierung.
- continuum: Forschung; isoliert.

**6. Welche Repo-Abhängigkeiten sind heute real?**
Praktisch **keine** Code-Abhängigkeit. Die einzige reale Kopplung ist dokumentarisch (`RENKER_PLATFORM.md`, Wikis).

**7. Welche Abhängigkeiten sind nur konzeptionell?**
renker-core → (rencora/renkervault/continuum): konzeptionell. Der geteilte `protocol`-Layer, gemeinsames Memory/Evidence: konzeptionell.

**8. Bestehende Sicherheitsannahmen?**
- rencora: lokaler, vertrauenswürdiger Nutzer; Home-Verzeichnis als grobe Vertrauensgrenze; Tool-Ergebnisse aus externen Quellen sind untrusted; Bestätigung ab Risiko 4; Secrets DPAPI-gebunden.
- renkervault: Server ist untrusted (Zero-Knowledge-Ziel); Krypto nur aus geprüften Libs.
- renker-core: bisher keine durchgesetzten Annahmen (kein Enforcement-Code).

**9. Welche Tests existieren?**
rencora 7 Sicherheits-Tests; continuum 10 Tests + Demo-Smoke; renkervault client-/server-Security-Suites; renker-core 1 Smoke-Test. CI in allen vieren.

**10. Was fehlt vor Produktionsnutzung?**
Für die Plattform-Autorisierung: eine echte, getestete Identity→Capability→Policy→Audit-Kette; adversariale Tests (Traversal/Prefix/Expiry/Actor/Op/Target/Revocation/Audit-Integrität); eine reale Integration in genau eine rencora-Aktion; ein ehrliches Threat-Model.

**11. Kleinste nützliche Integration renker-core ↔ Rencora?**
Eine **akteurgebundene, scope-begrenzte Datei-Capability** für **genau eine** Datei-Aktion (Lesen/Schreiben): renker-core identifiziert den Akteur (Agent-Session), prüft die Capability (Pfad-Scope, Ablauf, Widerruf), wertet die Policy aus (ALLOW/DENY/REQUIRE_APPROVAL mit erklärbarem Grund) und schreibt ein strukturiertes Audit-Event — **oberhalb** von rencoras bestehendem Tool-Risiko-Gate, nicht als Ersatz. Least Privilege: „darf nach `~/Documents/drafts/**` schreiben", nicht „hat Dateisystemzugriff".

**12. Was soll ausdrücklich NOCH NICHT gebaut werden?**
Memory, Tasks, Events, Experiments, Evidence, das `protocol`-Wire-Format, jede Krypto-Implementierung, REQUIRE_APPROVAL-UI-Flows, verteiltes/serverseitiges Audit, network/browser/camera-Capabilities, Microservices, generische `utils`-Abstraktionen. Ebenfalls nicht: ein Umschreiben von rencoras bestehender `policy.py` oder `file_controller.py`.

---

## Konsequenz für Phase 2

Die erste vertikale Scheibe (Vision-Default) passt zur bestehenden Architektur und wird umgesetzt — **stdlib-only in renker-core**, mit realer Datei-Ausführung im Integrations-Adapter und einer additiven, CI-sicheren Anbindung an rencora. Details: `docs/THREAT_MODEL.md`, `SECURITY_ATTACKS.md`, `PHASE_2_REPORT.md`.
