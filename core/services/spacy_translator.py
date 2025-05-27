# core/services/spacy_extractor.py

import re
import spacy
from spacy.matcher import PhraseMatcher

# Carga el modelo una sola vez
_nlp = spacy.load("es_core_news_sm")

# Lista de expresiones compuestas y nombres de documento
_MULTI_WORDS = [
    "por favor",
    "dedo índice",
    "acta de nacimiento",
    "carnet",
    "rut",
    # añade más si hace falta…
]

# Configura PhraseMatcher
_matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
_patterns = [_nlp.make_doc(text) for text in _MULTI_WORDS]
_matcher.add("COMPOUND", _patterns)


def extract_keywords_spacy(text: str) -> list[str]:
    """
    Extrae términos en el orden en que aparecen en el texto:
      1) Nombres entre "comillas" → deletreados.
      2) Expresiones compuestas definidas en _MULTI_WORDS.
      3) Verbos (VERB) en infinitivo.
      4) Sustantivos (NOUN).
    Sólo devuelve cada término una vez.
    """
    seen = set()
    result = []

    # 1) detectar nombres entre comillas con posición
    for m in re.finditer(r'"([^"]+)"', text):
        name = m.group(1)
        start = m.start()
        spelled = "-".join(name.replace(" ", "").upper())
        if spelled not in seen:
            seen.add(spelled)
            result.append((start, spelled))

    # Prepara el texto sin los fragmentos entre comillas
    cleaned = re.sub(r'"[^"]+"', " ", text)
    doc = _nlp(cleaned)

    # 2) detectar compuestos y anotar sus spans
    matches = [(start, end, doc[start:end].text.lower())
               for _, start, end in _matcher(doc)]
    # convierte índices de token a posición char para ordenar
    comp_spans = []
    for start, end, span_text in matches:
        char_start = doc[start].idx
        if span_text not in seen:
            seen.add(span_text)
            comp_spans.append((char_start, span_text, start, end))

    # 3) ahora recorre el doc token a token, en paralelo compuestos
    # ordenamos primero nombres entre comillas, luego compuestos, luego tokens
    # pero mejor: usamos puntero sobre tokens
    comp_index = {start: (end, text) for _, text, start, end in comp_spans}
    i = 0
    while i < len(doc):
        # si arranca un compuesto aquí
        if i in comp_index:
            end, span_text = comp_index[i]
            # posición char para el orden lineal
            char_pos = doc[i].idx
            result.append((char_pos, span_text))
            i = end  # saltamos la expresión completa
            continue

        tok = doc[i]
        if tok.pos_ in ("VERB", "NOUN"):
            lemma = tok.lemma_.lower()
            if lemma not in seen:
                seen.add(lemma)
                result.append((tok.idx, lemma))
        i += 1

    # 4) unimos todo y ordenamos por posición original
    ordered = [term for _, term in sorted(result, key=lambda x: x[0])]
    return ordered
