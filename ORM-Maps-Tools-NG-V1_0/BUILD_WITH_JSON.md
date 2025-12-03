# Anleitung: EXE-Build mit externer JSON-Konfiguration

## Überblick

Die Suffix-Definitionen wurden in `texture_suffixes.json` ausgelagert, damit sie **auch nach der EXE-Kompilierung** anpassbar bleiben.

## Vorteile

✅ **Anpassbar nach Kompilierung** - JSON kann jederzeit bearbeitet werden  
✅ **Keine Neu-Kompilierung** - Änderungen sofort wirksam  
✅ **Benutzerfreundlich** - Einfaches JSON-Format  
✅ **Versionierbar** - Änderungen nachvollziehbar  
✅ **Portabel** - Eine JSON für alle Installationen  

## EXE-Kompilierung mit PyInstaller

### Standard-Build (ohne JSON einbetten)

```bash
pyinstaller --onefile --windowed --name "ORM-Maps-Tools-NG" orm-maps-tools-ng.py
```

**Wichtig:** Die `texture_suffixes.json` muss im gleichen Verzeichnis wie die EXE liegen!

### Build mit JSON als Daten-Datei

Alternativ kann die JSON mit der EXE gebündelt werden (aber bleibt editierbar):

```bash
pyinstaller --onefile --windowed ^
  --name "ORM-Maps-Tools-NG" ^
  --add-data "texture_suffixes.json;." ^
  orm-maps-tools-ng.py
```

**Windows:** Nutzen Sie `;` als Trennzeichen  
**Linux/Mac:** Nutzen Sie `:` als Trennzeichen

### Kompletter Build mit allen Dateien

```bash
pyinstaller --onefile --windowed ^
  --name "ORM-Maps-Tools-NG" ^
  --icon="icon.ico" ^
  --add-data "texture_suffixes.json;." ^
  orm-maps-tools-ng.py
```

## Verzeichnis-Struktur nach Build

### Ohne --add-data

```bash
📁 dist/
├── 📄 ORM-Maps-Tools-NG.exe
└── 📄 texture_suffixes.json      ← Manuell kopieren!
```

### Mit --add-data

```bash
📁 dist/
└── 📄 ORM-Maps-Tools-NG.exe      ← JSON ist eingebettet, wird aber beim ersten Start extrahiert
```

## Funktionsweise

### 1. JSON vorhanden

- Programm lädt `texture_suffixes.json` aus aktuellem Verzeichnis
- Benutzer kann jederzeit bearbeiten
- ✓ Konsole zeigt: "✓ Suffix-Konfiguration geladen"

### 2. JSON fehlt

- Programm erstellt automatisch Standard-JSON
- Standard-Werte werden verwendet
- ✓ Konsole zeigt: "✓ Standard-Konfiguration erstellt"

### 3. JSON fehlerhaft

- Programm verwendet eingebaute Standard-Werte
- ⚠ Konsole zeigt: "⚠ Fehler beim Laden... Verwende Standard-Werte"
- Programm läuft weiter (Fail-Safe)

## Verteilung

### Variante A: JSON separat (Empfohlen)

**Vorteile:**

- Benutzer können JSON vor erstem Start anpassen
- Sichtbar und zugänglich
- Einfach zu updaten

**Dateien:**

```bash
📦 Distribution/
├── 📄 ORM-Maps-Tools-NG.exe
├── 📄 texture_suffixes.json
├── 📄 README.md
└── 📄 TEXTURE_SUFFIXES_README.md
```

### Variante B: JSON eingebettet

**Vorteile:**

- Nur eine Datei zu verteilen
- JSON wird beim ersten Start extrahiert
- Benutzer kann danach bearbeiten

**Dateien:**

```bash
📦 Distribution/
├── 📄 ORM-Maps-Tools-NG.exe
├── 📄 README.md
└── 📄 TEXTURE_SUFFIXES_README.md
```

## Benutzer-Anpassungen

Nach EXE-Verteilung können Benutzer:

1. **JSON direkt bearbeiten** (mit Editor/Notepad++)
2. **Eigene Konventionen hinzufügen**
3. **Suffixe priorisieren** (Reihenfolge ändern)
4. **Programm neu starten** → Änderungen aktiv

**Keine Neu-Kompilierung nötig!**

## Build-Skript Beispiele

### Windows (build_ng.bat)

```batch
@echo off
echo Building ORM Maps Tools NG...

REM Erstelle sauberes Build-Verzeichnis
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build mit PyInstaller
pyinstaller --onefile --windowed ^
  --name "ORM-Maps-Tools-NG" ^
  --icon="icon.ico" ^
  --add-data "texture_suffixes.json;." ^
  orm-maps-tools-ng.py

REM Kopiere Dokumentation
copy README.md dist\
copy FEATURES_NG.md dist\
copy QUICKSTART_NG.md dist\
copy TEXTURE_SUFFIXES_README.md dist\
copy texture_suffixes.json dist\

echo Build complete! Check dist/ folder
pause
```

### Linux/Mac (build_ng.sh)

```bash
#!/bin/bash
echo "Building ORM Maps Tools NG..."

# Erstelle sauberes Build-Verzeichnis
rm -rf build dist

# Build mit PyInstaller
pyinstaller --onefile --windowed \
  --name "ORM-Maps-Tools-NG" \
  --add-data "texture_suffixes.json:." \
  orm-maps-tools-ng.py

# Kopiere Dokumentation
cp README.md dist/
cp FEATURES_NG.md dist/
cp QUICKSTART_NG.md dist/
cp TEXTURE_SUFFIXES_README.md dist/
cp texture_suffixes.json dist/

echo "Build complete! Check dist/ folder"
```

## Testing nach Build

### Test 1: JSON vorhanden

```bash
cd dist
./ORM-Maps-Tools-NG.exe
# Erwartung: "✓ Suffix-Konfiguration geladen"
```

### Test 2: JSON fehlt

```bash
cd dist
del texture_suffixes.json  # Windows
rm texture_suffixes.json   # Linux/Mac
./ORM-Maps-Tools-NG.exe
# Erwartung: "✓ Standard-Konfiguration erstellt"
# → JSON wird neu erstellt
```

### Test 3: JSON anpassen

```bash
# Bearbeite texture_suffixes.json
# Füge "myCustomSuffix" zu albedo hinzu
./ORM-Maps-Tools-NG.exe
# Lade Texturen mit "myCustomSuffix"
# Erwartung: Texturen werden gefunden
```

### Test 4: JSON defekt

```bash
# Lösche eine Klammer in JSON
./ORM-Maps-Tools-NG.exe
# Erwartung: "⚠ Fehler... Verwende Standard-Werte"
# Programm läuft trotzdem
```

## Fehlerbehebung

### Problem: JSON wird nicht gefunden

**Lösung:** JSON muss im gleichen Verzeichnis wie EXE liegen

**Prüfen:**

```bash
dir  # Windows
ls   # Linux/Mac
```

Sollte zeigen:

```bash
ORM-Maps-Tools-NG.exe
texture_suffixes.json
```

### Problem: Änderungen in JSON werden nicht übernommen

**Lösungen:**

1. JSON-Syntax validieren (jsonlint.com)
2. Programm vollständig beenden und neu starten
3. Konsolen-Log prüfen auf Fehler
4. JSON löschen → Programm erstellt neue

### Problem: EXE findet JSON nicht (eingebettet mit --add-data)

**Code wurde bereits angepasst!**

- Sucht zuerst im aktuellen Verzeichnis
- Falls nicht gefunden, sucht in sys._MEIPASS (PyInstaller temp)
- Falls dort auch nicht, erstellt neue JSON

## Deployment-Checkliste

- [ ] EXE kompiliert und getestet
- [ ] texture_suffixes.json vorhanden
- [ ] JSON-Syntax validiert
- [ ] Dokumentation (README, QUICKSTART, etc.) kopiert
- [ ] Test auf sauberem System durchgeführt
- [ ] JSON-Anpassung getestet
- [ ] Fehlende JSON getestet (Auto-Erstellung)
- [ ] Defekte JSON getestet (Fallback)

## Best Practices

### Für Entwickler

1. **JSON im Repository** committen
2. **Standard-JSON dokumentieren**
3. **Build-Skript automatisieren**
4. **Fail-Safe testen** (JSON fehlt/defekt)

### Für Benutzer

1. **JSON vor Bearbeitung sichern**
2. **Syntax validieren** vor Speichern
3. **Schrittweise testen** (1 Änderung → Test)
4. **Dokumentation lesen** (TEXTURE_SUFFIXES_README.md)

## Erweiterte Szenarien

### Mehrere Konfigurationen

Benutzer können mehrere JSON-Varianten anlegen:

```bash
texture_suffixes_standard.json
texture_suffixes_polyhaven.json
texture_suffixes_studio.json
```

Vor Start umbenennen zur aktiven:

```bash
copy texture_suffixes_polyhaven.json texture_suffixes.json
```

### Update der Standard-JSON

Bei neuem Release:

1. Neue texture_suffixes.json bereitstellen
2. Benutzer können überschreiben oder mergen
3. Alte Konfiguration als Backup behalten

### Team-Konfiguration

Teams können Standard-JSON im Netzwerk teilen:

1. JSON auf Netzlaufwerk
2. Lokale Kopie beim Start
3. Zentrales Update möglich

---

**Version:** 1.0  
**Erstellt:** 03.12.2025  
**Kompatibel mit:** ORM Maps Tools NG v2.0+
