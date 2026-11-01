# Contributing to ZENEX OS

Danke für dein Interesse! Dieses Projekt ist bewusst als offenes Quellcode-Projekt veröffentlicht, damit es von anderen weitergebaut werden kann. Es gibt keinen CLA und keine kommerziellen Hintergedanken.

## Was am dringendsten gebraucht wird

1. **Build-Kapazität für AOSP.** Offizielle Empfehlung: Linux, ca. 400 GB freier Speicher und mindestens 64 GB RAM. Baue zuerst ein unverändertes Cuttlefish-Image, bevor ZENEX-Patches integriert werden.
2. **Kotlin-Build.** `mobile/launcher/` und `mobile/policy-app/` in einem gepinnten AOSP-Baum kompilieren, Fehler beheben und als Standard-HOME bzw. Device Owner testen.
3. **Linux-Desktop-Image.** Minimales QEMU-x86_64-Image mit Plymouth-Theme, DNS-Proxy und systemd-Units bauen.
4. **Tests.** DNS-Fail-Closed, IPv6, Startreihenfolge, Blocklist-Updates, 1-GiB-/2-GiB-Profile, Barrierefreiheit.
5. **Rechtliches.** Markenrecherche für „ZENEX“ und Redistributionsrechte für das Logo; siehe `BRANDING.md`.

## Grundregeln

- Keine Google Play Services, Google-Apps, Analytics, Werbe-IDs oder Telemetrie im Basisprodukt.
- Keine stillen Netzwerkverbindungen und kein stiller Klartext-DNS-Fallback.
- Keine echten Zugangsdaten, Schlüssel oder privaten Hostnamen committen.
- Bestehende Sicherheits- und Datenschutzgrenzen nicht aufweichen, nur um etwas einfacher zu bauen.
- Änderungen möglichst klein und nachvollziehbar halten; Build-Ausgaben und ISOs nicht committen (siehe `.gitignore`).

## Arbeitsablauf

1. Issue eröffnen oder einen bestehenden Punkt aus `ROADMAP.md` auswählen.
2. Fork erstellen, Branch anlegen und ändern.
3. Build-/Testnachweise im Pull Request erwähnen (Host, RAM, Speicher, exakte Befehle, Ergebnis).
4. Pull Request senden. Review ist willkommen, auch wenn noch nicht alles perfekt ist.

## Build-Hinweise

- AOSP: gepinnte Branch/Manifest verwenden, nicht `master` ungeprüft übernehmen.
- Desktop: QEMU x86_64 ist das erste Ziel; niemals die Windows-Systemplatte an einen Installer hängen.
- Python-Skripte: mit Python 3 testen, keine zusätzlichen Abhängigkeiten einführen, wenn die Standardbibliothek reicht.
- Shell-Skripte: `sh -n`/`bash -n` und nach Möglichkeit `shellcheck` ausführen.

## Lizenz der Beiträge

Mit dem Absenden eines Pull Requests stimmst du zu, dass dein Beitrag unter der MIT-Lizenz dieses Repositories steht. Marken- und Logo-Rechte werden dadurch nicht übertragen.
