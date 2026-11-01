# CI workflow template

`github-actions-build.yml` ist die vorbereitete GitHub-Actions-Pipeline für
Validierung, Quellpaket und (optional) den ARM64-GSI-Build.

Sie liegt absichtlich **nicht** unter `.github/workflows/`, weil der
GitHub-Token, mit dem dieses Repository veröffentlicht wurde, keinen
`workflow`-Scope besitzt. Zum Aktivieren:

1. Datei nach `.github/workflows/build.yml` verschieben (oder kopieren).
2. Committen und pushen.

Wer den Workflow selbst pushen will, braucht einen Token mit `workflow`-Scope,
z. B.:

```sh
gh auth refresh -h github.com -s workflow
```

Der Build-Job für das GSI bricht auf normalen `ubuntu-latest`-Runnern bewusst
ab, weil AOSP ca. 400 GB Speicher und mindestens 64 GB RAM benötigt. Der
Validierungs-Job ist auch auf kleinen Runnern sinnvoll.
