import re
import spacy
from spacy.matcher import PhraseMatcher

# Carga el modelo de spaCy (modelo español)
_nlp = spacy.load("es_core_news_sm")

# Lista de expresiones compuestas que quieres detectar como una sola unidad
_MULTI_WORDS = ["por favor", "dedo índice", "acta de nacimiento", "carnet", "rut"]

# Configura PhraseMatcher para capturar estos _MULTI_WORDS
_matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
_patterns = [_nlp.make_doc(text) for text in _MULTI_WORDS]
_matcher.add("COMPOUND", _patterns)


def extract_keywords_spacy(text: str) -> list[str]:
    """
    Extrae términos en el orden en que aparecen en el texto:
      1) Palabras entre "comillas" → deletreados (si existen).
      2) Expresiones compuestas definidas en _MULTI_WORDS.
      3) Verbos (VERB) y Sustantivos (NOUN) (en forma de lematizado).
    Sólo devuelve cada término una sola vez, manteniendo el orden original.
    Devuelve una lista de strings (keywords).
    """
    seen = set()
    result = []

    # 1) Detectar palabras entre comillas
    for m in re.finditer(r'"([^"]+)"', text):
        name = m.group(1)
        start = m.start()
        spelled = "-".join(name.replace(" ", "").upper())
        if spelled not in seen:
            seen.add(spelled)
            result.append((start, spelled))

    # 2) Remover fragmentos entre comillas para procesar con spaCy
    cleaned = re.sub(r'"[^"]+"', " ", text)
    doc = _nlp(cleaned)

    # 3) Detectar expresiones compuestas (_MULTI_WORDS) con PhraseMatcher
    matches = [
        (start, end, doc[start:end].text.lower())
        for _, start, end in _matcher(doc)
    ]
    comp_spans = []
    for start, end, span_text in matches:
        char_start = doc[start].idx
        if span_text not in seen:
            seen.add(span_text)
            comp_spans.append((char_start, span_text, start, end))

    # Crear un índice (token index → (end_index, texto)) para saltar compuestos
    comp_index = {start: (end, text) for _, text, start, end in comp_spans}

    # 4) Recorrer tokens, saltando compuestos y agregando VERB/NOUN lematizados
    i = 0
    while i < len(doc):
        if i in comp_index:
            end, span_text = comp_index[i]
            result.append((doc[i].idx, span_text))
            i = end
            continue

        tok = doc[i]
        if tok.pos_ in ("VERB", "NOUN"):
            lemma = tok.lemma_.lower()
            if lemma not in seen:
                seen.add(lemma)
                result.append((tok.idx, lemma))
        i += 1

    # 5) Ordenar por posición de ocurrencia (primer campo de cada tupla)
    ordered = [term for _, term in sorted(result, key=lambda x: x[0])]
    return ordered