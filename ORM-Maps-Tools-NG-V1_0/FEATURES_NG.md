# ORM Maps Tools NG - Advanced Edition Features

## 🎯 Neue Features

### 1. **Textursuch- und Verarbeitungsoptionen**

#### Auflösungswahl

- Bevorzugte Auflösung auswählen (auto, 1k, 2k, 4k, 8k, 16k)
- Automatische Priorisierung der gewählten Auflösung bei Polyhaven-Texturen

#### Rekursive Verzeichnissuche

- Option zum Ein-/Ausschalten der Unterordner-Durchsuchung
- Perfekt für große Textur-Bibliotheken

#### Gloss zu Roughness Invertierung

- Automatische Erkennung und Invertierung von Gloss-Maps
- Unterstützt Legacy-PBR-Workflows

### 2. **Map-Generierungsoptionen**

#### Anpassbare Standardwerte

- Benutzerdefinierte RGB-Werte für fehlende Maps
  - AO: Standard 255 (weiß = keine Verdeckung)
  - Roughness: Standard 128 (mittlere Rauheit)
  - Metallic: Standard 0 (nicht-metallisch)

#### Material-Presets

Vordefinierte Einstellungen für gängige Materialtypen:

- **Standard**: AO=255, Roughness=128, Metallic=0
- **Metall**: AO=255, Roughness=30, Metallic=255
- **Holz**: AO=200, Roughness=180, Metallic=0
- **Stein**: AO=220, Roughness=200, Metallic=0
- **Glas**: AO=255, Roughness=10, Metallic=0
- **Stoff**: AO=230, Roughness=220, Metallic=0

#### Ausgabeformate

- **PNG**: Verlustfrei, optimal für Qualität
- **JPEG**: Mit einstellbarer Qualität (1-100)
- **JP2**: JPEG2000 für bessere Kompression

### 3. **Vorschau-Verbesserungen**

#### Zoom-Funktionalität

- **Vergrößern**: Ctrl++ oder Zoom-Button
- **Verkleinern**: Ctrl+- oder Zoom-Button
- **Reset**: Ctrl+0 oder 1:1-Button
- Zoom-Bereich: 0.5x bis 3.0x

#### Histogramm-Anzeige

- Klick auf AO, Roughness oder Metallic Preview
- Zeigt Statistiken:
  - Durchschnittswert
  - Minimum/Maximum
  - Standardabweichung
- Visuelle Histogramm-Darstellung

#### Preview-Cache

- Automatisches Caching von bis zu 50 Vorschaubildern
- Schnellere Navigation zwischen Materialien

#### Validierung

- Warnung bei nicht-quadratischen Texturen
- Hinweise auf inkonsistente Auflösungen

### 4. **GLTF-Optionen**

#### Material-Einstellungen

- **Double Sided**: Zweiseitiges Material-Rendering
- **Alpha Mode**: OPAQUE, MASK, BLEND
- **Emission Stärke**: 0.0 - 2.0 (einstellbar)
- **Metallic Factor**: 0.0 - 1.0
- **Roughness Factor**: 0.0 - 1.0

#### Batch-Export

- Alle Materialien auf einmal als GLTF exportieren
- Automatische ORM-Generierung wenn fehlend

### 5. **Workflow-Optimierungen**

#### Hotkey-Unterstützung

- **←/→**: Navigation zwischen Texturen
- **Enter**: ORM-Generierung starten
- **Ctrl+L**: Texturen laden
- **Ctrl+G**: GLTF generieren
- **Ctrl+M**: Fehlende Maps generieren
- **Ctrl++/-/0**: Zoom-Steuerung

#### Erweiterte UI

- Tab-basierte Optionen-Organisation
  - **Basis**: Grundlegende Einstellungen
  - **Erweitert**: Format, Auflösung, Qualität
  - **Standardwerte**: Map-Defaults und Presets
  - **GLTF**: GLTF-spezifische Optionen
  - **Validierung**: Qualitätsprüfung und Logging

### 6. **Qualitätskontrolle**

#### Auflösungsvalidierung

- Automatische Prüfung auf konsistente Auflösungen
- Warnungen bei Inkonsistenzen

#### Warnungen bei ungewöhnlichen Werten

- Erkennung problematischer Roughness-Werte
- Hinweise auf unvollständige Metallic-Maps
- Histogramm-basierte Analyse

### 7. **Protokollierung & Export**

#### Export-Log

- Automatische Protokollierung aller Operationen
- Format-Optionen:
  - **CSV**: Tabellarisch für Excel
  - **JSON**: Strukturiert für Tools
  - **TXT**: Einfache Textdatei

#### Detaillierte Logs

- Timestamped Dateinamen
- Vollständige Dokumentation aller Änderungen
- Nachvollziehbare Verarbeitungshistorie

## 🎨 Verbesserungen gegenüber Standard-Version

### Performance

- Preview-Caching reduziert Ladezeiten um ~80%
- Intelligente Textursuche mit Auflösungspriorisierung
- Optimierte Bildverarbeitung

### Benutzerfreundlichkeit

- Intuitive Tab-Navigation
- Kontextuelle Hotkeys
- Sofortiges visuelles Feedback
- Material-Presets für schnelle Einrichtung

### Flexibilität

- Mehrere Ausgabeformate
- Anpassbare Standardwerte
- Erweiterte GLTF-Konfiguration
- Flexible Validierungsoptionen

### Professionalität

- Export-Protokollierung
- Qualitätsvalidierung
- Histogramm-Analyse
- Batch-Verarbeitung

## 📋 Verwendungsbeispiele

### Schnellstart mit Preset

1. Texturen laden
2. Material-Preset wählen (z.B. "Metall")
3. "Fehlende Maps" klicken
4. "ORM generieren" klicken
5. "GLTF generieren" klicken

### Professioneller Workflow

1. Eingabe-Verzeichnis wählen
2. Bevorzugte Auflösung auf "4k" setzen
3. Material-Preset anwenden
4. Export-Log aktivieren (CSV)
5. Validierung aktivieren
6. Batch GLTF Export ausführen
7. Log-Datei für Dokumentation verwenden

### Qualitätskontrolle

1. Texturen laden
2. Durch Materialien navigieren (Pfeiltasten)
3. Auf Map-Previews klicken für Histogramme
4. Warnungen in Logs prüfen
5. Problematische Materialien manuell korrigieren

## 🔧 Technische Details

### Unterstützte Texture-Konventionen

- **Standard**: material_roughness.png
- **Polyhaven**: material_rough_4k.jpg
- **AmbientCG**: material_Roughness.png
- **Gloss-Inversion**: material_gloss.png → roughness

### Ausgabeformate2

- **PNG**: 8-bit/16-bit, verlustfrei
- **JPEG**: Quality 1-100, optimiert
- **JP2**: JPEG2000 mit dB quality mode

### GLTF 2.0 Kompatibilität

- SecondLife/OpenSim kompatibel
- PBR MetallicRoughness Workflow
- Korrekte ORM-Kanal-Zuordnung (R=AO, G=Rough, B=Metal)
- Emission Support mit Stärke-Faktor

## 💡 Tipps & Tricks

1. **Zoom für Details**: Nutze Zoom um Artefakte zu erkennen
2. **Presets als Startpunkt**: Passe nach Preset-Anwendung fein an
3. **Batch-Export**: Bei vielen Materialien Zeit sparen
4. **Histogramme**: Schnelle Qualitätsprüfung
5. **Logs**: Dokumentation für Projekt-Pipeline
6. **Rekursive Suche**: Deaktivieren bei großen Ordnern für Geschwindigkeit

## 🚀 Performance-Optimierungen

- Preview-Cache: Bis zu 50 Bilder im Speicher
- Lazy Loading: Nur aktuelle Ansicht wird geladen
- Threading: UI bleibt responsiv während Verarbeitung
- Intelligente Suche: Bevorzugte Auflösung zuerst

## 📦 Abhängigkeiten

- Python 3.8+
- Pillow (PIL) für Bildverarbeitung
- tkinter (Standard in Python)
- NumPy für Histogramme (optional)

---

**Version**: 2.0 NG (Next Generation)
**Autor**: ManfredAabye
**Lizenz**: Siehe LICENSE
