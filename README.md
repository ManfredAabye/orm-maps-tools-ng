# OpenSim (O)RM Map Tools NG - Benutzerhandbuch

![OpenSim ORM Tools NG](orm-maps-tools-ng-master.png)

## 📖 Inhaltsverzeichnis

1. [Was ist ORM Maps Tools NG?](#was-ist-orm-maps-tools-ng)
2. [Installation](#installation)
3. [Erste Schritte](#erste-schritte)
4. [Hauptfunktionen](#hauptfunktionen)
5. [Benutzeroberfläche](#benutzeroberfläche)
6. [Einstellungen und Optionen](#einstellungen-und-optionen)
7. [Tipps und Tricks](#tipps-und-tricks)
8. [Häufige Probleme](#häufige-probleme)

---

## 🎯 Was ist ORM Maps Tools NG?

**ORM Maps Tools NG** ist ein professionelles Tool zur Verwaltung und Erstellung von PBR-Texturen (Physically Based Rendering) für OpenSimulator und andere 3D-Anwendungen.

### Was bedeutet ORM?

ORM steht für **O**cclusion (AO), **R**oughness und **M**etallic - drei wichtige Textur-Maps, die in einer einzigen RGB-Datei kombiniert werden:

- **R-Kanal**: Ambient Occlusion (Schatten in Vertiefungen)
- **G-Kanal**: Roughness (Oberflächenrauheit)
- **B-Kanal**: Metallic (Metallische Eigenschaften)

### Warum ORM Maps Tools NG?

- ✅ **Einfach**: Intuitive Benutzeroberfläche mit Vorschau
- ✅ **Automatisch**: Erkennt automatisch verschiedene Texturnamen
- ✅ **Flexibel**: Unterstützt verschiedene Auflösungen (128-2048px)
- ✅ **Komplett**: Generiert ORM-Maps, skaliert Texturen und erstellt GLTF-Dateien
- ✅ **Anpassbar**: Konfigurierbare Texture-Suffixe über JSON

---

## 💾 Installation

### Voraussetzungen

- **Python 3.8 oder höher**
- **Pillow** (PIL) für Bildverarbeitung
- **NumPy** (optional, für Histogramme)

### Schnellinstallation

1. **Dateien herunterladen**

   ```bash
   git clone https://github.com/ManfredAabye/OpenSim-ORM-Map-Generator.git
   cd OpenSim-ORM-Map-Generator
   ```

2. **Abhängigkeiten installieren**

   ```bash
   pip install Pillow numpy
   ```

3. **Programm starten**

   ```bash
   python orm-maps-tools-ng.py
   ```

### Als EXE-Datei (Windows)

Eine kompilierte EXE-Version benötigt keine Python-Installation. Einfach `ORM-Maps-Tools-NG.exe` starten!

---

## 🚀 Erste Schritte

### Schritt 1: Texturen laden

1. Klicken Sie auf **"Durchsuchen"** neben "Eingabe-Verzeichnis"
2. Wählen Sie den Ordner mit Ihren Texturen aus
3. Die Texturen werden **automatisch geladen** und erkannt

### Schritt 2: Vorschau prüfen

Nach dem Laden sehen Sie:

- 🎨 **Albedo** (Basisfarbe)
- 🗺 **Normal Map** (Oberflächendetails)
- 🌫 **Ambient Occlusion** (Schatten)
- ✨ **Roughness** (Rauheit)
- ⚡ **Metallic** (Metallisch)
- 💡 **Emission** (Leuchten)
- 🌈 **Kombinierte Vorschau** (Wie das Material aussieht)

### Schritt 3: ORM generieren

Klicken Sie auf **"⚙ ORM generieren"** oder drücken Sie **Enter**.

Die ORM-Maps werden im Ausgabe-Verzeichnis erstellt!

---

## 🛠 Hauptfunktionen

### 1. 📂 Texturen laden (Ctrl+L)

Lädt automatisch alle Texturen aus einem Verzeichnis.

**Unterstützte Formate:**

- PNG, JPG, JPEG, JP2

**Erkannte Texture-Typen:**

- Albedo/Diffuse/BaseColor
- Normal (auch OpenGL/DirectX Varianten)
- Ambient Occlusion
- Roughness/Gloss
- Metallic/Specular
- Height/Displacement
- Emission/Emissive

### 2. 🔧 Fehlende Maps (Ctrl+M)

Generiert automatisch fehlende Einzeltexturen mit Standardwerten:

- **AO**: 255 (weiß = keine Schatten)
- **Roughness**: 128 (mittlere Rauheit)
- **Metallic**: 0 (nicht-metallisch)

### 3. ⚙ ORM generieren (Enter)

Kombiniert AO, Roughness und Metallic in eine ORM-Datei.

**Optionen:**

- Speicher-Auflösung wählen (original, 128-2048px)
- Format: PNG, JPEG oder JP2
- Automatisches Auffüllen fehlender Maps

### 4. 🔍 Skalieren

Skaliert **ALLE** Texturen auf eine Zielauflösung:

- Wählen Sie die Zielauflösung (128-2048px)
- Alle Texture-Typen werden skaliert
- ORM-Maps werden automatisch erstellt
- GLTF-Dateien werden generiert

**Wichtig:** Nur die Ausgabe wird skaliert, Originale bleiben unverändert!

### 5. 📦 GLTF (Ctrl+G)

Erstellt GLTF-Dateien für das aktuelle Material:

- Automatische Texture-Referenzen
- PBR-Material-Eigenschaften
- Konfigurierbare Optionen (Alpha, Double-Sided, etc.)

### 6. 📦📦 Batch GLTF

Erstellt GLTF-Dateien für **alle** geladenen Materialien auf einmal.

---

## 🖥 Benutzeroberfläche

### Linke Seite: Kontrollfunktionen

#### Verzeichnisse

- **Eingabe-Verzeichnis**: Wo sind Ihre Texturen?
- **Ausgabe-Verzeichnis**: Wo sollen die ORM-Maps hin?

#### Optionen (5 Tabs)

##### Tab: Basis

- ☑ **Height für AO verwenden**: Nutzt Height-Map als AO-Ersatz
- ☑ **Existierende überschreiben**: Überschreibt vorhandene ORM-Dateien
- ☑ **Fehlende Maps automatisch auffüllen**: Erstellt fehlende Maps
- ☑ **Rekursive Suche**: Sucht auch in Unterordnern
- ☑ **Gloss zu Roughness invertieren**: Wandelt Gloss-Maps um

##### Tab: Erweitert

- **Bevorzugte Auflösung**: auto, 128-2048px
- **Speicher-Auflösung**: Skaliert nur die Ausgabe
- **Ausgabeformat**: PNG, JPEG, JP2
- **JPEG Qualität**: 1-100

##### Tab: Standardwerte

- **AO Default**: 0-255 (Standard: 255)
- **Roughness Default**: 0-255 (Standard: 128)
- **Metallic Default**: 0-255 (Standard: 0)
- **Material Preset**: Standard, Metall, Holz, Stein, Glas, Stoff

##### Tab: GLTF

- **Double Sided**: Beidseitig sichtbar
- **Alpha Mode**: OPAQUE, MASK, BLEND
- **Emission Stärke**: 0-2
- **Metallic Factor**: 0-1
- **Roughness Factor**: 0-1

##### Tab: Validierung

- ☑ **Auflösungskonsistenz prüfen**
- ☑ **Bei ungewöhnlichen Werten warnen**
- ☑ **Export-Log erstellen** (CSV, JSON, TXT)

#### Aktionen

Alle Haupt-Buttons mit Farbcodierung:

- 🟢 **Texturen laden** (Hauptaktion)
- 🟠 **Fehlende Maps** (Hilfsfunktion)
- 🔴 **ORM generieren** (Hauptaktion)
- 🟣 **Skalieren** (Batch-Funktion)
- 🔵 **GLTF** (Export)
- 🔵 **Batch GLTF** (Batch-Export)

### Rechte Seite: Material Vorschau

#### Navigation

- **◄ Zurück** / **Vor ►**: Durch Texturen blättern (auch mit Pfeiltasten)
- **🔍+** / **🔍-** / **1:1**: Zoom-Kontrolle (auch mit Ctrl+/-/0)

#### Vorschau-Bereiche

- **ORM-Komponenten**: AO, Roughness, Metallic einzeln
- **Emission Map**: Selbstleuchtende Bereiche
- **ORM Map**: Kombinierte Map
- **Normal Map**: Oberflächendetails
- **Albedo**: Basisfarbe
- **Alle Bestandteile**: Kombinierte Vorschau

**Tipp:** Klicken Sie auf AO, Roughness oder Metallic für ein **Histogramm** mit Statistiken!

---

## ⚙ Einstellungen und Optionen

### Material Presets

Schnelle Voreinstellungen für typische Materialien:

| Preset | AO | Roughness | Metallic | Verwendung |
|--------|-----|-----------|----------|------------|
| **Standard** | 255 | 128 | 0 | Normale Oberflächen |
| **Metall** | 255 | 30 | 255 | Glänzendes Metall |
| **Holz** | 200 | 180 | 0 | Raues Holz |
| **Stein** | 220 | 200 | 0 | Rauer Stein |
| **Glas** | 255 | 10 | 0 | Glattes Glas |
| **Stoff** | 230 | 220 | 0 | Textilien |

### Auflösungen

**Für OpenSimulator:** Maximum ist **2048x2048 Pixel**!

Verfügbare Größen:

- **128px**: Sehr kleine Texturen, niedrige Qualität
- **256px**: Kleine Objekte, Details aus Entfernung
- **512px**: Standard für viele Objekte
- **1024px**: Hochwertige Texturen, nahe Ansicht
- **2048px**: Maximum für OpenSim, höchste Qualität

### Ausgabeformate

- **PNG**: Verlustfrei, größere Dateien, empfohlen
- **JPEG**: Komprimiert, kleinere Dateien, Qualitätsverlust
- **JP2**: JPEG2000, gute Kompression, nicht überall unterstützt

---

## 💡 Tipps und Tricks

### Texture-Benennung

Das Tool erkennt viele Namens-Konventionen automatisch:

**Beispiele für Albedo:**

- `material_albedo.png`
- `wood_diffuse.jpg`
- `metal_basecolor.png`
- `stone_col.png`

**Beispiele für Normal:**

- `material_normal.png`
- `wall_nor_gl.png` (OpenGL)
- `floor_NormalDX.png` (DirectX)

**Mit Auflösung:**

- `material_albedo_1024.png`
- `wood_rough_2048.jpg`

### Workflow-Tipps

1. **Strukturierte Ordner**: Organisieren Sie Texturen in Unterordnern nach Material
2. **Konsistente Benennung**: Nutzen Sie einheitliche Suffixe
3. **Auflösung wählen**: Für OpenSim nie mehr als 2048px
4. **Batch-Skalierung**: Skalieren Sie alle Texturen auf einmal statt einzeln
5. **GLTF-Export**: Nutzen Sie Batch GLTF für mehrere Materialien

### Tastaturkürzel

| Taste | Funktion |
|-------|----------|
| **←** / **→** | Vorheriges/Nächstes Material |
| **Enter** | ORM generieren |
| **Ctrl+L** | Texturen laden |
| **Ctrl+G** | GLTF erstellen |
| **Ctrl+M** | Fehlende Maps generieren |
| **Ctrl+Plus** | Zoom vergrößern |
| **Ctrl+Minus** | Zoom verkleinern |
| **Ctrl+0** | Zoom zurücksetzen |
| **Up/Down** | Scrollen |
| **Page Up/Down** | Seitenweise scrollen |
| **Home/End** | Zum Anfang/Ende |

### Custom Texture Suffixes

Sie können eigene Texture-Suffixe in `texture_suffixes.json` definieren:

```json
{
  "suffixes": {
    "albedo": ["mein_suffix", "custom_name"],
    "roughness": ["rough", "rgh", "roughness"]
  }
}
```

---

## 🐛 Häufige Probleme

### Problem: "Keine Texturen gefunden"

**Lösung:**

1. Prüfen Sie, ob Texturen im richtigen Format sind (PNG, JPG, JPEG, JP2)
2. Aktivieren Sie "Rekursive Suche", wenn Texturen in Unterordnern sind
3. Prüfen Sie die Dateinamen - mindestens Albedo/Diffuse sollte vorhanden sein
4. Passen Sie `texture_suffixes.json` an, wenn Sie andere Namenskonventionen nutzen

### Problem: ORM-Map ist schwarz

**Lösung:**

1. Prüfen Sie, ob AO, Roughness und Metallic vorhanden sind
2. Aktivieren Sie "Fehlende Maps automatisch auffüllen"
3. Nutzen Sie Material Presets für Standardwerte
4. Klicken Sie auf die Vorschau für ein Histogramm zur Werteprüfung

### Problem: Texturen zu groß für OpenSim

**Lösung:**

1. Wählen Sie "Speicher-Auflösung" maximal 2048
2. Oder nutzen Sie "Skalieren" für Batch-Konvertierung
3. OpenSim akzeptiert maximal 2048x2048 Pixel

### Problem: GLTF-Datei funktioniert nicht

**Lösung:**

1. Prüfen Sie, ob alle referenzierten Texturen vorhanden sind
2. Stellen Sie sicher, dass Pfade relativ sind
3. Nutzen Sie die gleiche Auflösung für alle Texturen
4. Prüfen Sie Alpha Mode und Double-Sided Einstellungen

### Problem: Programm ist langsam

**Lösung:**

1. Reduzieren Sie die Vorschau-Größe (Zoom out)
2. Verarbeiten Sie weniger Texturen auf einmal
3. Deaktivieren Sie "Rekursive Suche" wenn nicht benötigt
4. Schließen Sie andere rechenintensive Programme

---

## 📚 Weitere Ressourcen

- **FEATURES_NG.md**: Detaillierte Feature-Liste
- **QUICKSTART_NG.md**: Schnelleinstieg
- **CHANGELOG_NG.md**: Versionshistorie
- **TEXTURE_SUFFIXES_README.md**: Anleitung zu Custom Suffixes
- **texture_suffixes.json**: Konfigurationsdatei für Texture-Namen

---

## 🤝 Support und Mitwirken

- **GitHub**: [OpenSim-ORM-Map-Generator](https://github.com/ManfredAabye/OpenSim-ORM-Map-Generator)
- **Issues**: Melden Sie Bugs oder schlagen Sie Features vor
- **Pull Requests**: Beiträge sind willkommen!

---

## 📄 Lizenz

Siehe [LICENSE](LICENSE) Datei für Details.

---

## 👨‍💻 Entwickler

Manfred Aabye

- GitHub: [@ManfredAabye](https://github.com/ManfredAabye)

---

**Viel Erfolg mit OpenSim (O)RM Map Tools NG!** 🚀
