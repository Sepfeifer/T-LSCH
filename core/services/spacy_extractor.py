import re
import spacy
from spacy.matcher import PhraseMatcher

_nlp = spacy.load("es_core_news_sm")

_MULTI_WORDS = [
    # existentes
    "por favor",
    "dedo índice",
    "acta de nacimiento",
    "carnet",
    "rut",
    "$3500",
    "3500",
    # nuevas dos-palabras (espacio)
    "Registro civil",
    "Firmar aqui",
    "Cuatro Semanas",
    "Bloquear Carnet",
    "Entrar a internet",
    # nuevas unidas por "_"
    "Poner_Huella",
    "Entregar documento",
    "Dos Semanas",
    "Documento de defunción",
    "Acta de nacimiento",
    "acta de nacimiento donde",
    "Una Semana",
    "Cómo estas",
    # nuevas variantes monetarias
    "3.500",
    "3,500",
]

_matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
_patterns = [_nlp.make_doc(text) for text in _MULTI_WORDS]
_matcher.add("COMPOUND", _patterns)

SALUDOS = {"hola"}
VERBOS_DUDOSOS = {"ser", "estar", "haber", "tener", "hacer", "poder", "esperar", "decir"}
INTERROGATIVOS = {"qué", "quién", "quienes", "cual", "cuales", "como", "cuando", "donde", "por qué", "cuanto", "cuantos"}
NUMEROS_PALABRAS = {
    "0": "cero", "1": "uno", "2": "dos", "3": "tres", "4": "cuatro",
    "5": "cinco", "6": "seis", "7": "siete", "8": "ocho", "9": "nueve"
}


def es_verbo_relevante(tok):
    """Permite verbos dudosos solo si tienen sujeto o complemento."""
    if tok.lemma_ not in VERBOS_DUDOSOS:
        return True
    hijos = [h.dep_ for h in tok.children]
    return "obj" in hijos or "nsubj" in hijos


def extract_keywords_spacy(text: str) -> list[str]:
    """
    Extrae términos clave en orden desde el texto:
      1) Deletreos entre comillas.
      2) Compuestos (palabras múltiples).
      3) Interrogativos y saludos.
      4) Sustantivos, verbos relevantes e interjecciones.
      5) Dígitos o números escritos.
    """
    seen = set()
    result = []

    # 1) Deletreos entre comillas
    for m in re.finditer(r'"([^\"]+)"', text):
        name = m.group(1)
        start = m.start()
        spelled = "-".join(name.replace(" ", "").upper())
        if spelled not in seen:
            seen.add(spelled)
            result.append((start, spelled))

    # 2) Texto sin comillas, limpio de signos solo al final de palabras
    cleaned = re.sub(r'"[^\"]+"', " ", text)
    cleaned = re.sub(r'[^\w\s$]', '', cleaned)  # quita signos pero conserva "$" y espacios
    doc = _nlp(cleaned)

    # 3) Detectar compuestos
    matches = [(s, e, doc[s:e].text.lower()) for _, s, e in _matcher(doc)]
    comp_index = {}
    for s, e, text_m in matches:
        idx = doc[s].idx
        if text_m not in seen:
            seen.add(text_m)
            result.append((idx, text_m.replace(" ", "_")))
            comp_index.update({i: True for i in range(s, e)})

    # 4) Resto del análisis
    for i, tok in enumerate(doc):
        if i in comp_index:
            continue  # ya se incluyó como parte de una expresión compuesta

        txt = tok.text.lower().strip("¿?")

        if txt in INTERROGATIVOS or txt in SALUDOS:
            if txt not in seen:
                seen.add(txt)
                result.append((tok.idx, txt))

        elif tok.pos_ == "INTJ" and txt not in seen:
            seen.add(txt)
            result.append((tok.idx, txt))

        elif tok.pos_ == "NOUN":
            lemma = tok.lemma_.lower()
            if lemma not in seen and len(lemma) > 2:
                seen.add(lemma)
                result.append((tok.idx, lemma))

        elif tok.pos_ == "VERB":
            lemma = tok.lemma_.lower()
            if lemma not in seen and len(lemma) > 2 and es_verbo_relevante(tok):
                seen.add(lemma)
                result.append((tok.idx, lemma))

    # 5) Dígitos como palabras
    for m in re.finditer(r'\d+', text):
        inicio = m.start()
        for d in m.group():
            palabra = NUMEROS_PALABRAS.get(d)
            if palabra and palabra not in seen:
                seen.add(palabra)
                result.append((inicio, palabra))

    # 6) Números escritos como texto
    for tok in doc:
        palabra = tok.text.lower()
        if palabra in NUMEROS_PALABRAS.values() and palabra not in seen:
            seen.add(palabra)
            result.append((tok.idx, palabra))

    # 7) Orden final limpio por posición real
    final = [texto for _, texto in sorted(result, key=lambda x: x[0])]
    return final