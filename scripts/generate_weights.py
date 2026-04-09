import json
import os
import pandas as pd
import unicodedata

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "data")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "data", "station_weights.csv")

def normalize(text):
    if not text: return ""
    text = str(text).lower().strip()
    return "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def generate_weights():
    all_stations = []
    
    # Process each GeoJSON in the data folder
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith("_normalized.geojson"):
            continue
            
        transport_type = filename.split("_")[0] # e.g., "metro"
        file_path = os.path.join(DATA_DIR, filename)
        
        print(f"Buscando estaciones en: {filename}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            
            # Extract common properties across different formats
            name = props.get('NOMBRE') or props.get('nombre') or props.get('Name') or props.get('STATION') or props.get('INSTERSECC') or props.get('label')
            line = props.get('LINEA') or props.get('linea') or props.get('Line') or props.get('RUTA') or "1"
            tipo = props.get('TIPO') or props.get('tipo') or ""
            
            if not name: continue
            
            # WEIGHTING LOGIC (Inspired by AutoAI/Granite)
            weight = 1.0 # Base
            
            # 1. Transport Type Multiphase
            if transport_type == "metro": weight *= 1.2
            elif transport_type == "metrobus": weight *= 1.0
            elif transport_type == "cablebus": weight *= 0.6 # Lower capacity
            
            # 2. Network Hub identification
            is_hub = False
            if tipo.lower() in ['terminal', 'correspondencia', 'transbordo', 'hub']:
                weight *= 1.8
                is_hub = True
            
            # 3. Known high-traffic hubs (Manual boost if data is missing 'tipo')
            high_traffic = ['pantitlan', 'hidalgo', 'tacubaya', 'pino suarez', 'bellas artes', 'balderas', 'constitucion de 1917']
            if normalize(name) in high_traffic:
                weight *= 1.5
                is_hub = True
                
            all_stations.append({
                "transport": transport_type,
                "name": name,
                "line": line,
                "weight": round(weight, 2),
                "is_hub": is_hub,
                "base_occupancy": 0.2 # Standard baseline
            })
            
    # Create DataFrame and save
    df = pd.DataFrame(all_stations)
    # Deduplicate in case of overlaps
    df = df.drop_duplicates(subset=['transport', 'name'])
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Escaneo completado. Se generaron {len(df)} perfiles de estaciones en {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_weights()
