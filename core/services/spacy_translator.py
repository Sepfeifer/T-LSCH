"""
Este módulo se encarga de “traducir” un término en español (extraído por spaCy)
a la etiqueta/tag que corresponderá en la base de datos de LSCH (Lengua de Señas Chilena).

Si el término no está mapeado en 'mapeo_basico', devuelve el mismo término en minúsculas.
"""

def translate_to_lsch(term: str) -> str:
    # Mapeo de términos en español a su etiqueta en LSCH
    mapeo_basico = {
        "rut": "rut_signo",
        "carnet": "carnet_signo",
        "acta de nacimiento": "acta_nacimiento_signo",
        "por favor": "por_favor_signo",
        "dedo índice": "dedo_indice_signo",
        
        # <-- Añade aquí cada tag que tengas en la tabla Tema.nombre -->
    }

    # Normaliza a minúsculas y elimina espacios al inicio/fin
    term_lower = term.lower().strip()
    return mapeo_basico.get(term_lower, term_lower) 