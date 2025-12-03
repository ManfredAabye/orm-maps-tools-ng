import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import glob
import threading

class ORMGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenSim (O)RM Map Viewer")
        self.root.geometry("1200x900")
        
        # Variablen
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.progress = tk.DoubleVar()
        self.status = tk.StringVar(value="Bereit")
        self.current_texture_index = 0
        self.texture_list = []
        
        # Preview Images
        self.preview_images = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Root-Fenster Grid-Konfiguration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Titel
        title_label = ttk.Label(main_frame, text="OpenSim (O)RM Map Viewer", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Linke Seite: Steuerung
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Eingabe-Verzeichnis
        ttk.Label(control_frame, text="Eingabe-Verzeichnis:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(control_frame, textvariable=self.input_dir, width=40).grid(row=1, column=0, pady=5)
        ttk.Button(control_frame, text="Durchsuchen", command=self.browse_input_dir).grid(row=1, column=1, pady=5, padx=5)
        
        # Ausgabe-Verzeichnis
        ttk.Label(control_frame, text="Ausgabe-Verzeichnis:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(control_frame, textvariable=self.output_dir, width=40).grid(row=3, column=0, pady=5)
        ttk.Button(control_frame, text="Durchsuchen", command=self.browse_output_dir).grid(row=3, column=1, pady=5, padx=5)
        
        # Optionen
        options_frame = ttk.LabelFrame(control_frame, text="Optionen", padding="5")
        options_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        self.use_height_for_ao = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Height für AO verwenden", 
                       variable=self.use_height_for_ao).grid(row=0, column=0, sticky=tk.W)
        
        self.overwrite_existing = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Existierende überschreiben", 
                       variable=self.overwrite_existing).grid(row=1, column=0, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Texturen laden", command=self.load_textures).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ORM generieren", command=self.start_generation).pack(side=tk.LEFT, padx=5)
        
        # Fortschritt
        ttk.Label(control_frame, text="Fortschritt:").grid(row=6, column=0, sticky=tk.W, pady=(10, 0))
        progress_bar = ttk.Progressbar(control_frame, variable=self.progress, length=400)
        progress_bar.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Status
        status_label = ttk.Label(control_frame, textvariable=self.status)
        status_label.grid(row=8, column=0, columnspan=2, pady=5)
        
        # Log
        log_frame = ttk.LabelFrame(control_frame, text="Log", padding="5")
        log_frame.grid(row=9, column=0, columnspan=2, sticky="nsew", pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, width=50)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Rechte Seite: Vorschau
        preview_frame = ttk.LabelFrame(main_frame, text="Material Vorschau", padding="10")
        preview_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        
        # Navigation
        nav_frame = ttk.Frame(preview_frame)
        nav_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(nav_frame, text="◄ Zurück", command=self.prev_texture).pack(side=tk.LEFT, padx=5)
        self.texture_label = ttk.Label(nav_frame, text="Keine Texturen geladen")
        self.texture_label.pack(side=tk.LEFT, padx=20)
        ttk.Button(nav_frame, text="Vor ►", command=self.next_texture).pack(side=tk.LEFT, padx=5)
        
        # Zeile 1: Eingabe-Texturen
        ttk.Label(preview_frame, text="Ambient Occlusion", font=("Arial", 9, "bold")).grid(row=1, column=0, pady=5)
        self.ao_preview = ttk.Label(preview_frame, text="Keine Vorschau", relief="solid", width=25)
        self.ao_preview.grid(row=2, column=0, padx=5, pady=5)
        
        ttk.Label(preview_frame, text="Roughness", font=("Arial", 9, "bold")).grid(row=1, column=1, pady=5)
        self.roughness_preview = ttk.Label(preview_frame, text="Keine Vorschau", relief="solid", width=25)
        self.roughness_preview.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(preview_frame, text="Metallic", font=("Arial", 9, "bold")).grid(row=1, column=2, pady=5)
        self.metallic_preview = ttk.Label(preview_frame, text="Keine Vorschau", relief="solid", width=25)
        self.metallic_preview.grid(row=2, column=2, padx=5, pady=5)
        
        # Zeile 2: Ausgabe
        ttk.Label(preview_frame, text="ORM Map (kombiniert)", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=3, pady=(20, 5))
        self.orm_preview = ttk.Label(preview_frame, text="Noch nicht generiert", relief="solid", width=25)
        self.orm_preview.grid(row=4, column=0, columnspan=3, padx=5, pady=5)
        
        # Albedo Preview (optional)
        ttk.Label(preview_frame, text="Albedo/Base Color", font=("Arial", 9, "bold")).grid(row=5, column=0, columnspan=3, pady=(20, 5))
        self.albedo_preview = ttk.Label(preview_frame, text="Keine Vorschau", relief="solid", width=25)
        self.albedo_preview.grid(row=6, column=0, columnspan=3, padx=5, pady=5)
        
        # Grid-Konfiguration
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        control_frame.rowconfigure(9, weight=1)
    
    def browse_input_dir(self):
        directory = filedialog.askdirectory(title="Eingabe-Verzeichnis auswählen")
        if directory:
            self.input_dir.set(directory)
            if not self.output_dir.get():
                self.output_dir.set(os.path.join(directory, "ORM_Maps"))
    
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
        input_dir = self.input_dir.get()
        self.status.set("Suche Texturen...")
        self.log_text.delete(1.0, tk.END)
        
        # Alle Albedo-Texturen finden
        albedo_files = []
        albedo_suffixes = [
            "albedo", "Albedo", "base", "Base", "color", "Color", 
            "col", "Col", "diffuse", "Diffuse", "diff", "Diff"
        ]
        extensions = ["png", "jpg", "jpeg", "jp2"]
        
        for suffix in albedo_suffixes:
            for ext in extensions:
                for sep in ["_", "-"]:
                    pattern = f"*{sep}{suffix}.{ext}"
                    albedo_files.extend(glob.glob(os.path.join(input_dir, pattern)))
                    albedo_files.extend(glob.glob(os.path.join(input_dir, "**", pattern), recursive=True))
        
        albedo_files = list(set(albedo_files))
        
        if not albedo_files:
            self.log("Keine Texturen gefunden!")
            self.status.set("Fehler: Keine Texturen gefunden")
            return
        
        # Extrahiere Base-Namen
        self.texture_list = []
        for albedo_file in albedo_files:
            base_name = os.path.basename(albedo_file)
            for suffix in albedo_suffixes:
                for ext in extensions:
                    for sep in ["_", "-"]:
                        full_suffix = f"{sep}{suffix}.{ext}"
                        if base_name.endswith(full_suffix):
                            base_name = base_name[:-(len(full_suffix))]
                            self.texture_list.append({
                                'base_name': base_name,
                                'albedo_file': albedo_file,
                                'dir': os.path.dirname(albedo_file)
                            })
                            break
                    else:
                        continue
                    break
                else:
                    continue
                break
        
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
        
        # Finde Textur-Dateien
        ao_file = self.find_texture_file(texture_dir, base_name, ["ao", "AO", "ambient", "occlusion"])
        roughness_file = self.find_texture_file(texture_dir, base_name, ["roughness", "Roughness", "rough"])
        metallic_file = self.find_texture_file(texture_dir, base_name, ["metallic", "Metallic", "metal"])
        height_file = self.find_texture_file(texture_dir, base_name, ["height", "Height", "disp", "bump"])
        
        # Falls AO fehlt, Height verwenden
        if not ao_file and height_file and self.use_height_for_ao.get():
            ao_file = height_file
        
        # ORM Datei prüfen
        output_dir = self.output_dir.get() or os.path.join(texture_dir, "ORM_Maps")
        orm_file = os.path.join(output_dir, f"{base_name}_ORM.png")
        
        # Zeige Previews
        self.show_preview_image(ao_file, self.ao_preview, "AO fehlt")
        self.show_preview_image(roughness_file, self.roughness_preview, "Roughness fehlt")
        self.show_preview_image(metallic_file, self.metallic_preview, "Metallic fehlt")
        self.show_preview_image(texture_info['albedo_file'], self.albedo_preview, "Albedo fehlt")
        
        if os.path.exists(orm_file):
            self.show_preview_image(orm_file, self.orm_preview, "ORM Map")
        else:
            self.orm_preview.config(image='', text="Noch nicht generiert")
    
    def find_texture_file(self, directory, base_name, suffixes):
        extensions = ["png", "jpg", "jpeg", "jp2"]
        for suffix in suffixes:
            for sep in ['_', '-']:
                for ext in extensions:
                    path = os.path.join(directory, f"{base_name}{sep}{suffix}.{ext}")
                    if os.path.exists(path):
                        return path
        return None
    
    def show_preview_image(self, file_path, label_widget, fallback_text):
        if not file_path or not os.path.exists(file_path):
            label_widget.config(image='', text=fallback_text)
            return
        
        try:
            img = Image.open(file_path)
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Speichere Referenz
            label_widget.image = photo
            label_widget.config(image=photo, text='')
        except Exception as e:
            label_widget.config(image='', text=f"Fehler: {str(e)[:20]}")
    
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
    
    def generate_orm_maps(self):
        try:
            output_dir = self.output_dir.get()
            
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
                
                success = self.create_single_orm_map(texture_dir, output_dir, base_name)
                
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
    
    def create_single_orm_map(self, input_dir, output_dir, base_name):
        try:
            # Suffix-Definitionen
            ao_suffixes = ["ao", "AO", "ambient", "Ambient", "occlusion", "Occlusion"]
            roughness_suffixes = ["roughness", "Roughness", "rough", "Rough", "rgh"]
            metallic_suffixes = ["metallic", "Metallic", "metal", "Metal", "mtl"]
            height_suffixes = ["height", "Height", "disp", "displacement", "bump"]
            
            def find_texture_file(base, suffix_list):
                extensions = ["png", "jpg", "jpeg", "jp2"]
                for suffix in suffix_list:
                    for sep in ['_', '-']:
                        for ext in extensions:
                            path = os.path.join(input_dir, f"{base}{sep}{suffix}.{ext}")
                            if os.path.exists(path):
                                return path
                return None
            
            ao_file = find_texture_file(base_name, ao_suffixes)
            roughness_file = find_texture_file(base_name, roughness_suffixes)
            metallic_file = find_texture_file(base_name, metallic_suffixes)
            height_file = find_texture_file(base_name, height_suffixes)
            
            output_file = os.path.join(output_dir, f"{base_name}_ORM.png")
            
            if os.path.exists(output_file) and not self.overwrite_existing.get():
                self.log(f"Übersprungen: {base_name}")
                return True
            
            if self.use_height_for_ao.get() and not ao_file and height_file:
                ao_file = height_file
            
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
            
            assert ao_file and roughness_file and metallic_file
            ao_img = Image.open(ao_file).convert("L")
            roughness_img = Image.open(roughness_file).convert("L")
            metallic_img = Image.open(metallic_file).convert("L")
            
            sizes = [img.size for img in [ao_img, roughness_img, metallic_img]]
            target_size = max(sizes, key=lambda x: x[0] * x[1])
            
            if ao_img.size != target_size:
                ao_img = ao_img.resize(target_size, Image.Resampling.LANCZOS)
            if roughness_img.size != target_size:
                roughness_img = roughness_img.resize(target_size, Image.Resampling.LANCZOS)
            if metallic_img.size != target_size:
                metallic_img = metallic_img.resize(target_size, Image.Resampling.LANCZOS)
            
            orm_map = Image.merge("RGB", (ao_img, roughness_img, metallic_img))
            
            os.makedirs(output_dir, exist_ok=True)
            orm_map.save(output_file, "PNG")
            
            self.log(f"ERFOLG: {base_name}")
            return True
            
        except Exception as e:
            self.log(f"FEHLER {base_name}: {str(e)}")
            return False

def main():
    root = tk.Tk()
    ORMGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
