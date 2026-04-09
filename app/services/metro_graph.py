class MetroRouter:
    def __init__(self):
        # Topología Simplificada de CDMX (Principales estaciones y transbordos)
        self.red = {
            "Línea 1": ["Observatorio", "Tacubaya", "Balderas", "Salto del Agua", "Pino Suárez", "Candelaria", "San Lázaro", "Gómez Farías", "Zaragoza", "Pantitlán"],
            "Línea 2": ["Cuatro Caminos", "Tacuba", "Hidalgo", "Bellas Artes", "Allende", "Zócalo", "Pino Suárez", "Chabacano", "Ermita", "Tasqueña"],
            "Línea 3": ["Indios Verdes", "Deportivo 18 de Marzo", "La Raza", "Guerrero", "Hidalgo", "Juárez", "Balderas", "Centro Médico", "Zapata", "Coyoacán", "Viveros", "Miguel Ángel de Quevedo", "Copilco", "Universidad"],
            "Línea 4": ["Martín Carrera", "Consulado", "Morelos", "Candelaria", "Jamaica", "Santa Anita"],
            "Línea 5": ["Politécnico", "Instituto del Petróleo", "La Raza", "Consulado", "Oceanía", "Pantitlán"],
            "Línea 6": ["El Rosario", "Instituto del Petróleo", "Deportivo 18 de Marzo", "Martín Carrera"],
            "Línea 7": ["El Rosario", "Tacuba", "Polanco", "Auditorio", "Constituyentes", "Tacubaya", "Mixcoac", "Barranca del Muerto"],
            "Línea 8": ["Garibaldi", "Bellas Artes", "Salto del Agua", "Chabacano", "Santa Anita", "Constitución de 1917"],
            "Línea 9": ["Tacubaya", "Centro Médico", "Chabacano", "Jamaica", "Ciudad Deportiva", "Puebla", "Pantitlán"],
            "Línea 12": ["Mixcoac", "Zapata", "Ermita", "Atlalilco", "Tláhuac"],
            "Línea A": ["Pantitlán", "Santa Marta", "Los Reyes", "La Paz"],
            "Línea B": ["Buenavista", "Guerrero", "Garibaldi", "Morelos", "San Lázaro", "Oceanía", "Ciudad Azteca"]
        }

        # Matriz de Conexiones (Línea A, Línea B) -> Estación de Transbordo
        self.transbordos = {
            ("Línea 1", "Línea 2"): "Pino Suárez",
            ("Línea 1", "Línea 3"): "Balderas",
            ("Línea 1", "Línea 7"): "Tacubaya",
            ("Línea 1", "Línea 9"): "Tacubaya",
            ("Línea 1", "Línea B"): "San Lázaro",
            ("Línea 2", "Línea 3"): "Hidalgo",
            ("Línea 2", "Línea 7"): "Tacuba",
            ("Línea 2", "Línea 8"): "Chabacano",
            ("Línea 2", "Línea 9"): "Chabacano",
            ("Línea 2", "Línea 12"): "Ermita",
            ("Línea 3", "Línea 6"): "Deportivo 18 de Marzo",
            ("Línea 3", "Línea 9"): "Centro Médico",
            ("Línea 3", "Línea 12"): "Zapata",
            ("Línea 4", "Línea B"): "Morelos",
            ("Línea 7", "Línea 9"): "Tacubaya",
            ("Línea 7", "Línea 12"): "Mixcoac",
            ("Línea 8", "Línea 9"): "Chabacano",
            ("Línea 8", "Línea B"): "Garibaldi",
            ("Línea 9", "Línea 12"): "Ermita",
            ("Línea 1", "Línea A"): "Pantitlán",
            ("Línea 5", "Línea 9"): "Pantitlán",
            ("Línea 1", "Línea 5"): "Pantitlán",
        }

    def infer_line(self, query: str):
        query = query.lower()
        for linea, estaciones in self.red.items():
            for est in estaciones:
                if est.lower() in query or query in est.lower():
                    return linea, est
        return None, None

    def route(self, origen_text: str, destino_text: str):
        linea_origen, est_origen = self.infer_line(origen_text)
        linea_destino, est_destino = self.infer_line(destino_text)

        if not linea_origen or not linea_destino:
            # Fallback a heurística conversacional si no conocemos la estación
            return None

        if linea_origen == linea_destino:
            return [{
                "linea": linea_origen,
                "origen": est_origen,
                "destino": est_destino,
                "via": "Directo"
            }]

        # Buscar transbordo directo
        camino_directo = self.transbordos.get((linea_origen, linea_destino)) or self.transbordos.get((linea_destino, linea_origen))
        
        if camino_directo:
            return [
                {"linea": linea_origen, "origen": est_origen, "destino": camino_directo, "via": "Transbordo directo"},
                {"linea": linea_destino, "origen": camino_directo, "destino": est_destino, "via": "Llegada rápida"}
            ]

        # Transbordo Puente (2 saltos) - Búsqueda rápida
        for (l1, l2), est_trans1 in self.transbordos.items():
            if l1 == linea_origen or l2 == linea_origen:
                linea_intermedia = l2 if l1 == linea_origen else l1
                trans2 = self.transbordos.get((linea_intermedia, linea_destino)) or self.transbordos.get((linea_destino, linea_intermedia))
                if trans2:
                    return [
                        {"linea": linea_origen, "origen": est_origen, "destino": est_trans1, "via": "Inicio"},
                        {"linea": linea_intermedia, "origen": est_trans1, "destino": trans2, "via": "Transbordo intermedio"},
                        {"linea": linea_destino, "origen": trans2, "destino": est_destino, "via": "Tramo final"}
                    ]

        return None
