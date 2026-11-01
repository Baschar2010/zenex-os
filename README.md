# ZENEX OS

> **Status: frühes Quellcode-Projekt — es gibt noch kein fertiges ISO und kein fertiges Android-Image.**
> Dieses Repository wurde veröffentlicht, damit andere das Projekt weiterbauen können. Der ursprüngliche Autor hat keinen Build-Rechner mit genug RAM und Speicher für einen vollständigen AOSP-Build. **Mitarbeit, Co-Maintainer und Build-Kapazität sind sehr willkommen.**

**English:** ZENEX OS is an early, source-only operating-system project: an AOSP-based mobile variant and a Linux-based desktop variant that share branding, privacy rules, DNS filtering and child-profile policy. It does **not** produce a complete image yet. Contributions and maintainers are welcome — see [Help wanted](#help-wanted--hier-kann-man-anfangen).

---

## Worum geht es?

ZENEX ist als eigenes, frei verteilbares Betriebssystem mit zwei Varianten geplant:

| Variante | Basis | Erstes Ziel |
|---|---|---|
| **ZENEX Mobile** | AOSP / Android Open Source Project | Cuttlefish-Virtualgerät (ARM64) |
| **ZENEX Desktop** | Linux-Kernel + eigener ZENEX-Desktop | QEMU x86_64 |

Beide Varianten teilen Branding, Designvorgaben, Datenschutzregeln und das DNS-Filterkonzept. Sie teilen **keinen** Kernel und werden nicht als ein universelles Image veröffentlicht.

Grundsätze:

- keine Google Play Services, Google-Apps oder Analytics im Basisprodukt
- keine Werbe-IDs, kein Telemetrie-Versand, keine versteckten Hintergrundverbindungen
- DoH/DoT mit Zertifikatsprüfung, sichtbarem Status und Fail-Closed-Verhalten
- optionales Kind-Profil mit Guardian-PIN und Adult-Content-Sperre (OISD-NSFW-Liste)
- ZENEX-Branding mit eigenem Logo und Boot-Animation
- nachvollziehbare Builds, Lizenzhinweise und Prüfsummen

## Aktueller Stand

Das Repository ist ein **Quellcode- und Integrationspaket**, kein Release. Konkret vorhanden:

- Produkt- und Sicherheitsspezifikation (`SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`)
- ZENEX-Branding: Original-Logo, transparente Variante, Boot-Animationen für Android und Plymouth
- Android-Launcher als Kotlin-Scaffold (`mobile/launcher/`)
- Device-Owner-App für Private DNS (`mobile/policy-app/`)
- AOSP-Overlays, Produkt-Makefiles und Preferred-Activities-Vorlagen
- Lokaler DNS-Filter/DoT-Proxy und Blocklist-Updater (`network/`)
- OISD-NSFW-Snapshot mit Lizenzhinweisen
- Build-/Bündelskript und GitHub-Workflow-Vorlage
- vollständige Projektdokumentation auf Deutsch: [`DOKUMENTATION-ZENEX.txt`](DOKUMENTATION-ZENEX.txt)

**Noch nicht passiert:**

- kein AOSP-Checkout und kein AOSP-Build (zu wenig RAM/Speicher)
- Launcher und Policy-App wurden nie kompiliert
- kein Linux-Desktop-Image, kein Installer
- DNS-Filter, Boot-Animationen und Plymouth-Theme wurden nie in einem gebooteten Image getestet
- keine Tests auf echter Hardware

## Help wanted – hier kann man anfangen

Am meisten fehlt **Build-Kapazität und tatsächliches Testen**. Konkrete Aufgaben:

1. **AOSP-Grundlage bauen:** unverändertes AOSP-Cuttlefish-Image bauen und booten, danach die ZENEX-Overlays integrieren.
2. **Launcher kompilieren:** `mobile/launcher/` in einem gepinnten AOSP-Baum bauen, als Standard-HOME setzen und Laufzeitfehler beheben.
3. **Policy-App kompilieren:** `mobile/policy-app/` als Device Owner testen und das Private-DNS-Verhalten prüfen.
4. **Desktop-Image bauen:** minimales Linux-QEMU-Image mit Plymouth-Theme, DNS-Proxy und systemd-Units erstellen.
5. **DNS-Filter testen:** Fail-Closed-Verhalten, IPv6, Startreihenfolge, Blocklist-Updates und Lizenzhinweise.
6. **Desktop-Shell:** erste ZENEX-Desktop-Anwendungen (Dateimanager, Terminal, Editor, Einstellungen).
7. **Barrierefreiheit & Low-RAM:** 1-GiB- und 2-GiB-Profile messen, Screenreader, Tastatur, RTL und reduzierte Bewegung prüfen.
8. **Rechtliches:** Markenrecherche für den Namen ZENEX und Redistributionsrechte für das gelieferte Logo klären.

**Wie mitmachen:** Issue eröffnen oder einen Fork erstellen und einen Pull Request senden. Bitte keine Telemetrie, keine Google-Dienste und keine ungefragten Netzwerkverbindungen hinzufügen. Details in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Projektstruktur

```text
assets/                 Logo-Original, transparente Variante, Importskript
desktop/                Plymouth-Bootthemes und systemd-Vorlagen
device/                 Beispiel-Geräteprofil (Redmi Note 14 Pro 5G)
launcher/               HTML-Prototyp und Launcher-Spezifikation
manifest/               Repo-/AOSP-Manifestvorlagen
mobile/boot-animation/  Android-Bootanimationen (normal + Low-RAM)
mobile/launcher/        nativer Kotlin-HOME-Launcher (Scaffold)
mobile/policy-app/      Device-Owner-App für Private DNS
mobile/overlay/         AOSP-Ressource-Overlays
mobile/product/         Produkt-Makefiles und Preferred Activities
network/                DNS-Filter, Updater, systemd, OISD-Snapshot
scripts/                Build-Bündel und Bootanimations-Generator
vendor/zenex/           Platzhalter für die AOSP-Integration
```

## Dokumentation

- [`SPEC.md`](SPEC.md) – Produktanforderungen und Abnahmekriterien
- [`ARCHITECTURE.md`](ARCHITECTURE.md) – Systemaufteilung und Sicherheitsgrenzen
- [`ROADMAP.md`](ROADMAP.md) – Phasenplan
- [`BUILD-ENVIRONMENT.md`](BUILD-ENVIRONMENT.md) – warum hier nicht gebaut wurde
- [`BUILD-TARGETS.md`](BUILD-TARGETS.md) – Android-/GSI-Ziele
- [`RESOURCE-TARGETS.md`](RESOURCE-TARGETS.md) – RAM-/Speicherprofile
- [`BRANDING.md`](BRANDING.md) – Markenstatus und Rechtshinweise
- [`DOKUMENTATION-ZENEX.txt`](DOKUMENTATION-ZENEX.txt) – vollständige deutsche Projektdokumentation

## Lizenz und Marken

Der ZENEX-eigene Quellcode steht unter der **MIT-Lizenz** (siehe [`LICENSE`](LICENSE)). Für mitgelieferte oder referenzierte Fremdkomponenten gelten deren eigene Lizenzen; die OISD-Liste und ihre Lizenz liegen unter `network/policy/`.

Das ZENEX-Logo und die Markenrechte liegen beim Projektinhaber. Der Name ZENEX und das gelieferte Logo sind **noch nicht markenrechtlich für eine öffentliche Verteilung freigegeben**; siehe [`BRANDING.md`](BRANDING.md). Die MIT-Lizenz gilt nicht automatisch für Logo- und Markenassets.

---

## Bisherige Integrationshinweise

### AOSP/LineageOS: lokales Manifest

1. Initialisiere zuerst den gewünschten AOSP-/LineageOS-Quellbaum mit einer festgelegten Upstream-Branch.
2. Kopiere `manifest/local_manifest.xml` nach `.repo/local_manifests/zenex.xml` im Quellbaum.
3. Beachte `manifest/README.md`: Das lokale Projekt verweist auf `vendor/zenex`; die Einbindung setzt voraus, dass der Checkout den lokalen Remote-Eintrag enthält bzw. der Projektordner im Baum liegt. Danach kann Repo lokal synchronisieren.
4. Das ZENEX-Projekt muss zusätzlich in den gewählten Produktbaum integriert werden. Dieses Manifest allein baut kein Gerät.

### Bootanimation und Low-RAM-Profil

Im Produkt-Makefile `ZENEX_LOW_RAM_PROFILE` ausdrücklich setzen:

- **1 GB RAM:** `ZENEX_LOW_RAM_PROFILE=true` wählt `bootanimation-lowram.zip` mit zwei statischen Frames.
- **2 GB RAM oder mehr:** `ZENEX_LOW_RAM_PROFILE=false` wählt die normale 171-Frame-Sequenz.

Die Einstellung ist eine bewusste Produktwahl; sie wird nicht automatisch aus Host-RAM abgeleitet. Für ein echtes 1-GB-System müssen zusätzlich Dienste, Desktop/Launcher und Speichernutzung separat reduziert und getestet werden.

### OISD-NSFW-DNS-Updater

Der Quellcode liegt unter `network/dns-filter/update-zenex-blocklist.py`. Er lädt die OISD-NSFW-small-Liste über HTTPS, prüft Format und Mindestanzahl, schreibt zunächst temporär und ersetzt die aktive Liste atomar.

Beispiel in einer Linux-Umgebung:

```sh
python3 network/dns-filter/update-zenex-blocklist.py \
  --output network/policy/adult-domains.txt
```

Im installierten System startet `zenex-blocklist-update.timer` den Update-Dienst beim Boot und danach periodisch. Die Liste ist eine Domain-Sperrliste, keine vollständige Inhaltsklassifizierung. DNS-Filter können durch VPN, app-eigenes DoH oder direkte IP-Verbindungen umgangen werden.

### Integrationspaket

`scripts/build-zenex.sh` bündelt Module für `desktop`, `aosp` oder `all` und erzeugt ein Archiv plus SHA-256. Für den Desktop muss zuvor ein eigener vertrauenswürdiger DoT-Hostname und dessen Bootstrap-IP in `ZENEX_DOT_HOST` und `ZENEX_DOT_IP` festgelegt werden; das Skript wählt keinen Anbieter automatisch. Das Archiv kompiliert weder ein Linux-ISO noch ein AOSP-Image.

### Plattform-Builds und GitHub Releases

Das aktuelle Workflow-Ziel ist vorerst nur **Android ARM64 GSI**. Der offizielle AOSP GSI-Target heißt `gsi_arm64-userdebug`; `aosp_arm64-userdebug` wäre kein GSI. Android-x86 bleibt für einen späteren Lauf dokumentiert. Siehe [BUILD-TARGETS.md](BUILD-TARGETS.md) für Einschränkungen.

Der Workflow nutzt `ubuntu-latest` und prüft vor dem AOSP-Download die Runner-Ressourcen. Auf Standardrunnern stoppt diese Prüfung, weil GitHub 14 GB SSD und je nach Repository 8 oder 16 GB RAM nennt; AOSP verlangt etwa 400 GB freien Speicher und mindestens 64 GB RAM. Cleanup kann die Lücke nicht ausgleichen. [GitHub Runner-Spezifikationen](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) · [AOSP Build-Anforderungen](https://source.android.com/docs/setup/start/requirements)

Der Workflow staged Launcher, Policy-App, Overlays, HOME-Auswahl, Bootanimationsprofile und die DoT-Werte `family.adguard-dns.com` / `94.140.14.15`. Der Android-DNS-Baustein ist derzeit ein Device-Owner-DoT-Setup und **kein lokaler Resolver, der die OISD-Liste erzwingt**. Das GSI ist nur für kompatible Treble-Geräte gedacht und kein universell auf jedes Handy flashbares Komplettsystem. Ein `v*`-Tag veröffentlicht das GSI nur nach erfolgreichem Build als experimentelles Pre-Release; auf `ubuntu-latest` stoppt der Ressourcencheck zuvor.

Das frühere Geräteprofil für das **Redmi Note 14 Pro 5G Global (24090RA29G, `malachite`)** bleibt unter `device/targets.example.json` und `manifest/local_manifest_malachite.xml` als separates Community-Profil erhalten. Es wird vom aktuellen GSI-Job nicht gebaut.
