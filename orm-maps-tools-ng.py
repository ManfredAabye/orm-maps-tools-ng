import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import glob
import threading
import json
import csv

class ORMGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenSim (O)RM Map Tools NG")
        
        # Setze Icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "orm-maps-tools-ng-64.png")
            if os.path.exists(icon_path):
                icon_img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon_img)
        except Exception as e:
            print(f"⚠ Icon konnte nicht geladen werden: {e}")
        
        # Setze Mindestgröße und initiale Größe
        self.root.geometry("1250x1028")
        # self.root.minsize(1200, 700)
        
        # Lade Suffix-Definitionen aus JSON
        self.load_suffix_config()
        
        # Variablen
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.progress = tk.DoubleVar()
        self.status = tk.StringVar(value="Bereit")
        self.current_texture_index = 0
        self.texture_list = []
        self.zoom_level = 1.0
        
        # Preview Images Cache
        self.preview_images = {}
        self.preview_cache = {}
        self.normal_preview_widget = None
        self.combined_preview_widget = None
        
        # Optionen - Basic
        self.use_height_for_ao = tk.BooleanVar(value=True)
        self.overwrite_existing = tk.BooleanVar(value=False)
        self.fill_missing_maps = tk.BooleanVar(value=False)
        self.recursive_search = tk.BooleanVar(value=True)
        self.invert_gloss = tk.BooleanVar(value=True)
        
        # Optionen - Erweitert
        self.preferred_resolution = tk.StringVar(value="auto")
        self.target_resolution = tk.StringVar(value="original")  # Skalierungsziel
        self.output_format = tk.StringVar(value="PNG")
        self.compression_quality = tk.IntVar(value=95)
        
        # Standardwerte für fehlende Maps
        self.default_ao_value = tk.IntVar(value=255)
        self.default_roughness_value = tk.IntVar(value=128)
        self.default_metallic_value = tk.IntVar(value=0)
        
        # GLTF Optionen
        self.gltf_double_sided = tk.BooleanVar(value=False)
        self.gltf_alpha_mode = tk.StringVar(value="OPAQUE")
        self.gltf_emission_strength = tk.DoubleVar(value=1.0)
        self.gltf_metallic_factor = tk.DoubleVar(value=1.0)
        self.gltf_roughness_factor = tk.DoubleVar(value=1.0)
        
        # Material Preset
        self.material_preset = tk.StringVar(value="Standard")
        
        # Export Log
        self.export_log = tk.BooleanVar(value=False)
        self.log_format = tk.StringVar(value="CSV")
        
        # Validation
        self.validate_resolution = tk.BooleanVar(value=True)
        self.warn_unusual_values = tk.BooleanVar(value=True)
        
        # Hotkeys
        self.setup_hotkeys()
        
        self.setup_ui()
    
    def load_suffix_config(self):
        """Lädt Suffix-Definitionen aus JSON-Datei"""
        config_file = os.path.join(os.path.dirname(__file__), "texture_suffixes.json")
        
        # Standard-Fallback falls JSON fehlt
        default_config = {
            "suffixes": {
                "albedo": ["albedo", "Albedo", "ALBEDO", "alb", "Alb", "ALB", "base", "Base", "BASE",
                          "basecolor", "BaseColor", "BASECOLOR", "color", "Color", "COLOR",
                          "col", "Col", "COL", "diffuse", "Diffuse", "DIFFUSE", "diff", "Diff", "DIFF"],
                "normal": ["normal", "Normal", "NORMAL", "NormalGL", "NormalDX", "nor_gl", "nor_dx",
                          "norrmal", "norm", "Norm", "NRM", "Nrm", "nrm", "nor", "Nor", "NOR"],
                "ao": ["ao", "AO", "Ao", "ambient", "Ambient", "AMBIENT", "occlusion", "Occlusion",
                      "OCCLUSION", "AmbientOcclusion", "ambientOcclusion", "Occlusionc", "ambient-occlusion"],
                "roughness": ["roughness", "Roughness", "ROUGHNESS", "rough", "Rough", "ROUGH",
                             "roughnness", "rgh", "RGH", "Rgh", "REFL", "Refl", "refl",
                             "gloss", "Gloss", "GLOSS"],
                "metallic": ["metallic", "Metallic", "METALLIC", "metal", "Metal", "METAL", "metalic",
                            "metallness", "Metallness", "metalness", "Metalness", "mtl", "MTL", "Mtl",
                            "Metalness", "specular", "Specular", "SPECULAR"],
                "height": ["height", "Height", "HEIGHT", "disp", "Disp", "DISP",
                          "displacement", "Displacement", "DISPLACEMENT", "bump", "Bump", "BUMP"],
                "emission": ["emission", "Emission", "EMISSION", "emissive", "Emissive", "EMISSIVE",
                            "emiss", "Emiss", "emis", "Emis", "emi", "Emi", "glow", "Glow", "GLOW"]
            },
            "extensions": ["png", "jpg", "jpeg", "jp2"],
            "separators": ["_", "-"],
            "resolutions": ["128", "256", "512", "1024", "2048"]
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.suffix_config = config
                    print(f"✓ Suffix-Konfiguration geladen: {config_file}")
            else:
                # Erstelle Standard-Konfigurationsdatei
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "version": "1.0",
                        "description": "Texture suffix definitions - Edit to add custom naming conventions",
                        **default_config,
                        "comments": {
                            "albedo": "Base color / diffuse textures",
                            "normal": "Normal maps (OpenGL format preferred)",
                            "ao": "Ambient Occlusion maps",
                            "roughness": "Roughness maps (also detects gloss maps for inversion)",
                            "metallic": "Metallic maps (also legacy specular)",
                            "height": "Height/Displacement/Bump maps",
                            "emission": "Emissive/Glow maps"
                        }
                    }, f, indent=2, ensure_ascii=False)
                self.suffix_config = default_config
                print(f"✓ Standard-Konfiguration erstellt: {config_file}")
        except Exception as e:
            print(f"⚠ Fehler beim Laden der Suffix-Konfiguration: {e}")
            print("  Verwende eingebaute Standard-Werte")
            self.suffix_config = default_config
    
    def get_suffixes(self, map_type):
        """Gibt Suffixe für einen Map-Typ zurück"""
        return self.suffix_config.get("suffixes", {}).get(map_type, [])
    
    def get_extensions(self):
        """Gibt unterstützte Datei-Erweiterungen zurück"""
        return self.suffix_config.get("extensions", ["png", "jpg", "jpeg", "jp2"])
    
    def get_separators(self):
        """Gibt Suffix-Trennzeichen zurück"""
        return self.suffix_config.get("separators", ["_", "-"])
    
    def get_resolutions(self):
        """Gibt Auflösungs-Suffixe zurück"""
        return self.suffix_config.get("resolutions", ["128", "256", "512", "1024", "2048"])
    
    def setup_hotkeys(self):
        """Richtet Tastaturkürzel ein"""
        self.root.bind('<Left>', lambda e: self.prev_texture())
        self.root.bind('<Right>', lambda e: self.next_texture())
        self.root.bind('<Return>', lambda e: self.start_generation())
        self.root.bind('<Control-l>', lambda e: self.load_textures())
        self.root.bind('<Control-g>', lambda e: self.generate_gltf())
        self.root.bind('<Control-m>', lambda e: self.generate_missing_maps())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
    
    def setup_ui(self):
        # Root-Fenster Grid-Konfiguration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Hauptcontainer mit Canvas für Scrolling
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Canvas für scrollbaren Inhalt
        canvas = tk.Canvas(main_container, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        h_scrollbar = ttk.Scrollbar(main_container, orient=tk.HORIZONTAL, command=canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Frame innerhalb Canvas
        main_frame = ttk.Frame(canvas, padding="10")
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Update scroll region wenn Frame sich ändert
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        main_frame.bind("<Configure>", configure_scroll_region)
        
        # Canvas-Größe anpassen wenn Fenster sich ändert
        def configure_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", configure_canvas)
        
        # Mausrad-Scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", bind_mousewheel)
        canvas.bind("<Leave>", unbind_mousewheel)
        
        # Tastatur-Scrolling
        def on_key_up(event):
            canvas.yview_scroll(-1, "units")
        
        def on_key_down(event):
            canvas.yview_scroll(1, "units")
        
        def on_page_up(event):
            canvas.yview_scroll(-1, "pages")
        
        def on_page_down(event):
            canvas.yview_scroll(1, "pages")
        
        def on_home(event):
            canvas.yview_moveto(0)
        
        def on_end(event):
            canvas.yview_moveto(1)
        
        self.root.bind("<Up>", on_key_up)
        self.root.bind("<Down>", on_key_down)
        self.root.bind("<Prior>", on_page_up)  # Page Up
        self.root.bind("<Next>", on_page_down)  # Page Down
        self.root.bind("<Home>", on_home)
        self.root.bind("<End>", on_end)
        
        # Speichere Canvas-Referenz für spätere Verwendung
        self.main_canvas = canvas
        
        # Titel mit Hintergrund und Logo
        title_frame = tk.Frame(main_frame, bg="#2E86AB", relief="raised", bd=2)
        title_frame.grid(row=0, column=0, columnspan=4, pady=(0, 10), sticky="ew")
        
        # Logo und Titel Container (zentriert)
        title_container = tk.Frame(title_frame, bg="#2E86AB")
        title_container.pack(expand=True, pady=10)
        
        # Lade und zeige Logo
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "orm-maps-tools-ng-128.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((64, 64), Image.Resampling.LANCZOS)  # Verkleinere auf 64x64
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(title_container, image=logo_photo, bg="#2E86AB")
                logo_label.image = logo_photo  # type: ignore # Referenz speichern gegen GC
                logo_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"⚠ Logo konnte nicht geladen werden: {e}")
        
        # Titel-Text
        title_label = tk.Label(title_container, text="OpenSim (O)RM Map Tools NG", 
                               font=("Arial", 16, "bold"), bg="#2E86AB", fg="white")
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Hotkey Info mit Hintergrund
        hotkey_frame = tk.Frame(main_frame, bg="#A23B72", relief="sunken", bd=1)
        hotkey_frame.grid(row=1, column=0, columnspan=4, pady=(0, 10), sticky="ew")
        hotkey_label = tk.Label(hotkey_frame, 
                               text="⌨ Hotkeys: ←→ Navigation | Enter: ORM | Ctrl+L: Laden | Ctrl+G: GLTF | Ctrl+M: Fehlend | Ctrl +/-/0: Zoom", 
                               font=("Arial", 8, "bold"), bg="#A23B72", fg="white", pady=5)
        hotkey_label.pack(fill=tk.X)
        
        # Linke Seite: Steuerung mit Hintergrund
        control_frame = tk.LabelFrame(main_frame, text="⚡ Kontrollfunktionen", 
                                     font=("Arial", 10, "bold"), bg="#F0F4F8", fg="#006494",
                                     relief="ridge", bd=3)
        control_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        
        # Eingabe-Verzeichnis mit Farbe
        input_label = tk.Label(control_frame, text="📁 Eingabe-Verzeichnis:", font=("Arial", 9, "bold"), 
                              bg="#F0F4F8", fg="#006494")
        input_label.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(control_frame, textvariable=self.input_dir, width=40).grid(row=1, column=0, pady=5, padx=5)
        ttk.Button(control_frame, text="Durchsuchen", command=self.browse_input_dir).grid(row=1, column=1, pady=5, padx=5)
        
        # Ausgabe-Verzeichnis mit Farbe
        output_label = tk.Label(control_frame, text="💾 Ausgabe-Verzeichnis:", font=("Arial", 9, "bold"), 
                               bg="#F0F4F8", fg="#006494")
        output_label.grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(control_frame, textvariable=self.output_dir, width=40).grid(row=3, column=0, pady=5, padx=5)
        ttk.Button(control_frame, text="Durchsuchen", command=self.browse_output_dir).grid(row=3, column=1, pady=5, padx=5)
        
        # Notebook für Optionen
        options_notebook = ttk.Notebook(control_frame)
        options_notebook.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Tab 1: Basis-Optionen
        basic_frame = ttk.Frame(options_notebook, padding="5")
        options_notebook.add(basic_frame, text="Basis")
        
        ttk.Checkbutton(basic_frame, text="Height für AO verwenden", 
                       variable=self.use_height_for_ao).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(basic_frame, text="Existierende überschreiben", 
                       variable=self.overwrite_existing).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(basic_frame, text="Fehlende Maps automatisch auffüllen", 
                       variable=self.fill_missing_maps).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(basic_frame, text="Rekursive Suche in Unterordnern", 
                       variable=self.recursive_search).grid(row=3, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(basic_frame, text="Gloss zu Roughness invertieren", 
                       variable=self.invert_gloss).grid(row=4, column=0, sticky=tk.W, pady=2)
        
        # Tab 2: Erweiterte Optionen
        advanced_frame = ttk.Frame(options_notebook, padding="5")
        options_notebook.add(advanced_frame, text="Erweitert")
        
        # Auflösung
        ttk.Label(advanced_frame, text="Bevorzugte Auflösung:").grid(row=0, column=0, sticky=tk.W, pady=2)
        resolution_combo = ttk.Combobox(advanced_frame, textvariable=self.preferred_resolution, 
                                       values=["auto", "128", "256", "512", "1024", "2048"], width=10, state="readonly")
        resolution_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Zielauflösung (Skalierung)
        ttk.Label(advanced_frame, text="Zielauflösung:").grid(row=3, column=0, sticky=tk.W, pady=2)
        target_res_combo = ttk.Combobox(advanced_frame, textvariable=self.target_resolution, 
                                       values=["original", "128", "256", "512", "1024", "2048"], width=10, state="readonly")
        target_res_combo.grid(row=3, column=1, sticky=tk.W, pady=2)
        ttk.Label(advanced_frame, text="(Skaliert alle Texturen)", font=("Arial", 7), foreground="gray").grid(row=3, column=2, sticky=tk.W, pady=2, padx=5)
        
        # Output Format
        ttk.Label(advanced_frame, text="Ausgabeformat:").grid(row=1, column=0, sticky=tk.W, pady=2)
        format_combo = ttk.Combobox(advanced_frame, textvariable=self.output_format, 
                                    values=["PNG", "JPEG", "JP2"], width=10, state="readonly")
        format_combo.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Compression Quality
        ttk.Label(advanced_frame, text="JPEG Qualität:").grid(row=2, column=0, sticky=tk.W, pady=2)
        quality_scale = ttk.Scale(advanced_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                                 variable=self.compression_quality, length=150)
        quality_scale.grid(row=2, column=1, sticky=tk.W, pady=2)
        quality_label = ttk.Label(advanced_frame, textvariable=self.compression_quality)
        quality_label.grid(row=2, column=2, sticky=tk.W, pady=2, padx=5)
        
        # Zielauflösung (Skalierung)
        ttk.Label(advanced_frame, text="Speicher-Auflösung:").grid(row=3, column=0, sticky=tk.W, pady=2)
        target_res_combo = ttk.Combobox(advanced_frame, textvariable=self.target_resolution, 
                                       values=["original", "128", "256", "512", "1024", "2048"], width=10, state="readonly")
        target_res_combo.grid(row=3, column=1, sticky=tk.W, pady=2)
        ttk.Label(advanced_frame, text="(nur Ausgabe)", font=("Arial", 7), foreground="gray").grid(row=3, column=2, sticky=tk.W, pady=2, padx=5)
        
        # Info-Text
        info_label = ttk.Label(advanced_frame, 
                              text="⚠ Originale bleiben unverändert!\nNur gespeicherte ORM/Texturen werden skaliert", 
                              font=("Arial", 7), 
                              foreground="darkgreen")
        info_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(5, 10))
        
        # Tab 3: Standardwerte
        defaults_frame = ttk.Frame(options_notebook, padding="5")
        options_notebook.add(defaults_frame, text="Standardwerte")
        
        ttk.Label(defaults_frame, text="AO Default (0-255):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ao_spinbox = ttk.Spinbox(defaults_frame, from_=0, to=255, textvariable=self.default_ao_value, width=10)
        ao_spinbox.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(defaults_frame, text="Roughness Default (0-255):").grid(row=1, column=0, sticky=tk.W, pady=2)
        rough_spinbox = ttk.Spinbox(defaults_frame, from_=0, to=255, textvariable=self.default_roughness_value, width=10)
        rough_spinbox.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(defaults_frame, text="Metallic Default (0-255):").grid(row=2, column=0, sticky=tk.W, pady=2)
        metal_spinbox = ttk.Spinbox(defaults_frame, from_=0, to=255, textvariable=self.default_metallic_value, width=10)
        metal_spinbox.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Material Presets
        ttk.Label(defaults_frame, text="Material Preset:").grid(row=3, column=0, sticky=tk.W, pady=2)
        preset_combo = ttk.Combobox(defaults_frame, textvariable=self.material_preset, 
                                   values=["Standard", "Metall", "Holz", "Stein", "Glas", "Stoff"], 
                                   width=10, state="readonly")
        preset_combo.grid(row=3, column=1, sticky=tk.W, pady=2)
        preset_combo.bind('<<ComboboxSelected>>', self.apply_material_preset)
        
        # Tab 4: GLTF Optionen
        gltf_frame = ttk.Frame(options_notebook, padding="5")
        options_notebook.add(gltf_frame, text="GLTF")
        
        ttk.Checkbutton(gltf_frame, text="Double Sided", 
                       variable=self.gltf_double_sided).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Label(gltf_frame, text="Alpha Mode:").grid(row=1, column=0, sticky=tk.W, pady=2)
        alpha_combo = ttk.Combobox(gltf_frame, textvariable=self.gltf_alpha_mode, 
                                  values=["OPAQUE", "MASK", "BLEND"], width=10, state="readonly")
        alpha_combo.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(gltf_frame, text="Emission Stärke:").grid(row=2, column=0, sticky=tk.W, pady=2)
        emission_scale = ttk.Scale(gltf_frame, from_=0, to=2, orient=tk.HORIZONTAL, 
                                  variable=self.gltf_emission_strength, length=150)
        emission_scale.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(gltf_frame, text="Metallic Factor:").grid(row=3, column=0, sticky=tk.W, pady=2)
        metallic_scale = ttk.Scale(gltf_frame, from_=0, to=1, orient=tk.HORIZONTAL, 
                                  variable=self.gltf_metallic_factor, length=150)
        metallic_scale.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(gltf_frame, text="Roughness Factor:").grid(row=4, column=0, sticky=tk.W, pady=2)
        roughness_scale = ttk.Scale(gltf_frame, from_=0, to=1, orient=tk.HORIZONTAL, 
                                   variable=self.gltf_roughness_factor, length=150)
        roughness_scale.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # Tab 5: Validierung & Export
        validation_frame = ttk.Frame(options_notebook, padding="5")
        options_notebook.add(validation_frame, text="Validierung")
        
        ttk.Checkbutton(validation_frame, text="Auflösungskonsistenz prüfen", 
                       variable=self.validate_resolution).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(validation_frame, text="Bei ungewöhnlichen Werten warnen", 
                       variable=self.warn_unusual_values).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(validation_frame, text="Export-Log erstellen", 
                       variable=self.export_log).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(validation_frame, text="Log Format:").grid(row=3, column=0, sticky=tk.W, pady=2)
        log_combo = ttk.Combobox(validation_frame, textvariable=self.log_format, 
                                values=["CSV", "JSON", "TXT"], width=10, state="readonly")
        log_combo.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Buttons mit Farben und Beschriftung
        actions_frame = tk.LabelFrame(control_frame, text="🎬 Aktionen", 
                                     font=("Arial", 9, "bold"), bg="#F0F4F8", fg="#006494",
                                     relief="ridge", bd=2)
        actions_frame.grid(row=5, column=0, columnspan=2, pady=10, padx=5, sticky="ew")
        
        # Erste Reihe Buttons
        button_frame1 = tk.Frame(actions_frame, bg="#F0F4F8")
        button_frame1.pack(pady=(5, 2), padx=5)
        
        # Button mit grüner Hervorhebung für Hauptaktion
        load_btn = tk.Button(button_frame1, text="📂 Texturen laden (Ctrl+L)", command=self.load_textures,
                            bg="#52B788", fg="white", font=("Arial", 9, "bold"), relief="raised", bd=3)
        load_btn.pack(side=tk.LEFT, padx=3)
        
        tk.Button(button_frame1, text="🔧 Fehlende Maps (Ctrl+M)", command=self.generate_missing_maps,
                 bg="#F77F00", fg="white", font=("Arial", 9), relief="raised", bd=2).pack(side=tk.LEFT, padx=3)
        
        tk.Button(button_frame1, text="⚙ ORM generieren (Enter)", command=self.start_generation,
                 bg="#D62828", fg="white", font=("Arial", 9, "bold"), relief="raised", bd=3).pack(side=tk.LEFT, padx=3)
        
        # Zweite Reihe Buttons
        button_frame2 = tk.Frame(actions_frame, bg="#F0F4F8")
        button_frame2.pack(pady=(2, 5), padx=5)
        
        tk.Button(button_frame2, text="🔍 Skalieren", command=self.batch_scale_textures,
                 bg="#6A4C93", fg="white", font=("Arial", 9), relief="raised", bd=2).pack(side=tk.LEFT, padx=3)
        
        tk.Button(button_frame2, text="📦 GLTF (Ctrl+G)", command=self.generate_gltf,
                 bg="#1982C4", fg="white", font=("Arial", 9), relief="raised", bd=2).pack(side=tk.LEFT, padx=3)
        
        tk.Button(button_frame2, text="📦📦 Batch GLTF", command=self.batch_export_gltf,
                 bg="#0466C8", fg="white", font=("Arial", 9), relief="raised", bd=2).pack(side=tk.LEFT, padx=3)
        
        # Fortschritt mit Farbe
        progress_label = tk.Label(control_frame, text="⏳ Fortschritt:", font=("Arial", 9, "bold"), 
                                 bg="#F0F4F8", fg="#006494")
        progress_label.grid(row=7, column=0, sticky=tk.W, pady=(10, 0), padx=5)
        progress_bar = ttk.Progressbar(control_frame, variable=self.progress, length=400)
        progress_bar.grid(row=8, column=0, columnspan=2, sticky="ew", pady=5, padx=5)
        
        # Status mit Hintergrund
        status_frame = tk.Frame(control_frame, bg="#E8F5E9", relief="sunken", bd=2)
        status_frame.grid(row=9, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
        status_label = tk.Label(status_frame, textvariable=self.status, font=("Arial", 9), 
                               bg="#E8F5E9", fg="#2E7D32", pady=5)
        status_label.pack(fill=tk.X)
        
        # Log mit Farbe
        log_frame = tk.LabelFrame(control_frame, text="📋 Log", font=("Arial", 9, "bold"), 
                                 bg="#F0F4F8", fg="#006494", relief="ridge", bd=3)
        log_frame.grid(row=10, column=0, columnspan=2, sticky="nsew", pady=10, padx=5)
        
        self.log_text = tk.Text(log_frame, height=6, width=50, bg="#263238", fg="#00E676", 
                               font=("Consolas", 9), insertbackground="white")
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Rechte Seite: Vorschau mit Farbe
        preview_frame = tk.LabelFrame(main_frame, text="🎨 Material Vorschau", font=("Arial", 10, "bold"), 
                                     bg="#FFF3E0", fg="#E65100", relief="ridge", bd=3, padx=10, pady=10)
        preview_frame.grid(row=2, column=1, sticky="nsew", padx=(10, 0))
        
        # Navigation mit Zoom und Farbe
        nav_frame = tk.Frame(preview_frame, bg="#FFF3E0")
        nav_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        tk.Button(nav_frame, text="◄ Zurück", command=self.prev_texture, 
                 bg="#42A5F5", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        self.texture_label = tk.Label(nav_frame, text="Keine Texturen geladen", 
                                     font=("Arial", 10, "bold"), bg="#FFF3E0", fg="#D84315")
        self.texture_label.pack(side=tk.LEFT, padx=20)
        tk.Button(nav_frame, text="Vor ►", command=self.next_texture, 
                 bg="#42A5F5", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Zoom Controls mit Farbe
        tk.Button(nav_frame, text="🔍+", command=self.zoom_in, 
                 bg="#66BB6A", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
        tk.Button(nav_frame, text="🔍-", command=self.zoom_out, 
                 bg="#EF5350", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
        tk.Button(nav_frame, text="1:1", command=self.reset_zoom, 
                 bg="#78909C", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
        
        # Zeile 1: ORM-Komponenten mit Farben
        tk.Label(preview_frame, text="🌫 Ambient Occlusion", font=("Arial", 9, "bold"), 
                bg="#FFF3E0", fg="#D32F2F").grid(row=1, column=0, pady=5)
        self.ao_preview = tk.Label(preview_frame, text="Keine Vorschau", relief="ridge", 
                                  bg="#FFEBEE", bd=3)
        self.ao_preview.grid(row=2, column=0, padx=5, pady=5)
        self.ao_preview.bind("<Button-1>", lambda e: self.show_histogram("AO"))
        
        tk.Label(preview_frame, text="✨ Roughness", font=("Arial", 9, "bold"), 
                bg="#FFF3E0", fg="#388E3C").grid(row=1, column=1, pady=5)
        self.roughness_preview = tk.Label(preview_frame, text="Keine Vorschau", relief="ridge", 
                                         bg="#E8F5E9", bd=3)
        self.roughness_preview.grid(row=2, column=1, padx=5, pady=5)
        self.roughness_preview.bind("<Button-1>", lambda e: self.show_histogram("Roughness"))
        
        tk.Label(preview_frame, text="⚡ Metallic", font=("Arial", 9, "bold"), 
                bg="#FFF3E0", fg="#1976D2").grid(row=1, column=2, pady=5)
        self.metallic_preview = tk.Label(preview_frame, text="Keine Vorschau", relief="ridge", 
                                        bg="#E3F2FD", bd=3)
        self.metallic_preview.grid(row=2, column=2, padx=5, pady=5)
        self.metallic_preview.bind("<Button-1>", lambda e: self.show_histogram("Metallic"))
        
        # Zeile 2: Emission und ORM Map mit Farben
        tk.Label(preview_frame, text="💡 Emission Map", font=("Arial", 10, "bold"), 
                bg="#FFF3E0", fg="#F57C00").grid(row=3, column=0, pady=(20, 5))
        self.emission_preview = tk.Label(preview_frame, text="Keine Vorschau", relief="ridge", 
                                        bg="#FFF8E1", bd=3)
        self.emission_preview.grid(row=4, column=0, padx=5, pady=5)
        
        tk.Label(preview_frame, text="🎯 ORM Map (kombiniert)", font=("Arial", 10, "bold"), 
                bg="#FFF3E0", fg="#7B1FA2").grid(row=3, column=1, columnspan=2, pady=(20, 5))
        self.orm_preview = tk.Label(preview_frame, text="Noch nicht generiert", relief="ridge", 
                                   bg="#F3E5F5", bd=3)
        self.orm_preview.grid(row=4, column=1, columnspan=2, padx=5, pady=5)
        
        # Zeile 3: Normal Map, Albedo, Alle Bestandteile mit Farben
        tk.Label(preview_frame, text="🗺 Normal Map", font=("Arial", 9, "bold"), 
                bg="#FFF3E0", fg="#0288D1").grid(row=5, column=0, pady=(20, 5))
        self.normal_preview = tk.Label(preview_frame, text="Keine Vorschau", relief="ridge", 
                                      bg="#E1F5FE", bd=3)
        self.normal_preview.grid(row=6, column=0, padx=5, pady=5)
        
        tk.Label(preview_frame, text="🎨 Albedo/Base Color", font=("Arial", 9, "bold"), 
                bg="#FFF3E0", fg="#C2185B").grid(row=5, column=1, pady=(20, 5))
        self.albedo_preview = tk.Label(preview_frame, text="Keine Vorschau", relief="ridge", 
                                      bg="#FCE4EC", bd=3)
        self.albedo_preview.grid(row=6, column=1, padx=5, pady=5)
        
        tk.Label(preview_frame, text="🌈 Alle Bestandteile", font=("Arial", 9, "bold"), 
                bg="#FFF3E0", fg="#00897B").grid(row=5, column=2, pady=(20, 5))
        self.combined_preview = tk.Label(preview_frame, text="Keine Vorschau", relief="ridge", 
                                        bg="#E0F2F1", bd=3)
        self.combined_preview.grid(row=6, column=2, padx=5, pady=5)
        
        # Grid-Konfiguration
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        control_frame.rowconfigure(10, weight=1)
    
    def apply_material_preset(self, event=None):
        """Wendet Material-Presets an"""
        preset = self.material_preset.get()
        
        presets = {
            "Standard": {"ao": 255, "roughness": 128, "metallic": 0},
            "Metall": {"ao": 255, "roughness": 30, "metallic": 255},
            "Holz": {"ao": 200, "roughness": 180, "metallic": 0},
            "Stein": {"ao": 220, "roughness": 200, "metallic": 0},
            "Glas": {"ao": 255, "roughness": 10, "metallic": 0},
            "Stoff": {"ao": 230, "roughness": 220, "metallic": 0}
        }
        
        if preset in presets:
            self.default_ao_value.set(presets[preset]["ao"])
            self.default_roughness_value.set(presets[preset]["roughness"])
            self.default_metallic_value.set(presets[preset]["metallic"])
            self.log(f"Preset '{preset}' angewendet")
    
    def zoom_in(self):
        """Vergrößert die Vorschaubilder"""
        self.zoom_level = min(self.zoom_level + 0.25, 3.0)
        self.refresh_current_preview()
    
    def zoom_out(self):
        """Verkleinert die Vorschaubilder"""
        self.zoom_level = max(self.zoom_level - 0.25, 0.5)
        self.refresh_current_preview()
    
    def reset_zoom(self):
        """Setzt Zoom zurück"""
        self.zoom_level = 1.0
        self.refresh_current_preview()
    
    def refresh_current_preview(self):
        """Aktualisiert Vorschau mit neuem Zoom"""
        if self.texture_list:
            self.show_current_texture()
    
    def show_histogram(self, map_type):
        """Zeigt Histogramm für eine Map an"""
        if not self.texture_list:
            return
        
        texture_info = self.texture_list[self.current_texture_index]
        base_name = texture_info['base_name']
        texture_dir = texture_info['dir']
        
        # Finde entsprechende Datei mit JSON-Konfiguration
        file_path = None
        if map_type == "AO":
            file_path = self.find_texture_file(texture_dir, base_name, self.get_suffixes("ao"))
        elif map_type == "Roughness":
            file_path = self.find_texture_file(texture_dir, base_name, self.get_suffixes("roughness"))
        elif map_type == "Metallic":
            file_path = self.find_texture_file(texture_dir, base_name, self.get_suffixes("metallic"))
        
        if not file_path or not os.path.exists(file_path):
            messagebox.showinfo("Info", f"{map_type} Map nicht gefunden")
            return
        
        # Erstelle Histogramm-Fenster
        self.create_histogram_window(file_path, map_type, base_name)
    
    def create_histogram_window(self, file_path, map_type, material_name):
        """Erstellt ein Fenster mit Histogramm"""
        try:
            import numpy as np
            
            hist_window = tk.Toplevel(self.root)
            hist_window.title(f"Histogramm: {map_type} - {material_name}")
            hist_window.geometry("600x400")
            
            # Lade Bild
            img = Image.open(file_path).convert('L')
            img_array = np.array(img)
            
            # Berechne Statistiken
            mean_val = np.mean(img_array)
            min_val = np.min(img_array)
            max_val = np.max(img_array)
            std_val = np.std(img_array)
            
            # Zeige Statistiken
            stats_frame = ttk.Frame(hist_window, padding="10")
            stats_frame.pack(fill=tk.X)
            
            ttk.Label(stats_frame, text=f"Durchschnitt: {mean_val:.2f}").pack(side=tk.LEFT, padx=10)
            ttk.Label(stats_frame, text=f"Min: {min_val}").pack(side=tk.LEFT, padx=10)
            ttk.Label(stats_frame, text=f"Max: {max_val}").pack(side=tk.LEFT, padx=10)
            ttk.Label(stats_frame, text=f"Std.Abw.: {std_val:.2f}").pack(side=tk.LEFT, padx=10)
            
            # Warnung bei ungewöhnlichen Werten
            if self.warn_unusual_values.get():
                warning_text = ""
                if map_type == "Roughness" and (mean_val < 20 or mean_val > 235):
                    warning_text = "⚠️ Ungewöhnliche Roughness-Werte!"
                elif map_type == "Metallic" and min_val > 50 and max_val < 200:
                    warning_text = "⚠️ Metallic Map scheint keinen vollständigen Bereich zu nutzen!"
                
                if warning_text:
                    ttk.Label(hist_window, text=warning_text, foreground="orange", 
                            font=("Arial", 10, "bold")).pack(pady=10)
            
            # Histogramm (einfache Text-Darstellung)
            hist, bins = np.histogram(img_array, bins=16, range=(0, 256))
            max_hist = np.max(hist)
            
            canvas_frame = ttk.Frame(hist_window)
            canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            canvas = tk.Canvas(canvas_frame, bg="white")
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Zeichne Balken
            def draw_histogram():
                canvas.delete("all")
                width = canvas.winfo_width()
                height = canvas.winfo_height()
                
                bar_width = width / len(hist)
                for i, count in enumerate(hist):
                    bar_height = (count / max_hist) * (height - 40) if max_hist > 0 else 0
                    x1 = i * bar_width
                    y1 = height - bar_height - 20
                    x2 = (i + 1) * bar_width - 2
                    y2 = height - 20
                    canvas.create_rectangle(x1, y1, x2, y2, fill="steelblue", outline="darkblue")
                
                # Achsenbeschriftung
                for i in range(0, 256, 64):
                    x = (i / 256) * width
                    canvas.create_text(x, height - 5, text=str(i), font=("Arial", 8))
            
            hist_window.after(100, draw_histogram)
            canvas.bind("<Configure>", lambda e: draw_histogram())
            
        except ImportError:
            messagebox.showerror("Fehler", "NumPy wird für Histogramme benötigt")
        except Exception as e:
            messagebox.showerror("Fehler", f"Histogramm-Fehler: {str(e)}")
    
    def batch_scale_textures(self):
        """Skaliert alle Texturen auf Zielauflösung"""
        if not self.texture_list:
            messagebox.showwarning("Warnung", "Bitte zuerst Texturen laden!")
            return
        
        if self.target_resolution.get() == "original":
            messagebox.showinfo("Info", "Bitte Zielauflösung in 'Erweitert' festlegen!")
            return
        
        target_size = int(self.target_resolution.get())
        
        if messagebox.askyesno("Batch Skalierung", 
                              f"Alle Texturen auf {target_size}x{target_size} skalieren?\n" +
                              f"Output: {self.output_dir.get() or self.input_dir.get()}\\{target_size}\\"):
            thread = threading.Thread(target=self._batch_scale_thread, args=(target_size,))
            thread.daemon = True
            thread.start()
    
    def _batch_scale_thread(self, target_size):
        """Thread für Batch-Skalierung"""
        try:
            base_output_dir = self.output_dir.get() or self.input_dir.get()
            output_dir = os.path.join(base_output_dir, str(target_size))
            os.makedirs(output_dir, exist_ok=True)
            
            self.status.set(f"Skaliere Texturen auf {target_size}x{target_size}...")
            self.progress.set(0)
            
            processed = 0
            total_files = 0
            
            for i, texture_info in enumerate(self.texture_list):
                base_name = texture_info['base_name']
                texture_dir = texture_info['dir']
                
                progress_percent = (i / len(self.texture_list)) * 100
                self.progress.set(progress_percent)
                self.status.set(f"Skaliere: {base_name}")
                
                # Finde alle Texturen für dieses Material
                all_textures = [
                    ("albedo", texture_info['albedo_file']),
                    ("normal", self.find_texture_file_with_ogl(texture_dir, base_name, self.get_suffixes("normal"))),
                    ("ao", self.find_texture_file(texture_dir, base_name, self.get_suffixes("ao"))),
                    ("roughness", self.find_texture_file(texture_dir, base_name, self.get_suffixes("roughness"))),
                    ("metallic", self.find_texture_file(texture_dir, base_name, self.get_suffixes("metallic"))),
                    ("height", self.find_texture_file(texture_dir, base_name, self.get_suffixes("height"))),
                    ("emission", self.find_texture_file(texture_dir, base_name, self.get_suffixes("emission")))
                ]
                
                for map_type, texture_file in all_textures:
                    if texture_file and os.path.exists(texture_file):
                        try:
                            img = Image.open(texture_file)
                            
                            # Nur skalieren wenn nötig
                            if img.size != (target_size, target_size):
                                # Verwende LANCZOS für beste Qualität beim Verkleinern
                                # und BICUBIC für Vergrößern
                                if img.size[0] > target_size:
                                    resample = Image.Resampling.LANCZOS
                                else:
                                    resample = Image.Resampling.BICUBIC
                                
                                img = img.resize((target_size, target_size), resample)
                            
                            # Generiere Ausgabename
                            ext = self.output_format.get().lower()
                            output_name = f"{base_name}_{map_type}.{ext}"
                            output_path = os.path.join(output_dir, output_name)
                            
                            self.save_image_with_format(img, output_path)
                            total_files += 1
                            
                        except Exception as e:
                            self.log(f"Fehler bei {base_name}_{map_type}: {str(e)}")
                
                processed += 1
            
            # Jetzt ORM-Maps für die skalierten Texturen generieren
            self.log("=" * 50)
            self.log("Generiere ORM-Maps für skalierte Texturen...")
            orm_created = 0
            
            for i, texture_info in enumerate(self.texture_list):
                base_name = texture_info['base_name']
                
                progress_percent = (i / len(self.texture_list)) * 100
                self.progress.set(progress_percent)
                self.status.set(f"ORM: {base_name}")
                
                # Erstelle ORM aus den skalierten Texturen
                try:
                    # Lade skalierte Texturen
                    ao_file = os.path.join(output_dir, f"{base_name}_ao.{self.output_format.get().lower()}")
                    roughness_file = os.path.join(output_dir, f"{base_name}_roughness.{self.output_format.get().lower()}")
                    metallic_file = os.path.join(output_dir, f"{base_name}_metallic.{self.output_format.get().lower()}")
                    
                    # Prüfe ob alle Maps vorhanden sind
                    maps_exist = os.path.exists(ao_file) and os.path.exists(roughness_file) and os.path.exists(metallic_file)
                    
                    if maps_exist or self.fill_missing_maps.get():
                        # Lade oder erstelle Maps
                        if os.path.exists(ao_file):
                            ao_img = Image.open(ao_file).convert("L")
                        else:
                            ao_img = Image.new("L", (target_size, target_size), self.default_ao_value.get())
                        
                        if os.path.exists(roughness_file):
                            roughness_img = Image.open(roughness_file).convert("L")
                        else:
                            roughness_img = Image.new("L", (target_size, target_size), self.default_roughness_value.get())
                        
                        if os.path.exists(metallic_file):
                            metallic_img = Image.open(metallic_file).convert("L")
                        else:
                            metallic_img = Image.new("L", (target_size, target_size), self.default_metallic_value.get())
                        
                        # Erstelle ORM
                        orm_map = Image.merge("RGB", (ao_img, roughness_img, metallic_img))
                        orm_path = os.path.join(output_dir, f"{base_name}_ORM.{self.output_format.get().lower()}")
                        self.save_image_with_format(orm_map, orm_path)
                        orm_created += 1
                        self.log(f"ORM erstellt: {base_name}")
                    
                except Exception as e:
                    self.log(f"Fehler bei ORM für {base_name}: {str(e)}")
            
            # Jetzt GLTF-Dateien erstellen
            self.log("=" * 50)
            self.log("Generiere GLTF-Dateien...")
            gltf_created = 0
            
            for i, texture_info in enumerate(self.texture_list):
                base_name = texture_info['base_name']
                
                progress_percent = (i / len(self.texture_list)) * 100
                self.progress.set(progress_percent)
                self.status.set(f"GLTF: {base_name}")
                
                try:
                    # Erstelle Texture-Dictionary mit relativen Pfaden
                    gltf_textures = {}
                    
                    # Prüfe welche Texturen existieren
                    for map_type, texture_key in [("albedo", "baseColor"), ("normal", "normal"), ("emission", "emission")]:
                        texture_path = os.path.join(output_dir, f"{base_name}_{map_type}.{self.output_format.get().lower()}")
                        if os.path.exists(texture_path):
                            gltf_textures[texture_key] = f"./{target_size}/{base_name}_{map_type}.{self.output_format.get().lower()}"
                    
                    # ORM Map
                    orm_path = os.path.join(output_dir, f"{base_name}_ORM.{self.output_format.get().lower()}")
                    if os.path.exists(orm_path):
                        gltf_textures['orm'] = f"./{target_size}/{base_name}_ORM.{self.output_format.get().lower()}"
                    
                    # Erstelle GLTF nur wenn mindestens eine Textur vorhanden ist
                    if gltf_textures:
                        gltf_data = self._create_gltf_structure(base_name, gltf_textures)
                        gltf_file = os.path.join(output_dir, f"{base_name}.gltf")
                        
                        with open(gltf_file, 'w') as f:
                            import json
                            json.dump(gltf_data, f, indent=2)
                        
                        gltf_created += 1
                        self.log(f"GLTF erstellt: {base_name}.gltf")
                
                except Exception as e:
                    self.log(f"Fehler bei GLTF für {base_name}: {str(e)}")
            
            self.progress.set(100)
            self.status.set("Batch-Verarbeitung abgeschlossen!")
            self.log("=" * 50)
            self.log("Zusammenfassung:")
            self.log(f"  Texturen: {total_files}")
            self.log(f"  ORM-Maps: {orm_created}")
            self.log(f"  GLTF-Dateien: {gltf_created}")
            self.log(f"  Zielordner: {output_dir}")
            
            messagebox.showinfo("Fertig", 
                              "Batch-Verarbeitung abgeschlossen!\n" +
                              f"Materialien: {processed}\n" +
                              f"Texturen: {total_files}\n" +
                              f"ORM-Maps: {orm_created}\n" +
                              f"GLTF-Dateien: {gltf_created}\n" +
                              f"Größe: {target_size}x{target_size}\n" +
                              f"Ordner: {target_size}\\")
            
        except Exception as e:
            self.log(f"FEHLER: {str(e)}")
            self.status.set("Fehler bei Skalierung")
            messagebox.showerror("Fehler", f"Fehler bei Skalierung:\n{str(e)}")
    
    def batch_export_gltf(self):
        """Exportiert alle Materialien als GLTF"""
        if not self.texture_list:
            messagebox.showwarning("Warnung", "Bitte zuerst Texturen laden!")
            return
        
        if messagebox.askyesno("Batch Export", f"Alle {len(self.texture_list)} Materialien als GLTF exportieren?"):
            self.generate_gltf()
    
    def browse_input_dir(self):
        directory = filedialog.askdirectory(title="Eingabe-Verzeichnis auswählen")
        if directory:
            self.input_dir.set(directory)
            self.output_dir.set(directory)
            # Automatisch Texturen laden
            self.load_textures()
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Ausgabe-Verzeichnis auswählen")
        if directory:
            self.output_dir.set(directory)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def load_textures(self):
        if not self.input_dir.get():
            messagebox.showerror("Fehler", "Bitte Eingabe-Verzeichnis auswählen!")
            return
        
        thread = threading.Thread(target=self._load_textures_thread)
        thread.daemon = True
        thread.start()
    
    def _load_textures_thread(self):
        import shutil
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        self.status.set("Suche Texturen...")
        self.log_text.delete(1.0, tk.END)
        # Alle Albedo-Texturen finden
        albedo_files = []
        albedo_suffixes = self.get_suffixes("albedo")
        extensions = self.get_extensions()
        separators = self.get_separators()
        resolutions = self.get_resolutions()
        preferred_res = self.preferred_resolution.get()
        for suffix in albedo_suffixes:
            for ext in extensions:
                for sep in separators:
                    pattern = f"*{sep}{suffix}.{ext}"
                    albedo_files.extend(glob.glob(os.path.join(input_dir, pattern)))
                    if self.recursive_search.get():
                        albedo_files.extend(glob.glob(os.path.join(input_dir, "**", pattern), recursive=True))
                    if preferred_res == "auto":
                        search_resolutions = resolutions
                    else:
                        search_resolutions = [preferred_res] + [r for r in resolutions if r != preferred_res]
                    for res in search_resolutions:
                        pattern_res = f"*{sep}{suffix}_{res}.{ext}"
                        albedo_files.extend(glob.glob(os.path.join(input_dir, pattern_res)))
                        if self.recursive_search.get():
                            albedo_files.extend(glob.glob(os.path.join(input_dir, "**", pattern_res), recursive=True))
        albedo_files = list(set(albedo_files))
        if not albedo_files:
            self.log("Keine Texturen gefunden!")
            self.status.set("Fehler: Keine Texturen gefunden")
            return
        # Extrahiere Base-Namen und kopiere alle relevanten Texturen ins Ausgabe-Verzeichnis
        self.texture_list = []
        map_types = [
            ("albedo", self.get_suffixes("albedo")),
            ("normal", self.get_suffixes("normal")),
            ("ao", self.get_suffixes("ao")),
            ("roughness", self.get_suffixes("roughness")),
            ("metallic", self.get_suffixes("metallic")),
            ("height", self.get_suffixes("height")),
            ("emission", self.get_suffixes("emission")),
        ]
        for albedo_file in albedo_files:
            base_name = os.path.basename(albedo_file)
            base_name_clean = None
            for suffix in albedo_suffixes:
                for ext in extensions:
                    for sep in separators:
                        full_suffix = f"{sep}{suffix}.{ext}"
                        if base_name.endswith(full_suffix):
                            base_name_clean = base_name[:-(len(full_suffix))]
                            break
                        for res in resolutions:
                            full_suffix_res = f"{sep}{suffix}_{res}.{ext}"
                            if base_name.endswith(full_suffix_res):
                                base_name_clean = base_name[:-(len(full_suffix_res))]
                                break
                        else:
                            continue
                        break
                    else:
                        continue
                    break
                else:
                    continue
                break
            if base_name_clean is None:
                continue
            texture_entry = {'base_name': base_name_clean, 'dir': output_dir if output_dir else os.path.dirname(albedo_file)}
            # Kopiere und finde alle relevanten Texturen
            for map_type, suffixes in map_types:
                found_file = None
                if map_type == "albedo":
                    found_file = albedo_file
                elif map_type == "normal":
                    found_file = self.find_texture_file_with_ogl(os.path.dirname(albedo_file), base_name_clean, suffixes)
                else:
                    found_file = self.find_texture_file(os.path.dirname(albedo_file), base_name_clean, suffixes)
                if found_file and os.path.exists(found_file):
                    if output_dir and os.path.abspath(os.path.dirname(found_file)) != os.path.abspath(output_dir):
                        dst = os.path.join(output_dir, os.path.basename(found_file))
                        try:
                            shutil.copy2(found_file, dst)
                            found_file_out = dst
                        except Exception as copy_err:
                            self.log(f"WARNUNG: Konnte {found_file} nicht kopieren: {copy_err}")
                            found_file_out = found_file
                    else:
                        found_file_out = found_file
                    texture_entry[f"{map_type}_file"] = found_file_out
                else:
                    texture_entry[f"{map_type}_file"] = None
            self.texture_list.append(texture_entry)
        self.current_texture_index = 0
        self.log(f"Gefunden: {len(self.texture_list)} Textur-Sets")
        self.status.set(f"{len(self.texture_list)} Texturen geladen")
        if self.texture_list:
            self.show_current_texture()
    
    def show_current_texture(self):
        if not self.texture_list:
            return
        
        texture_info = self.texture_list[self.current_texture_index]
        base_name = texture_info['base_name']
        texture_dir = texture_info['dir']
        
        self.texture_label.config(text=f"Textur {self.current_texture_index + 1}/{len(self.texture_list)}: {base_name}")
        
        # Finde Textur-Dateien mit JSON-Konfiguration
        normal_file = self.find_texture_file_with_ogl(texture_dir, base_name, self.get_suffixes("normal"))
        ao_file = self.find_texture_file(texture_dir, base_name, self.get_suffixes("ao"))
        roughness_file = self.find_texture_file(texture_dir, base_name, self.get_suffixes("roughness"))
        metallic_file = self.find_texture_file(texture_dir, base_name, self.get_suffixes("metallic"))
        height_file = self.find_texture_file(texture_dir, base_name, self.get_suffixes("height"))
        emission_file = self.find_texture_file(texture_dir, base_name, self.get_suffixes("emission"))
        
        # Falls AO fehlt, Height verwenden
        if not ao_file and height_file and self.use_height_for_ao.get():
            ao_file = height_file
        
        # ORM Datei prüfen
        output_dir = self.output_dir.get() or os.path.join(texture_dir, "ORM_Maps")
        orm_file = os.path.join(output_dir, f"{base_name}_ORM.png")
        
        # Zeige Previews
        self.show_preview_image(normal_file, self.normal_preview, "Normal fehlt")
        self.show_preview_image(texture_info['albedo_file'], self.albedo_preview, "Albedo fehlt")
        self.show_preview_image(ao_file, self.ao_preview, "AO fehlt")
        self.show_preview_image(roughness_file, self.roughness_preview, "Roughness fehlt")
        self.show_preview_image(metallic_file, self.metallic_preview, "Metallic fehlt")
        self.show_preview_image(emission_file, self.emission_preview, "Emission fehlt")
        
        # Erstelle kombinierte Preview (alle Bestandteile)
        self.create_combined_preview(texture_info['albedo_file'], normal_file, ao_file, 
                                    roughness_file, metallic_file, height_file, emission_file)
        
        if os.path.exists(orm_file):
            self.show_preview_image(orm_file, self.orm_preview, "ORM Map")
        else:
            self.orm_preview.config(image='', text="Noch nicht generiert")
    
    def find_texture_file(self, directory, base_name, suffixes):
        extensions = self.get_extensions()
        separators = self.get_separators()
        resolutions = self.get_resolutions()
        
        for suffix in suffixes:
            for sep in separators:
                for ext in extensions:
                    # Standard: material_rough.jpg
                    path = os.path.join(directory, f"{base_name}{sep}{suffix}.{ext}")
                    if os.path.exists(path):
                        return path
                    
                    # Polyhaven: material_rough_1k.jpg
                    for res in resolutions:
                        path_res = os.path.join(directory, f"{base_name}{sep}{suffix}_{res}.{ext}")
                        if os.path.exists(path_res):
                            return path_res
        return None
    
    def find_texture_file_with_ogl(self, directory, base_name, suffixes):
        """Spezielle Suche für Normal-Maps die oft -ogl oder Nummern haben"""
        extensions = self.get_extensions()
        separators = self.get_separators()
        resolutions = self.get_resolutions()
        
        # Erst normale Suche (inkl. Polyhaven-Auflösungen)
        result = self.find_texture_file(directory, base_name, suffixes)
        if result:
            return result
        
        # Dann mit -ogl und Nummern
        import glob as glob_mod
        for suffix in suffixes:
            for sep in separators:
                for ext in extensions:
                    # Polyhaven: material_nor_gl_1k.jpg (with underscore before resolution)
                    for res in resolutions:
                        # Pattern: *_nor_gl_1k.jpg
                        pattern = os.path.join(directory, f"{base_name}{sep}{suffix}_{res}.{ext}")
                        matches = glob_mod.glob(pattern)
                        if matches:
                            return matches[0]
                    
                    # Mit -ogl Suffix: material_normal-ogl.jpg
                    pattern = os.path.join(directory, f"{base_name}{sep}{suffix}*-ogl.{ext}")
                    matches = glob_mod.glob(pattern)
                    if matches:
                        return matches[0]
                    
                    # Mit Nummern: material_normal4.jpg
                    pattern = os.path.join(directory, f"{base_name}{sep}{suffix}[0-9].{ext}")
                    matches = glob_mod.glob(pattern)
                    if matches:
                        return matches[0]
        
        return None
    
    def show_preview_image(self, file_path, label_widget, fallback_text):
        if not file_path or not os.path.exists(file_path):
            label_widget.config(image='', text=fallback_text)
            return
        
        try:
            # Cache-Key
            cache_key = f"{file_path}_{self.zoom_level}"
            
            # Prüfe Cache
            if cache_key in self.preview_cache:
                photo = self.preview_cache[cache_key]
            else:
                img = Image.open(file_path)
                base_size = int(200 * self.zoom_level)
                img.thumbnail((base_size, base_size), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # In Cache speichern (max 50 Bilder)
                if len(self.preview_cache) > 50:
                    # Älteste Einträge entfernen
                    self.preview_cache.pop(next(iter(self.preview_cache)))
                self.preview_cache[cache_key] = photo
            
            # Speichere Referenz
            label_widget.image = photo
            label_widget.config(image=photo, text='')
            
            # Validierung
            if self.validate_resolution.get():
                img_for_check = Image.open(file_path)
                if img_for_check.size[0] != img_for_check.size[1]:
                    label_widget.config(text=f"⚠️ Nicht quadratisch\n{img_for_check.size[0]}x{img_for_check.size[1]}")
        except Exception as e:
            label_widget.config(image='', text=f"Fehler: {str(e)[:20]}")
    
    def create_combined_preview(self, albedo_file, normal_file, ao_file, 
                               roughness_file, metallic_file, height_file, emission_file=None):
        """Erstellt eine kombinierte Vorschau - zeigt wie das Material aussehen würde"""
        try:
            # Lade Basis-Textur (Albedo)
            if not albedo_file or not os.path.exists(albedo_file):
                self.combined_preview.config(image='', text="Albedo fehlt")
                return
            
            base_img = Image.open(albedo_file).convert('RGB')
            width, height = base_img.size
            
            # Erstelle Pixel-Arrays für Verarbeitung
            import numpy as np
            albedo_data = np.array(base_img, dtype=np.float32) / 255.0
            
            # Lade AO und multipliziere mit Albedo (dunkelt Schatten ab)
            if ao_file and os.path.exists(ao_file):
                ao_img = Image.open(ao_file).convert('L').resize((width, height), Image.Resampling.LANCZOS)
                ao_data = np.array(ao_img, dtype=np.float32) / 255.0
                albedo_data *= ao_data[:, :, np.newaxis]
            
            # Simuliere Roughness-Effekt (weichere Albedo bei hoher Roughness)
            if roughness_file and os.path.exists(roughness_file):
                rough_img = Image.open(roughness_file).convert('L').resize((width, height), Image.Resampling.LANCZOS)
                rough_data = np.array(rough_img, dtype=np.float32) / 255.0
                # Leichtes Blur für raue Bereiche simulieren
                roughness_factor = 0.85 + (rough_data * 0.15)
                albedo_data *= roughness_factor[:, :, np.newaxis]
            
            # Simuliere Metallic-Effekt (metallische Bereiche reflektieren mehr)
            if metallic_file and os.path.exists(metallic_file):
                metal_img = Image.open(metallic_file).convert('L').resize((width, height), Image.Resampling.LANCZOS)
                metal_data = np.array(metal_img, dtype=np.float32) / 255.0
                # Metallische Bereiche sind glänzender (heller)
                metallic_boost = 1.0 + (metal_data * 0.3)
                albedo_data *= metallic_boost[:, :, np.newaxis]
            
            # Addiere Emission (selbstleuchtend, unabhängig von Beleuchtung)
            if emission_file and os.path.exists(emission_file):
                emission_img = Image.open(emission_file).convert('RGB').resize((width, height), Image.Resampling.LANCZOS)
                emission_data = np.array(emission_img, dtype=np.float32) / 255.0
                # Emission wird addiert (nicht multipliziert) - leuchtet selbst
                albedo_data += emission_data * 0.5  # 50% Stärke für bessere Sichtbarkeit
            
            # Konvertiere zurück zu Bild
            result_data = np.clip(albedo_data * 255.0, 0, 255).astype(np.uint8)
            result_img = Image.fromarray(result_data, mode='RGB')
            
            # Skaliere für Vorschau
            result_img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(result_img)
            
            # Speichere Referenz (verhindert Garbage Collection)
            self.combined_preview.image = photo  # type: ignore
            self.combined_preview.config(image=photo, text='')
            
        except Exception as e:
            self.combined_preview.config(image='', text=f"Fehler: {str(e)[:30]}")
    
    def prev_texture(self):
        if not self.texture_list:
            return
        self.current_texture_index = (self.current_texture_index - 1) % len(self.texture_list)
        self.show_current_texture()
    
    def next_texture(self):
        if not self.texture_list:
            return
        self.current_texture_index = (self.current_texture_index + 1) % len(self.texture_list)
        self.show_current_texture()
    
    def start_generation(self):
        if not self.input_dir.get() or not self.output_dir.get():
            messagebox.showerror("Fehler", "Bitte Eingabe- und Ausgabe-Verzeichnis auswählen!")
            return
        
        if not self.texture_list:
            messagebox.showwarning("Warnung", "Bitte zuerst Texturen laden!")
            return
        
        thread = threading.Thread(target=self.generate_orm_maps)
        thread.daemon = True
        thread.start()
    
    def generate_missing_maps(self):
        """Generiert nur fehlende Einzeltexturen (AO, Roughness, Metallic) als separate Dateien"""
        if not self.texture_list:
            messagebox.showwarning("Warnung", "Bitte zuerst Texturen laden!")
            return
        
        if not self.input_dir.get():
            messagebox.showerror("Fehler", "Bitte Eingabe-Verzeichnis auswählen!")
            return
        
        thread = threading.Thread(target=self._generate_missing_maps_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_missing_maps_thread(self):
        """Thread-Funktion für Generierung fehlender Maps"""
        try:
            self.status.set("Generiere fehlende Maps...")
            self.progress.set(0)
            
            generated = 0
            skipped = 0
            log_data = []
            
            for i, texture_info in enumerate(self.texture_list):
                base_name = texture_info['base_name']
                texture_dir = texture_info['dir']
                output_dir = self.output_dir.get() or texture_dir
                
                progress_percent = (i / len(self.texture_list)) * 100
                self.progress.set(progress_percent)
                self.status.set(f"Prüfe: {base_name}")
                
                # Prüfe welche Maps fehlen
                ao_file = self.find_texture_file(texture_dir, base_name, self.get_suffixes("ao"))
                roughness_file = self.find_texture_file(texture_dir, base_name, self.get_suffixes("roughness"))
                metallic_file = self.find_texture_file(texture_dir, base_name, self.get_suffixes("metallic"))
                
                # Bestimme Zielgröße
                reference_img = None
                if texture_info['albedo_file']:
                    reference_img = Image.open(texture_info['albedo_file'])
                
                if reference_img:
                    target_size = reference_img.size
                else:
                    target_size = (1024, 1024)
                
                created_maps = []
                
                # Erstelle fehlende AO
                if not ao_file:
                    ao_value = self.default_ao_value.get()
                    ao_img = Image.new("L", target_size, ao_value)
                    ao_path = os.path.join(output_dir, f"{base_name}_ao.{self.output_format.get().lower()}")
                    os.makedirs(output_dir, exist_ok=True)
                    self.save_image_with_format(ao_img, ao_path)
                    created_maps.append("AO")
                
                # Erstelle fehlende Roughness oder invertiere Gloss
                if not roughness_file or (roughness_file and "gloss" in os.path.basename(roughness_file).lower() and self.invert_gloss.get()):
                    if roughness_file and "gloss" in os.path.basename(roughness_file).lower():
                        # Invertiere Gloss zu Roughness
                        gloss_img = Image.open(roughness_file).convert("L")
                        from PIL import ImageOps
                        rough_img = ImageOps.invert(gloss_img)
                        created_maps.append("Roughness (invertiert)")
                    else:
                        # Erstelle neue
                        rough_value = self.default_roughness_value.get()
                        rough_img = Image.new("L", target_size, rough_value)
                        created_maps.append("Roughness")
                    
                    rough_path = os.path.join(output_dir, f"{base_name}_roughness.{self.output_format.get().lower()}")
                    os.makedirs(output_dir, exist_ok=True)
                    self.save_image_with_format(rough_img, rough_path)
                
                # Erstelle fehlende Metallic
                if not metallic_file:
                    metal_value = self.default_metallic_value.get()
                    metal_img = Image.new("L", target_size, metal_value)
                    metal_path = os.path.join(output_dir, f"{base_name}_metallic.{self.output_format.get().lower()}")
                    os.makedirs(output_dir, exist_ok=True)
                    self.save_image_with_format(metal_img, metal_path)
                    created_maps.append("Metallic")
                
                if created_maps:
                    self.log(f"Erstellt für {base_name}: {', '.join(created_maps)}")
                    generated += 1
                    log_data.append({"material": base_name, "created": ", ".join(created_maps)})
                else:
                    skipped += 1
            
            self.progress.set(100)
            self.status.set("Fehlende Maps generiert!")
            self.log("=" * 50)
            self.log(f"Materialien mit erstellten Maps: {generated}, Vollständig: {skipped}")
            
            # Export Log
            if self.export_log.get() and log_data:
                self.export_process_log(log_data, "missing_maps")
            
            messagebox.showinfo("Fertig", f"Fehlende Maps generiert!\nBearbeitet: {generated}\nVollständig: {skipped}")
            
        except Exception as e:
            self.log(f"FEHLER: {str(e)}")
            self.status.set("Fehler aufgetreten")
            messagebox.showerror("Fehler", f"Fehler bei Map-Generierung:\n{str(e)}")
    
    def save_image_with_format(self, img, path):
        """Speichert Bild im gewählten Format mit Kompression"""
        format_ext = self.output_format.get()
        
        if format_ext == "PNG":
            img.save(path, "PNG", optimize=True)
        elif format_ext == "JPEG":
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(path, "JPEG", quality=self.compression_quality.get(), optimize=True)
        elif format_ext == "JP2":
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(path, "JPEG2000", quality_mode="dB", quality_layers=[self.compression_quality.get()])
    
    def export_process_log(self, log_data, operation_name):
        """Exportiert Verarbeitungslog"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = self.output_dir.get() or self.input_dir.get()
            log_file = None
            
            if self.log_format.get() == "CSV":
                log_file = os.path.join(output_dir, f"log_{operation_name}_{timestamp}.csv")
                with open(log_file, 'w', newline='', encoding='utf-8') as f:
                    if log_data:
                        writer = csv.DictWriter(f, fieldnames=log_data[0].keys())
                        writer.writeheader()
                        writer.writerows(log_data)
                        
            elif self.log_format.get() == "JSON":
                log_file = os.path.join(output_dir, f"log_{operation_name}_{timestamp}.json")
                with open(log_file, 'w', encoding='utf-8') as f:
                    json.dump(log_data, f, indent=2, ensure_ascii=False)
                    
            elif self.log_format.get() == "TXT":
                log_file = os.path.join(output_dir, f"log_{operation_name}_{timestamp}.txt")
                with open(log_file, 'w', encoding='utf-8') as f:
                    for entry in log_data:
                        f.write(f"{entry}\n")
            
            if log_file:
                self.log(f"Log gespeichert: {os.path.basename(log_file)}")
            
        except Exception as e:
            self.log(f"Log-Export-Fehler: {str(e)}")
    
    def generate_orm_maps(self):
        try:
            base_output_dir = self.output_dir.get()
            
            # Wenn Zielauflösung gesetzt ist, erstelle Unterordner
            if self.target_resolution.get() != "original":
                output_dir = os.path.join(base_output_dir, self.target_resolution.get())
            else:
                output_dir = base_output_dir
            
            os.makedirs(output_dir, exist_ok=True)
            
            self.status.set("Generiere ORM-Maps...")
            self.progress.set(0)
            
            processed = 0
            errors = 0
            
            for i, texture_info in enumerate(self.texture_list):
                base_name = texture_info['base_name']
                texture_dir = texture_info['dir']
                
                progress_percent = (i / len(self.texture_list)) * 100
                self.progress.set(progress_percent)
                self.status.set(f"Verarbeite: {base_name}")
                
                # Verwende Skalierung wenn gesetzt
                target_size = None
                if self.target_resolution.get() != "original":
                    target_size = int(self.target_resolution.get())
                
                success = self.create_single_orm_map(texture_dir, output_dir, base_name, target_size)
                
                if success:
                    processed += 1
                else:
                    errors += 1
            
            self.progress.set(100)
            self.status.set("Fertig!")
            self.log("=" * 50)
            self.log(f"Erfolgreich: {processed}, Fehler: {errors}")
            
            # Zeige ORM Preview nach Generierung
            if self.texture_list:
                self.show_current_texture()
            
            messagebox.showinfo("Fertig", f"Verarbeitung abgeschlossen!\nErfolgreich: {processed}\nFehler: {errors}")
            
        except Exception as e:
            self.log(f"FEHLER: {str(e)}")
            self.status.set("Fehler aufgetreten")
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten:\n{str(e)}")
    
    def create_single_orm_map(self, input_dir, output_dir, base_name, target_size=None):
        try:
            # Lade Suffix-Definitionen aus JSON
            ao_suffixes = self.get_suffixes("ao")
            roughness_suffixes = self.get_suffixes("roughness")
            metallic_suffixes = self.get_suffixes("metallic")
            height_suffixes = self.get_suffixes("height")
            
            def find_texture_file(base, suffix_list):
                extensions = self.get_extensions()
                separators = self.get_separators()
                resolutions = self.get_resolutions()
                
                for suffix in suffix_list:
                    for sep in separators:
                        for ext in extensions:
                            # Standard: material_rough.jpg
                            path = os.path.join(input_dir, f"{base}{sep}{suffix}.{ext}")
                            if os.path.exists(path):
                                return path
                            
                            # Polyhaven: material_rough_1k.jpg
                            for res in resolutions:
                                path_res = os.path.join(input_dir, f"{base}{sep}{suffix}_{res}.{ext}")
                                if os.path.exists(path_res):
                                    return path_res
                return None
            
            ao_file = find_texture_file(base_name, ao_suffixes)
            roughness_file = find_texture_file(base_name, roughness_suffixes)
            metallic_file = find_texture_file(base_name, metallic_suffixes)
            height_file = find_texture_file(base_name, height_suffixes)
            
            # Ausgabeformat
            output_ext = self.output_format.get().lower()
            output_file = os.path.join(output_dir, f"{base_name}_ORM.{output_ext}")
            
            if os.path.exists(output_file) and not self.overwrite_existing.get():
                self.log(f"Übersprungen: {base_name}")
                return True
            
            if self.use_height_for_ao.get() and not ao_file and height_file:
                ao_file = height_file
            
            # Prüfe ob fehlende Maps automatisch aufgefüllt werden sollen
            if not self.fill_missing_maps.get():
                # Alte Logik: Fehlende Maps führen zu Fehler
                missing_files = []
                if not ao_file:
                    missing_files.append("ao")
                if not roughness_file:
                    missing_files.append("roughness")
                if not metallic_file:
                    missing_files.append("metallic")
                
                if missing_files:
                    self.log(f"FEHLER {base_name}: Fehlende Dateien - {', '.join(missing_files)}")
                    return False
            
            # Bestimme Zielgröße
            if target_size:
                # Explizite Zielgröße übergeben
                final_size = (target_size, target_size)
            else:
                # Bestimme aus vorhandenen Dateien
                reference_img = None
                if ao_file:
                    reference_img = Image.open(ao_file)
                elif roughness_file:
                    reference_img = Image.open(roughness_file)
                elif metallic_file:
                    reference_img = Image.open(metallic_file)
                
                # Falls alle fehlen, verwende Standardgröße
                if reference_img:
                    final_size = reference_img.size
                else:
                    final_size = (1024, 1024)  # Standardgröße
            
            # Validierung: Auflösungskonsistenz (nur wenn nicht skaliert wird)
            if self.validate_resolution.get() and not target_size:
                sizes = []
                for f in [ao_file, roughness_file, metallic_file]:
                    if f and os.path.exists(f):
                        img = Image.open(f)
                        sizes.append(img.size)
                
                if len(set(sizes)) > 1:
                    self.log(f"WARNUNG {base_name}: Inkonsistente Auflösungen - {sizes}")
            
            # Lade oder erstelle AO (Standard: Weiß = keine Verdeckung)
            if ao_file and os.path.exists(ao_file):
                ao_img = Image.open(ao_file).convert("L")
                if ao_img.size != final_size:
                    resample = Image.Resampling.LANCZOS if ao_img.size[0] > final_size[0] else Image.Resampling.BICUBIC
                    ao_img = ao_img.resize(final_size, resample)
            elif self.fill_missing_maps.get():
                ao_value = self.default_ao_value.get()
                ao_img = Image.new("L", final_size, ao_value)
                self.log(f"INFO {base_name}: AO fehlt - verwende Wert {ao_value}")
            else:
                raise Exception("AO-Map fehlt")
            
            # Lade oder erstelle Roughness (Standard: Mittelgrau = semi-rough)
            if roughness_file and os.path.exists(roughness_file):
                roughness_img = Image.open(roughness_file).convert("L")
                
                # Prüfe ob es Gloss ist und invertieren
                if self.invert_gloss.get() and "gloss" in os.path.basename(roughness_file).lower():
                    from PIL import ImageOps
                    roughness_img = ImageOps.invert(roughness_img)
                    self.log(f"INFO {base_name}: Gloss zu Roughness invertiert")
                
                if roughness_img.size != final_size:
                    resample = Image.Resampling.LANCZOS if roughness_img.size[0] > final_size[0] else Image.Resampling.BICUBIC
                    roughness_img = roughness_img.resize(final_size, resample)
            elif self.fill_missing_maps.get():
                rough_value = self.default_roughness_value.get()
                roughness_img = Image.new("L", final_size, rough_value)
                self.log(f"INFO {base_name}: Roughness fehlt - verwende Wert {rough_value}")
            else:
                raise Exception("Roughness-Map fehlt")
            
            # Lade oder erstelle Metallic (Standard: Schwarz = nicht-metallisch)
            if metallic_file and os.path.exists(metallic_file):
                metallic_img = Image.open(metallic_file).convert("L")
                if metallic_img.size != final_size:
                    resample = Image.Resampling.LANCZOS if metallic_img.size[0] > final_size[0] else Image.Resampling.BICUBIC
                    metallic_img = metallic_img.resize(final_size, resample)
            elif self.fill_missing_maps.get():
                metal_value = self.default_metallic_value.get()
                metallic_img = Image.new("L", final_size, metal_value)
                self.log(f"INFO {base_name}: Metallic fehlt - verwende Wert {metal_value}")
            else:
                raise Exception("Metallic-Map fehlt")
            
            orm_map = Image.merge("RGB", (ao_img, roughness_img, metallic_img))
            
            os.makedirs(output_dir, exist_ok=True)
            self.save_image_with_format(orm_map, output_file)
            
            self.log(f"ERFOLG: {base_name}")
            return True
            
        except Exception as e:
            self.log(f"FEHLER {base_name}: {str(e)}")
            return False
    
    def generate_gltf(self):
        """Generiert GLTF-Dateien mit allen PBR-Texturen"""
        if not self.texture_list:
            messagebox.showwarning("Warnung", "Bitte zuerst Texturen laden!")
            return
        
        if not self.input_dir.get():
            messagebox.showerror("Fehler", "Bitte Eingabe-Verzeichnis auswählen!")
            return
        
        thread = threading.Thread(target=self._generate_gltf_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_gltf_thread(self):
        """Thread-Funktion für GLTF-Generierung (immer ins Ausgabeverzeichnis)"""
        try:
            import shutil
            import json
            self.status.set("Generiere GLTF-Dateien...")
            self.progress.set(0)
            output_dir = self.output_dir.get() or os.getcwd()
            os.makedirs(output_dir, exist_ok=True)
            generated = 0
            errors = 0
            for i, texture_info in enumerate(self.texture_list):
                base_name = texture_info['base_name']
                texture_dir = texture_info['dir']
                progress_percent = (i / len(self.texture_list)) * 100
                self.progress.set(progress_percent)
                self.status.set(f"GLTF: {base_name}")
                try:
                    # Alle relevanten Texturen suchen und ins Ausgabeverzeichnis kopieren
                    map_types = [
                        ("albedo", self.get_suffixes("albedo")),
                        ("normal", self.get_suffixes("normal")),
                        ("ao", self.get_suffixes("ao")),
                        ("roughness", self.get_suffixes("roughness")),
                        ("metallic", self.get_suffixes("metallic")),
                        ("height", self.get_suffixes("height")),
                        ("emission", self.get_suffixes("emission")),
                    ]
                    texture_files = {}
                    for map_type, suffixes in map_types:
                        if map_type == "albedo":
                            src = texture_info.get('albedo_file')
                        elif map_type == "normal":
                            src = self.find_texture_file_with_ogl(texture_dir, base_name, suffixes)
                        else:
                            src = self.find_texture_file(texture_dir, base_name, suffixes)
                        if src and os.path.exists(src):
                            dst = os.path.join(output_dir, f"{base_name}_{map_type}.{self.output_format.get().lower()}")
                            if not os.path.abspath(src) == os.path.abspath(dst):
                                try:
                                    shutil.copy2(src, dst)
                                except Exception as copy_err:
                                    self.log(f"WARNUNG: Konnte {src} nicht kopieren: {copy_err}")
                            texture_files[map_type] = dst
                    # ORM Map ggf. erzeugen oder kopieren
                    orm_file = os.path.join(output_dir, f"{base_name}_ORM.{self.output_format.get().lower()}")
                    if not os.path.exists(orm_file):
                        # Versuche ORM zu erzeugen
                        self.create_single_orm_map(output_dir, output_dir, base_name)
                    if os.path.exists(orm_file):
                        texture_files['orm'] = orm_file
                    # Erstelle Texture-Dictionary für GLTF
                    gltf_textures = {}
                    if 'albedo' in texture_files:
                        gltf_textures['baseColor'] = f"./{os.path.basename(texture_files['albedo'])}"
                    if 'normal' in texture_files:
                        gltf_textures['normal'] = f"./{os.path.basename(texture_files['normal'])}"
                    if 'emission' in texture_files:
                        gltf_textures['emission'] = f"./{os.path.basename(texture_files['emission'])}"
                    if 'orm' in texture_files:
                        gltf_textures['orm'] = f"./{os.path.basename(texture_files['orm'])}"
                    # GLTF-Datei schreiben
                    gltf_data = self._create_gltf_structure(base_name, gltf_textures)
                    gltf_file = os.path.join(output_dir, f"{base_name}.gltf")
                    with open(gltf_file, 'w', encoding='utf-8') as f:
                        json.dump(gltf_data, f, indent=2)
                    self.log(f"GLTF: {os.path.basename(gltf_file)}")
                    generated += 1
                except Exception as e:
                    self.log(f"FEHLER GLTF {base_name}: {str(e)}")
                    errors += 1
            self.progress.set(100)
            self.status.set("GLTF-Generierung abgeschlossen!")
            self.log("=" * 50)
            self.log(f"GLTF: {generated} erstellt, {errors} Fehler")
            messagebox.showinfo("Fertig", f"GLTF-Generierung abgeschlossen!\nErstellt: {generated}\nFehler: {errors}")
        except Exception as e:
            self.log(f"FEHLER: {str(e)}")
            self.status.set("Fehler bei GLTF-Generierung")
            messagebox.showerror("Fehler", f"GLTF-Generierung fehlgeschlagen:\n{str(e)}")
    
    def _create_gltf_structure(self, material_name, textures):
        """Erstellt GLTF 2.0 JSON-Struktur - kompatibel mit SecondLife/OpenSim"""
        gltf = {
            "asset": {
                "generator": "ORM-Maps-Tools NG - Advanced Edition",
                "version": "2.0"
            },
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [{
                "primitives": [{
                    "attributes": {
                        "POSITION": 1,
                        "TEXCOORD_0": 2
                    },
                    "indices": 0,
                    "material": 0
                }]
            }],
            "materials": [{
                "doubleSided": self.gltf_double_sided.get(),
                "name": material_name,
                "pbrMetallicRoughness": {
                    "metallicFactor": self.gltf_metallic_factor.get(),
                    "roughnessFactor": self.gltf_roughness_factor.get()
                },
                "alphaMode": self.gltf_alpha_mode.get()
            }],
            "textures": [],
            "images": [],
            "samplers": [{
                "magFilter": 9729,
                "minFilter": 9987,
                "wrapS": 33648,
                "wrapT": 33648
            }],
            "buffers": [{
                "uri": "data:application/gltf-buffer;base64,AAABAAIAAQADAAIAAAAAAAAAAAAAAAAAAACAPwAAAAAAAAAAAAAAAAAAgD8AAAAAAACAPwAAgD8AAAAAAAAAAAAAgD8AAAAAAACAPwAAgD8AAAAAAAAAAAAAAAAAAAAAAACAPwAAAAAAAAAA",
                "byteLength": 108
            }],
            "bufferViews": [
                {
                    "buffer": 0,
                    "byteOffset": 0,
                    "byteLength": 12,
                    "target": 34963
                },
                {
                    "buffer": 0,
                    "byteOffset": 12,
                    "byteLength": 96,
                    "byteStride": 12,
                    "target": 34962
                }
            ],
            "accessors": [
                {
                    "bufferView": 0,
                    "byteOffset": 0,
                    "componentType": 5123,
                    "count": 6,
                    "type": "SCALAR",
                    "max": [3],
                    "min": [0]
                },
                {
                    "bufferView": 1,
                    "byteOffset": 0,
                    "componentType": 5126,
                    "count": 4,
                    "type": "VEC3",
                    "max": [1.0, 1.0, 0.0],
                    "min": [0.0, 0.0, 0.0]
                },
                {
                    "bufferView": 1,
                    "byteOffset": 48,
                    "componentType": 5126,
                    "count": 4,
                    "type": "VEC2",
                    "max": [1.0, 1.0],
                    "min": [0.0, 0.0]
                }
            ]
        }
        
        # Füge Texturen in richtiger Reihenfolge hinzu (wie C# Reference)
        image_index = 0
        texture_index = 0
        
        # 1. Normal Map (Index 0)
        if 'normal' in textures:
            gltf['images'].append({
                "mimeType": "image/png",
                "name": f"{material_name}_normal",
                "uri": textures['normal']
            })
            gltf['textures'].append({"source": image_index})
            gltf['materials'][0]['normalTexture'] = {"index": texture_index}
            image_index += 1
            texture_index += 1
        
        # 2. Base Color / Albedo (Index 1)
        if 'baseColor' in textures:
            gltf['images'].append({
                "mimeType": "image/png",
                "name": f"{material_name}_baseColor",
                "uri": textures['baseColor']
            })
            gltf['textures'].append({"source": image_index})
            gltf['materials'][0]['pbrMetallicRoughness']['baseColorTexture'] = {"index": texture_index}
            image_index += 1
            texture_index += 1
        
        # 3. ORM Map (Index 2) - WICHTIG: Wird für metallicRoughness UND occlusion verwendet
        if 'orm' in textures:
            gltf['images'].append({
                "mimeType": "image/png",
                "name": f"{material_name}_orm",
                "uri": textures['orm']
            })
            gltf['textures'].append({"source": image_index})
            
            # ORM Format: R=Occlusion, G=Roughness, B=Metallic
            # MetallicRoughness nutzt G+B Kanäle
            gltf['materials'][0]['pbrMetallicRoughness']['metallicRoughnessTexture'] = {"index": texture_index}
            # Occlusion nutzt R Kanal
            gltf['materials'][0]['occlusionTexture'] = {"index": texture_index}
            image_index += 1
            texture_index += 1
        
        # 4. Emission Map (optional)
        if 'emission' in textures:
            gltf['images'].append({
                "mimeType": "image/png",
                "name": f"{material_name}_emission",
                "uri": textures['emission']
            })
            gltf['textures'].append({"source": image_index})
            gltf['materials'][0]['emissiveTexture'] = {"index": texture_index}
            
            # Emission Strength
            strength = self.gltf_emission_strength.get()
            gltf['materials'][0]['emissiveFactor'] = [strength, strength, strength]
        
        return gltf

def main():
    root = tk.Tk()
    ORMGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
