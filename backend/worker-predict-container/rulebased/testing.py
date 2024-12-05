import spacy
from spacy.tokens import Doc

config = {
    "validate": False,
    "overwrite_ents": True,
}

# nlp = spacy.blank("en")
nlp = spacy.load("de_core_news_sm", disable=["ner", "parser"])
ruler = nlp.add_pipe("entity_ruler", config=config, after="lemmatizer")
pat = [{"label": "Dokument",
        "pattern": [{"TEXT": "Der"},
                    {"TEXT": "Bescheid"}]}]
words = ['1', '.', 'Der', 'Bescheid', 'ist', 'zu', 'erteilen', '.']
doc = Doc(nlp.vocab, words=words)
ruler.add_patterns(pat)
# doc = nlp(doc)
doc = Doc(nlp.vocab, words=words)
print(doc.text)
print([(ent.text, ent.label_) for ent in doc.ents])

