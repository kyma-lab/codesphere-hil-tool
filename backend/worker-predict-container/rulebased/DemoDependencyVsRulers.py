"""Working on a one-file input for developing and testing rules"""
# import os
import spacy
from spacy.matcher import DependencyMatcher
from spacy.tokens import Span
from entities_for_norms import EntitiesForNorms


# The input text must be in a file
inputfile = "/home/cunger/Documents/Canareno/dummy.txt"

# Parameters which are the same for every EntitiesForNorm instantiation
# are read into variables which are then passed as parameters
# for the class instantiations in the loop below.
config = {
    "validate": False,
    "overwrite_ents": True,
}

# Disable SpaCy's own NER to replace it with our EntityRuler.
# Since we don't use dependency relations in the present setup,
# we disable the (dependency) parser as well. But this may change.
thenlp = spacy.load("de_core_news_sm", disable=["ner"])
theruler = thenlp.add_pipe("entity_ruler", config=config, after="lemmatizer")
# theruler = thenlp.add_pipe("span_ruler", after="lemmatizer")
getspat = [{"label": "Signalwort", "pattern": [{"LEMMA": "sollen"}]},
           {"label": "Aktion", "pattern": [{"TEXT": "Vermeidung"}]},
           # Pattern "Entsorgungsträger" fehlt tatsächlich. Hilfst es hier?
           # {"label": "Hauptakteur",
           #  "pattern": [{"TEXT": "Entsorgungsträger"}]},
           {"label": "Hauptakteur",
            "pattern": [{"TEXT": "öffentlich-rechtlichen"},
                        {"TAG": "NNE"}]},
           {"label": "Hauptakteur",
            "pattern": [{"TEXT": "öffentlich-rechtlichen"},
                        {"TAG": "NN"}]},
           {"label": "Hauptakteur",
            "pattern": [{"TEXT": "öffentlich-rechtlichen"},
                        {"TAG": "NE"}]},
           {"label": "Handlungsgrundlage",
            "pattern": [{"TEXT": "§"},
                        {"TEXT": "§"},
                        {"IS_DIGIT": True},
                        {"TEXT": "bis"},
                        {"IS_DIGIT": True}]},
           {"label": "Handlungsgrundlage",
            "pattern": [{"TEXT": "§"},
                        {"TEXT": "§"},
                        {"IS_DIGIT": True},
                        {"TEXT": "und"},
                        {"IS_DIGIT": True}]},
           {"label": "Handlungsgrundlage",
            "pattern": [{"TEXT": "§"},
                        {"TEXT": "§"},
                        {"IS_DIGIT": True},
                        {"TEXT": "bis"},
                        {"IS_DIGIT": True},
                        {"TEXT": "und"},
                        {"IS_DIGIT": True}]},
           {"label": "Aktion",
            "pattern": [{"TAG": "VVIZU"}]},
           {"label": "Aktion",
            "pattern": [{"TEXT": "zu"},
                        {"TAG": "VVINF"}]},
           # patterns for "Frist"
           {"label": "Frist",
            "pattern": [{"IS_DIGIT": True},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]
            },
           {"label": "Frist",
            "pattern": [{"TEXT": {"IN": ["einem", "einer", "ein",
                                         "zwei", "drei", "vier",
                                         "fünf", "sechs", "sieben",
                                         "acht", "neun", "zehn"]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]
            },
           # mindestens ... lang
           {"label": "Frist",
            "pattern": [{"TEXT": "mindestens"},
                        {"IS_DIGIT": True},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}},
                        {"TEXT": "lang"}]
            },
           {"label": "Frist",
            "pattern": [{"TEXT": "mindestens"},
                        {"TEXT": {"IN": ["ein", "eine",
                                         "zwei", "drei", "vier",
                                         "fünf", "sechs", "sieben",
                                         "acht", "neun", "zehn"]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}},
                        {"TEXT": "lang"}]
            },

           # innerhalb einer Frist von ...
           {"label": "Frist",
            "pattern": [{"LEMMA": "innerhalb"},
                        {"TEXT": "einer"},
                        {"LEMMA": "Frist"},
                        {"LEMMA": "von"},
                        {"IS_DIGIT": True},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]
            },
           {"label": "Frist",
            "pattern": [{"LEMMA": "innerhalb"},
                        {"TEXT": "einer"},
                        {"LEMMA": "Frist"},
                        {"LEMMA": "von"},
                        {"TEXT": {"IN": ["zwei", "drei", "vier",
                                         "fünf", "sechs", "sieben",
                                         "acht", "neun", "zehn"]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]
            },
           # bis zu ...
           {"label": "Frist",
            "pattern": [{"LEMMA": "bis"},
                        {"LEMMA": "zu"},
                        {"IS_DIGIT": True},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]
            },
           {"label": "Frist",
            "pattern": [{"LEMMA": "bis"},
                        {"LEMMA": "zu"},
                        {"TEXT": {"IN": ["zwei", "drei", "vier",
                                         "fünf", "sechs", "sieben",
                                         "acht", "neun", "zehn"]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]
            },

           # ... vor Aufnahme der Tätigkeit
           {"label": "Frist",
            "pattern": [{"IS_DIGIT": True},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}},
                        {"LEMMA": "vor"},
                        {"LEMMA": "Aufnahme"},
                        {"TEXT": "der"},
                        {"LEMMA": "Tätigkeit"}]
            },
           {"label": "Frist",
            "pattern": [{"TEXT": {"IN": ["zwei", "drei", "vier",
                                         "fünf", "sechs", "sieben",
                                         "acht", "neun", "zehn"]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}},
                        {"LEMMA": "vor"},
                        {"LEMMA": "Aufnahme"},
                        {"TEXT": "der"},
                        {"LEMMA": "Tätigkeit"}]
            },

           # nach ...
           {"label": "Frist",
            "pattern": [{"LEMMA": "nach"},
                        {"IS_DIGIT": True},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]
            },
           {"label": "Frist",
            "pattern": [{"LEMMA": "nach"},
                        {"TEXT": {"IN": ["zwei", "drei", "vier",
                                         "fünf", "sechs", "sieben",
                                         "acht", "neun", "zehn"]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]
            },
           # innerhalb von ...
           {"label": "Frist",
            "pattern": [{"LEMMA": "innerhalb"},
                        {"LEMMA": "von"},
                        {"IS_DIGIT": True},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]
            },
           {"label": "Frist",
            "pattern": [{"TEXT": "innerhalb"},
                        {"TEXT": "von"},
                        {"TEXT": {"IN": ["eines", "einer", "einem",
                                         "zwei", "drei", "vier",
                                         "fünf", "sechs", "sieben",
                                         "acht", "neun", "zehn"]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]},
           # innerhalb eines/einer/einem ...
           {"label": "Frist",
            "pattern": [{"TEXT": "innerhalb"},
                        {"TEXT": {"IN": ["eines", "einer", "einem",]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]},
           # innerhalb des/der
           {"label": "Frist",
            "pattern": [{"TEXT": "innerhalb"},
                        {"TEXT": {"IN": ["des", "der", "dem",]}},
                        {"LEMMA": {"IN": ["Zeitraum", "Beurteilungszeitraum",
                                          "Frist"]}}]},

           # spätestens .... vor
           {"label": "Frist",
            "pattern": [{"TEXT": {"IN": ["spätestens", "mindestens"]}},
                        {"IS_DIGIT": True},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}},
                        {"LEMMA": "vor"},
                        {"POS": "NOUN"}]
            },
           {"label": "Frist",
            "pattern": [{"TEXT": {"IN": ["spätestens", "mindestens"]}},
                        {"TEXT": {"IN": ["eine", "einen", "ein",
                                         "zwei", "drei", "vier",
                                         "fünf", "sechs", "sieben",
                                         "acht", "neun", "zehn"]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}},
                        {"LEMMA": "vor"},
                        {"POS": "NOUN"}]
            },
           # spätestens alle ... Jahre
           {"label": "Frist",
            "pattern": [{"TEXT": {"IN": ["spätestens", "mindestens"]}},
                        {"TEXT": "alle"},
                        {"TEXT": {"IN": ["zwei", "drei", "vier",
                                         "fünf", "sechs", "sieben",
                                         "acht", "neun", "zehn"]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]
            },
           # spätestens innerhalb eines Monats
           {"label": "Frist",
            "pattern": [{"TEXT": {"IN": ["spätestens", "mindestens"]}},
                        {"TEXT": "innerhalb"},
                        {"TEXT": {"IN": ["eines", "einer"]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]},
           # spätestens innerhalb von ...
           {"label": "Frist",
            "pattern": [{"TEXT": {"IN": ["spätestens", "mindestens"]}},
                        {"TEXT": "innerhalb"},
                        {"TEXT": "von"},
                        {"TEXT": {"IN": ["einem", "einer",
                                         "zwei", "drei", "vier",
                                         "fünf", "sechs", "sieben",
                                         "acht", "neun", "zehn"]}},
                        {"LEMMA": {"IN": ["Minute", "Stunde", "Tag",
                                          "Woche", "Monat", "Jahr"]}}]},
           # spätestens mit Ablauf...
           # {"label": "Frist",
           #  "pattern": [{"LOWER": "spätestens"},
           #              {"TEXT": "mit"},
           #              {"LEMMA": {"IN": ["Ablauf", "Beginn"]}},
           #              {"TEXT": "des"},
           #              {"LEMMA": "Monat"},
           #              {"TEXT": ","},
           #              {"TEXT": "in"},
           #              {"TEXT": {"IN": ["dem", "der"]}}]},
           # {"label": "Frist",
           #  "pattern": "spätestens mit Ablauf des Monats"},
           # unverzüglich u.ä. Adverbien
           # {"label": "Frist",
           #  "pattern": [{"TEXT": "unverzüglich"}]},
           # {"label": "Frist",
           #  "pattern": [{"TEXT": "unmittelbar"}]},
           # {"label": "Frist",
           #  "pattern": [{"TEXT": "rechtzeitig"}]},
           # {"label": "Frist",
           #  "pattern": [{"TEXT": "frühzeitig"}]},
           # {"label": "Frist",
           #  "pattern": [{"TEXT": "umgehend"}]},
           {"label": "Frist",
            "pattern": [{"TEXT": {"IN": ["unverzüglich", "unmittelbar",
                                         "rechtzeitig",
                                         "frühzeitig", "umgehend"]}}]},
           # PP
           # P + NOUN
           {"label": "Frist",
            "pattern": [{"TEXT": {"IN": ["nach", "vor", "bei", "ab", "mit"]}},
                        {"LEMMA": {"IN": ["Ablauf", "Beginn",
                                          "Abschluß", "Antragstellung",
                                          "Anhörung", "Ausstellung",
                                          "Eintritt",
                                          "Vollendung", "Beendigung"]}}]},
           # P + DET + NOUN
           {"label": "Frist",
            "pattern": [{"TEXT": {"IN": ["nach", "vor", "bei", "ab"]}},
                        {"POS": "DET"},
                        {"LEMMA": {"IN": ["Ablauf", "Beginn",
                                          "Abschluß", "Antragstellung",
                                          "Anhörung", "Ausstellung",
                                          "Eintritt",
                                          "Vollendung", "Beendigung"]}}]},
           # P + bis + zu + DET + NOUN
           {"label": "Frist",
            "pattern": [{"TEXT": "bis"},
                        {"TEXT": "zu"},
                        {"POS": "DET"},
                        {"LEMMA": {"IN": ["Ablauf", "Beginn",
                                          "Abschluß", "Antragstellung",
                                          "Anhörung", "Ausstellung",
                                          "Eintritt",
                                          "Vollendung", "Beendigung"]}}]},
           # P + bis zur/zum + Noun
           {"label": "Frist",
            "pattern": [{"LOWER": {"IN": ["spätestens", "mindestens",
                                          "frühestens", "längstens"]},
                         "OP": "*"},
                        {"TEXT": "bis"},
                        {"TEXT": {"IN": ["zur", "zum"]}},
                        {"TEXT": {"IN": ["Ablauf", "Beginn",
                                         "Abschluß", "Antragstellung",
                                         "Anhörung", "Ausstellung",
                                         "Eintritt", "Ende", 
                                         "Vollendung", "Beendigung"]}}]},
           ]

# thespat = theruler.from_disk("patternlists/patterns.jsonl").add_patterns(getspat)
thespat = theruler.add_patterns(getspat)

matcher = DependencyMatcher(thenlp.vocab)
deppat = [
    {
        "RIGHT_ID": "anchor_prep",
        "RIGHT_ATTRS": {"POS": "ADP"}
    },
    {
        "LEFT_ID": "anchor_prep",
        "REL_OP": ">",
        "RIGHT_ID": "head_noun",
        "RIGHT_ATTRS": {"DEP": "nk"}
    },
    {
        "LEFT_ID": "anchor_prep",
        "REL_OP": ">",
        "RIGHT_ID": "adverb_spätestens",
        "RIGHT_ATTRS": {"DEP": "mo"}
        },
    {
        "LEFT_ID": "head_noun",
        "REL_OP": ">",
        "RIGHT_ID": "hd_verb",
        "RIGHT_ATTRS": {"DEP": "rc"}
    }
]


ea = EntitiesForNorms(
    inputfile,
    thenlp,
    theruler,
    thespat)
out = ea.predict()

# Setting up a DependencyMather working on the output of the EntityRuler
matcher.add("ABLAUF", [deppat])
doc = ea.nlp(ea.content)
matches = matcher(doc)

# Printing the input text
print("The input text: ")
print(ea.content)
# Printing the entities as labeled in the EntityRuler
print("")
print("The entities as labeled in the EntityRuler: ")
print([(ent.text, ent.label_) for ent in out.ents])
# Printing depency parser matches
print("")
print("Dependency parser matches in the form [(match-id, [token-index])]: ")
print(matches)

print("")
print("Doc span from min(token_ids) to max(token_ids)+1: ")
for mat in range(len(matches)):
    match_id, token_ids = matches[mat]
    # print((match_id, sorted(token_ids)))
    # print((match_id, [min(token_ids), max(token_ids)]))
    msp = doc[min(token_ids):max(token_ids)+1]
    dmsp = Span(doc, min(token_ids), max(token_ids)+1, label="Frist")
    # print(msp.text)
    print(dmsp.text + " --- " + dmsp.label_)

#    print([(span.text, span.label_) for span in doc.spans["theruler"]])
# match_id, token_ids = matches[0]
# for i in range(len(token_ids)):
#     print(deppat[i]["RIGHT_ID"] + ":", doc[token_ids[i]].text)
print("")
print("Testing the dependency patterns by printing RIGHT_ID values: ")
for m in range(len(matches)):
    match_id, token_ids = matches[m]
    for i in range(len(token_ids)):
        print(deppat[i]["RIGHT_ID"] + ":", doc[token_ids[i]].text)

