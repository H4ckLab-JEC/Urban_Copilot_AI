import random
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ── Color palettes ────────────────────────────────────────────────────────────
TRANSPORT_COLORS = {
    "Metrobús":   "#DA291C",
    "Cablebús":   "#0EA5E9",
    "Tren Ligero":"#2563EB",
    "RTP":        "#22C55E",
    "walk":       "#94A3B8",
    "destination":"#10B981",
}
METRO_COLORS = {
    "Línea 1":"#F54A91", "Línea 2":"#0055A5", "Línea 3":"#B0A32A",
    "Línea 4":"#68BCA2", "Línea 5":"#FBD100", "Línea 6":"#DA291C",
    "Línea 7":"#E36B2C", "Línea 8":"#00A94F", "Línea 9":"#56382D",
    "Línea A":"#8D2587", "Línea B":"#007460", "Línea 12":"#B69E52",
}
METROBUS_COLORS = {
    "Línea 1":"#B72025", "Línea 2":"#862B88", "Línea 3":"#75BF2A",
    "Línea 4":"#E17719", "Línea 5":"#00366D", "Línea 6":"#CA2973",
    "Línea 7":"#008149",
}

TRANSBORDOS = [
    ("Metrobús",   "Línea 1", "estación Insurgentes"),
    ("Metro",      "Línea 3", "estación Centro Médico"),
    ("Cablebús",   "Línea 2", "estación Quetzalcóatl"),
    ("RTP",        "Ruta 34-A","paradero Santa Fe"),
    ("Metro",      "Línea 2", "estación Chabacano"),
    ("Tren Ligero","Línea 1", "estación Xochimilco"),
    ("Metrobús",   "Línea 5", "estación San Lázaro"),
]

def _get_color(t_tipo: str, t_linea: str) -> str:
    if t_tipo == "Metro":
        return METRO_COLORS.get(t_linea, "#64748B")
    if t_tipo == "Metrobús":
        return METROBUS_COLORS.get(t_linea, "#64748B")
    return TRANSPORT_COLORS.get(t_tipo, "#64748B")

# ── Watsonx client (optional, lazy-loaded) ────────────────────────────────────
def _build_watsonx_client():
    """Returns a ModelInference client if credentials are present, else None."""
    try:
        from ibm_watsonx_ai import APIClient, Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        api_key    = os.getenv("WATSONX_API_KEY", "").strip().strip('"')
        project_id = os.getenv("WATSONX_PROJECT_ID", "").strip().strip('"')
        url        = os.getenv("WATSONX_URL", "").strip().strip('"')

        if not api_key or not project_id or not url:
            logger.info("Watsonx credentials not fully set – using smart mock.")
            return None

        creds  = Credentials(api_key=api_key, url=url)
        client = APIClient(credentials=creds, project_id=project_id)

        # Usamos Mistral Small (disponible en plan Lite, bilingüe y rápido)
        model  = ModelInference(
            model_id="mistralai/mistral-small-3-1-24b-instruct-2503",
            api_client=client,
            project_id=project_id,
            params={"max_new_tokens": 900, "temperature": 0.2}
        )
        logger.info("✅ Watsonx ModelInference client ready (Mistral Small 3.1).")
        return model
    except Exception as e:
        logger.warning(f"Watsonx setup error – falling back to mock. {e}")
        return None

_watsonx_model = None   # Will be set on first call

# ── Prompt & parser ───────────────────────────────────────────────────────────
def _build_prompt(origin: str, destination: str) -> str:
    import datetime
    now_str = datetime.datetime.now().strftime("%H:%M")
    return f"""[INST] Eres un experto en la red de transporte público de Ciudad de México (CDMX).
Tu única tarea es calcular la ruta ÓPTIMA de transporte público entre dos puntos.

════════════════════════════════════════════════
 TOPOLOGÍA COMPLETA DE LA RED METRO CDMX
════════════════════════════════════════════════
L1(Rosa)  Observatorio→Pantitlán  | 20 estaciones
L2(Azul)  Cuatro Caminos→Tasqueña | 24 estaciones
L3(Amarilla) Indios Verdes→Universidad | 21 estaciones
L4(Cian)  Martín Carrera→Santa Anita | 10 estaciones
L5(Lima)  Politécnico→Pantitlán | 11 estaciones
L6(Roja)  El Rosario→Martín Carrera | 11 estaciones
L7(Naranja) El Rosario→Barranca del Muerto | 14 estaciones
L8(Verde) Garibaldi→Constitución 1917 | 19 estaciones
L9(Café)  Tacubaya→Pantitlán | 12 estaciones
L12(Oro)  Mixcoac→Tláhuac | 20 estaciones
LA(Morada) Pantitlán→La Paz | 10 estaciones
LB(Teal)  Buenavista→Ciudad Azteca | 21 estaciones

════════════════════════════════════════════════
 TABLA COMPLETA DE TRANSBORDOS (ESTACIONES EXACTAS)
════════════════════════════════════════════════
Para ir de L1↔L2: transbordo en Pino Suárez
Para ir de L1↔L3: transbordo en Balderas o en Cuauhtémoc
Para ir de L1↔L4: transbordo en Martín Carrera (vía L6) o en Santa Anita (vía L9 en Jamaica)
Para ir de L1↔L5: transbordo en Pantitlán
Para ir de L1↔L7: transbordo en Tacubaya
Para ir de L1↔L9: transbordo en Tacubaya o en Pantitlán
Para ir de L1↔LA: transbordo en Pantitlán
Para ir de L1↔LB: transbordo en Guerrero (L3 como puente) o Buenavista
Para ir de L2↔L3: transbordo en Hidalgo
Para ir de L2↔L5: transbordo en Eduardo Molina (Consulado→Misterios) — usar L4↔L6↔L5
Para ir de L2↔L7: transbordo en Tacubaya (vía L1) → Pino Suárez→Tacubaya
Para ir de L2↔L9: transbordo en Tacubaya (vía L1, baja en Pino Suárez sube L9 en Tacubaya)
Para ir de L3↔L7: transbordo en Balderas→Tacubaya (L1 puente) O directo: Mixcoac→Barranca (L12 a L7)
Para ir de L3↔L9: transbordo en Balderas→Tacubaya (L1 puente)
Para ir de L3↔L12: transbordo en Mixcoac (L7→L12) vía Barranca del Muerto
Para ir de L4↔L6: transbordo en Consulado o en Martín Carrera
Para ir de L4↔L9: transbordo en Jamaica
Para ir de L5↔L9: transbordo en Pantitlán o en Pantitlán
Para ir de L6↔L7: transbordo en El Rosario
Para ir de L7↔L9: transbordo en Tacubaya
Para ir de L7↔L12: transbordo en Mixcoac
Para ir de L8↔LB: transbordo en Garibaldi
Para ir de L9↔LA: transbordo en Pantitlán
Para ir de L9↔L12: transbordo en Mixcoac (vía L7)

METROBÚS (BRT) — usar cuando acorte distancia significativamente:
MB1(Rojo) Buenavista→Dr. Gálvez — conecta col. Roma/Condesa/Doctores
MB2(Morado) UNAM→Tepalcapa — conecta sur con norte por Insurgentes
MB3(Verde) Tenayuca→Etiopía — norte-centro
MB4(Naranja) El Rosario→Buenavista — poniente-norte
MB6(Guinda) Martín Carrera→Observatorio — cruza toda la ciudad

════════════════════════════════════════════════
 ALGORITMO OBLIGATORIO (SÍGUELO EXACTAMENTE)
════════════════════════════════════════════════
PASO 1: Identifica la LÍNEA del origen y la LÍNEA del destino.
PASO 2: ¿Son la MISMA línea? → SÍ: genera 1 solo step directo. FIN. NO AÑADIR TRANSBORDOS.
PASO 3: Si son diferentes → busca en la TABLA DE TRANSBORDOS la estación de transbordo entre esas dos líneas.
PASO 4: Elige el transbordo que esté GEOGRÁFICAMENTE MÁS CERCA al origen (menos estaciones desde el origen hasta el transbordo).
PASO 5: Genera los steps: [step en línea origen hasta transbordo] + [step en línea destino desde transbordo hasta destino]
PASO 6: Si no existe transbordo directo entre las dos líneas, usa una línea puente pero MÍNIMO pasos posibles.

REGLAS DURAS:
✗ NUNCA añadir transbordo si origen y destino están en la MISMA línea
✗ NUNCA elegir un transbordo que esté lejos del origen cuando hay uno más cercano
✗ NUNCA generar más de 2 transbordos
✗ NUNCA inventar estaciones que no existen
✓ SIEMPRE elegir el camino con menos estaciones totales recorridas
✓ El trasbordo debe ser en la misma estación física (el usuario no camina entre estaciones distintas)

TAREA ACTUAL: Ruta de "{origin}" → "{destination}" (hora: {now_str})
Tiempo estimado: 2 min/estación + 3 min/transbordo + 5 min caminata inicio/fin

RESPONDE ÚNICAMENTE con este JSON (sin texto antes ni después):
tiempo_estimado_minutos: entero
steps: lista de objetos con: tipo, linea, estacion (abordaje), estacion_bajada, num_estaciones, direccion (hacia qué terminal), instruccion (clara y útil)

[/INST]
{{"""

def _parse_watsonx(raw: str, origin: str, destination: str) -> list:
    """Try to extract steps from the LLM JSON response."""
    import json, re

    # El prompt termina con '{' así que el modelo completa desde ahí
    raw_full = "{" + raw if not raw.strip().startswith("{") else raw

    data = None

    # Estrategia 1: JSON completo
    for pattern in [
        r'```(?:json)?\s*(\{.*?\})\s*```',
        r'(\{.*\})',
    ]:
        match = re.search(pattern, raw_full, re.DOTALL)
        if match:
            candidate = match.group(1) if match.lastindex else match.group()
            try:
                data = json.loads(candidate)
                if "steps" in data:
                    break
                data = None
            except json.JSONDecodeError:
                pass

    # Estrategia 2: JSON truncado — extraer el array steps directamente
    if data is None:
        steps_match = re.search(r'"steps"\s*:\s*(\[.*)', raw_full, re.DOTALL)
        time_match  = re.search(r'"tiempo_estimado_minutos"\s*:\s*(\d+)', raw_full)
        if steps_match:
            # Intentar parsear el array aunque esté incompleto
            arr_raw = steps_match.group(1)
            # Extraer objetos individuales bien formados del array
            objs = re.findall(r'\{[^{}]+\}', arr_raw)
            if objs:
                parsed_objs = []
                for obj in objs:
                    try:
                        parsed_objs.append(json.loads(obj))
                    except json.JSONDecodeError:
                        pass
                if parsed_objs:
                    data = {
                        "steps": parsed_objs,
                        "tiempo_estimado_minutos": int(time_match.group(1)) if time_match else None
                    }

    if data is None:
        raise ValueError(f"No valid JSON found in LLM response: {raw[:200]}")

    llm_time = data.get("tiempo_estimado_minutos")  # nuevo campo del prompt
    steps_raw = data.get("steps", [])
    steps = [{
        "type": "walk",
        "instruction": f"Camina hacia la estación sugerida cerca de <strong>{origin}</strong>.",
        "color": TRANSPORT_COLORS["walk"],
        "location_name": origin,
        "transport_id": None,
        "line_number": None,
    }]
    transport_id_map = {
        "Metro": "metro", "Metrobús": "metrobus", "Cablebús": "cablebus",
        "Tren Ligero": "tren_ligero", "RTP": "rtp", "Trolebús": "trolebus",
        "Caminata": None,
    }
    for s in steps_raw:
        t_tipo_raw     = s.get("tipo", "Metro")
        # Normalizar tipo: 'metro' → 'Metro', 'transbordo' → skip
        t_tipo_lower   = t_tipo_raw.lower()
        if t_tipo_lower == "transbordo":
            continue  # Los transbordos son implícitos entre steps consecutivos
        tipo_map = {"metro": "Metro", "metrobus": "Metrobús", "metrobús": "Metrobús",
                    "cablebus": "Cablebús", "cablebús": "Cablebús",
                    "tren_ligero": "Tren Ligero", "tren ligero": "Tren Ligero",
                    "rtp": "RTP", "trolebus": "Trolebús", "trolebús": "Trolebús", "caminata": "Caminata"}
        t_tipo         = tipo_map.get(t_tipo_lower, t_tipo_raw.capitalize())
        t_linea        = s.get("linea", "Línea 1")
        estacion       = s.get("estacion", "")
        estacion_bajada= s.get("estacion_bajada", "")
        num_est        = s.get("num_estaciones", "")
        direccion      = s.get("direccion", "")
        color          = _get_color(t_tipo, t_linea)
        # Normalizar número de línea: 'L7' → '7', 'Línea 7' → '7', '7' → '7'
        raw_num = re.sub(r'(?i)^(l[íi]nea\s*|linea\s*|l)', '', t_linea).strip()
        # Construir instrucción enriquecida si el LLM no la dio
        instruccion = s.get("instruccion") or (
            f"Aborda {t_tipo} {t_linea} en <strong>{estacion}</strong>"
            + (f" dirección {direccion}" if direccion else "")
            + (f". Baja en <strong>{estacion_bajada}</strong>" if estacion_bajada else "")
            + (f" ({num_est} estaciones)" if num_est else ".")
        )
        loc_name = f"{t_tipo} {estacion}" + (f" → {estacion_bajada}" if estacion_bajada else "")
        steps.append({
            "type": "transfer",
            "instruction": instruccion,
            "color": color,
            "location_name": loc_name,
            "transport_id": transport_id_map.get(t_tipo, "metro"),
            "line_number": raw_num,
            "station_from": estacion,
            "station_to": estacion_bajada,
        })
    steps.append({
        "type": "walk",
        "instruction": f"Llega a tu destino: <strong>{destination}</strong>.",
        "color": TRANSPORT_COLORS["destination"],
        "location_name": destination,
        "transport_id": None,
        "line_number": None,
    })
    return steps, llm_time

def _mock_steps(origin: str, destination: str) -> list:
    """Fallback matemático que usa la red de Metro real."""
    from app.services.metro_graph import MetroRouter
    router = MetroRouter()
    
    calc = router.route(origin, destination)
    
    steps = [{
        "type": "walk",
        "instruction": f"Camina hacia la estación sugerida cerca de <strong>{origin}</strong>.",
        "color": TRANSPORT_COLORS["walk"],
        "location_name": origin,
        "transport_id": None,
        "line_number": None,
    }]
    
    if calc:
        for stage in calc:
            t_linea = stage['linea']
            origen = stage['origen']
            dest = stage['destino']
            color = _get_color("Metro", t_linea)
            raw_num = t_linea.replace("Línea ", "").strip()
            
            steps.append({
                "type": "transfer",
                "instruction": f"Aborda la {t_linea} en dirección sugerida. Transbordo o bajada en {dest}.",
                "color": color,
                "location_name": f"Metro {t_linea}: {origen} → {dest}",
                "transport_id": "metro",
                "line_number": raw_num,
                "station_from": origen,
                "station_to": dest,
            })
    else:
        # Fallback ultra genérico si las ubicaciones no son de metro
        steps.append({
            "type": "transfer",
            "instruction": f"El algoritmo no encontró una conexión directa de Metro entre {origin} y {destination}. Te sugerimos tomar transporte de superficie.",
            "color": TRANSPORT_COLORS["Metrobús"],
            "location_name": "Ruta de Superficie",
            "transport_id": "metrobus",
            "line_number": None,
            "station_from": origin,
            "station_to": destination,
        })
        
    steps.append({
        "type": "walk",
        "instruction": f"Llega a tu destino final: <strong>{destination}</strong>.",
        "color": TRANSPORT_COLORS["destination"],
        "location_name": destination,
        "transport_id": None,
        "line_number": None,
    })
    
    return steps

# ── Main service ──────────────────────────────────────────────────────────────
async def generate_route_recommendation(origin: str, destination: str) -> dict:
    global _watsonx_model
    if _watsonx_model is None:
        _watsonx_model = _build_watsonx_client()

    base_minutes = random.randint(15, 60) + (len(origin) + len(destination)) // 2
    now          = datetime.now()
    arrival      = now + timedelta(minutes=base_minutes)
    fmt          = "%I:%M %p"

    llm_time = None
    steps    = None

    if _watsonx_model:
        try:
            prompt   = _build_prompt(origin, destination)
            response = _watsonx_model.generate_text(prompt=prompt)
            steps, llm_time = _parse_watsonx(response, origin, destination)
            logger.info("✅ Route generated via Watsonx LLM.")
        except Exception as e:
            logger.warning(f"Watsonx call failed – using mock. {e}")
            steps = None

    if steps is None:
        steps = _mock_steps(origin, destination)

    # Usar tiempo real del LLM si está disponible, sino calcular
    travel_minutes = llm_time if llm_time else base_minutes
    arrival = now + timedelta(minutes=travel_minutes)

    return {
        "travel_time_minutes": travel_minutes,
        "departure_time":      now.strftime(fmt),
        "arrival_time":        arrival.strftime(fmt),
        "steps":               steps,
    }
