# bot/graph_builder.py
import spacy

def extract_triples(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    triples = []

    for sent in doc.sents:
        subj = ""
        obj = ""
        relation = ""
        for token in sent:
            if "subj" in token.dep_:
                subj = token.text
            if "obj" in token.dep_ or token.dep_ == "pobj":
                obj = token.text
            if token.pos_ == "VERB":
                relation = token.lemma_
        if subj and relation and obj:
            triples.append((subj, relation, obj))
    return triples
