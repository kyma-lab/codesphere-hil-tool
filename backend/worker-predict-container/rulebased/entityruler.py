import spacy
import helper
from additional_modules import match_bedingung

########################################
# Demo for using the EntityRuler
########################################


def match_aktion(doc, epatterns):
    for i, token in enumerate(doc):
        if token.lemma_[-3:] == 'ung':
            epatterns.append({"label": "Aktion",
                              "pattern": [{"TEXT": token.text}]})
        elif token.tag_ == "VVIZU":
            epatterns.append({"label": "Aktion",
                              "pattern": [{"TEXT": token.text}]})
    return epatterns


nlp = spacy.load("de_core_news_sm")
# filecont = helper.read_file(
#     "/home/cunger/Documents/Canareno/testingnorm_a5.txt")
filecont = helper.read_file(
    "/Users/cunger1/Documents/firstday/after_ner/1002.txt.conll")

config = {
    "validate": True,
    "overwrite_ents": True
    }

ruler = nlp.add_pipe("entity_ruler", config=config, before="ner")

# We must start with some initial patterns
patterns = [{"label": "Signalwort", "pattern": [{"LEMMA": "sollen"}]},
            {"label": "Aktion",
             "pattern": [{"TEXT": "Vermeidung"}],
             "id": "Aktion"},
            {"label": "Aktion",
             "pattern": [{"MORPH": "VVIZU"}],
             "id": "Aktion"}]

ruler.add_patterns(patterns)

doc = nlp(filecont)

# Only now can we add more patterns, e.g. extracted from doc
# morepatterns = match_aktion(doc, [])
morepatterns = match_bedingung(doc, [])
ruler.add_patterns(morepatterns)

# And now we MUST create doc again
doc = nlp(filecont)
print([(ent.text, ent.label_) for ent in doc.ents])
