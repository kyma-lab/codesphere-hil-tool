import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Vor Beginn der Maßnahme")
print(doc[2].morph)  
print(doc[2].pos_)  
