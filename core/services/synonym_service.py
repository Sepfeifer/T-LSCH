# core/services/synonym_service.py

import nltk
from nltk.corpus import wordnet as wn

# Asegúrate de haber ejecutado en alguna parte:
#    nltk.download("wordnet")
#    nltk.download("omw-1.4")
# para contar con el corpus de sinónimos en español.

def get_synonyms(word: str) -> list[str]:
    """
    Retorna una lista de sinónimos en español (lang='spa') para 'word'
    usando WordNet de NLTK. Si no hay sinónimos, devuelve lista vacía.
    """
    syns = set()
    for synset in wn.synsets(word, lang='spa'):
        for lemma in synset.lemmas(lang='spa'):
            name = lemma.name().replace("_", " ").lower()
            if name != word.lower():
                syns.add(name)
    return list(syns)