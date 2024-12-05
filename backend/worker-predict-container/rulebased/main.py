# This is a sample Python script.
import spacy
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


from spacy.tokens import Token, Span
from spacy.language import Language

import helper
import aktion
import handlungsgrundlage
import ergebnisempfänger
import hauptakteur
import mitwirkender
import frist
import bedingung
import signalwort
import colorama
from colorama import Fore, Back


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    colorama.init(autoreset=True)
    nlp = spacy.load("de_core_news_sm")

    nlp.add_pipe('aktion')
    doc = nlp(u"Werden Abfälle zur Beseitigung überlassen, weil die Pflicht zur Verwertung aus den in § 7 Absatz 4 genannten Gründen nicht erfüllt werden muss,\nsind die öffentlich-rechtlichen Entsorgungsträger zur Verwertung verpflichtet, soweit bei ihnen diese Gründe nicht vorliegen.")
    for token in doc:
        if token._.get("is_aktion"):
            print(" " + Back.RED + token.text, end="")
        else:
            print(" " + token.text, end="")
