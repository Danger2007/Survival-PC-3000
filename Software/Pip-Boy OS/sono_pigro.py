import os
import shutil

# Percorso principale della cartella delle immagini da ripulire
TARGET_DIR = "./images"  # Lo script cercherà la cartella "images" di fianco a lui

# Percorsi dei due placeholder
PLACEHOLDER_PNG = "./Placeholder.png"
PLACEHOLDER_SVG = "./Placeholder.svg"

# Estensioni delle immagini da rimpiazzare e le altre da includere
# AGGIUNTO .webp ALLA LISTA DEI FORMATI RASTER
PNG_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp")
SVG_EXTENSIONS = (".svg",)
PSD_EXTENSIONS = (".psd",) 

# Controllo iniziale della presenza dei placeholder
if not os.path.exists(PLACEHOLDER_PNG) or not os.path.exists(PLACEHOLDER_SVG):
    print("Errore: Assicurati che Placeholder.png e Placeholder.svg siano in questa stessa cartella!")
    exit()

print("Inizio la sostituzione automatica ricorsiva (inclusi i file .webp)...")
conteggio_png = 0
conteggio_svg = 0
conteggio_psd = 0

# Esplorazione ricorsiva di tutte le cartelle
for root, dirs, files in os.walk(TARGET_DIR):
    for file in files:
        file_path = os.path.join(root, file)
        file_lower = file.lower()
        
        try:
            # Se è un formato raster (PNG, JPG, WEBP, ecc.), usa il placeholder PNG
            if file_lower.endswith(PNG_EXTENSIONS):
                shutil.copy(PLACEHOLDER_PNG, file_path)
                conteggio_png += 1
                
            # Se è un formato vettoriale (SVG), usa il placeholder SVG
            elif file_lower.endswith(SVG_EXTENSIONS):
                shutil.copy(PLACEHOLDER_SVG, file_path)
                conteggio_svg += 1
                
            # Per i file .psd di Photoshop, li bonifichiamo riducendone il peso
            elif file_lower.endswith(PSD_EXTENSIONS):
                shutil.copy(PLACEHOLDER_PNG, file_path)
                conteggio_psd += 1
                
        except Exception as e:
            print(f"Impossibile sostituire il file {file}: {e}")

print("\n--- OPERAZIONE COMPLETATA ---")
print(f"File raster (PNG/JPG/WEBP) sostituiti: {conteggio_png}")
print(f"File SVG sostituiti: {conteggio_svg}")
print(f"File PSD pesanti bonificati: {conteggio_psd}")
print("Tutti i file multimediali sono pronti. Ora puoi procedere con il terminale!")