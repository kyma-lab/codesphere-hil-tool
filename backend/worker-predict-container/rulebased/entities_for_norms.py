from additional_modules import match_bedingung, match_aktion, match_signalwort
# from additional_modules import match_handlungsgrundlage, match_hauptakteur
from additional_modules import match_frist, match_mitwirkender, match_handlungsgrundlage
from helper import read_file


class EntitiesForNorms:
    """Annotating Named Entities with the EntityRuler"""

    def __init__(self, inpath, nlp, sruler, spat):
        self.content = read_file(inpath)
        # Set up the pipeline
        self.nlp = nlp
        self.doc = self.nlp(self.content)
        # self.doc = []
        self.epatterns = []
        # Set up the EntityRuler
        self.ruler = sruler
        # EntityRuler patterns for initialization
        self.spat = spat

    def predict(self):
        doc = self.nlp(self.doc)
        bed = match_bedingung(doc, self.epatterns)
        akt = match_aktion(doc, bed)
        sig = match_signalwort(doc, akt)
        # fri = match_frist(doc, sig)
        # temporarily disabeling match_frist
        mwr = match_mitwirkender(doc, sig)
        hlg = match_handlungsgrundlage(doc, mwr)
        fri = hlg
        self.ruler.add_patterns(fri)
        doc = self.nlp(doc)
        return doc

    def get_annotations(self):
        return self.doc

    def to_file(self, outpath):
        outs = []
        ## conll files start with newline!
        # conll files no longer start with newline (2024-03-26)
        # outs.append("\n")
        for token in self.doc:
            token_text = token.text
            token_iob = token.ent_iob_
            entity_type = token.ent_type_
            if token_iob in ("B", "I"):
                outs.append(f"{token_text} {token_iob}-{entity_type}\n")
            # Don't show spurious tokens such as SPACE = 103
            elif token.pos_ == "SPACE":
                outs.append("")
            else:
                outs.append(f"{token_text} {token_iob}\n")

        with open(outpath, "w", encoding="utf-8") as outputfile:
            outs.append("\n\n")
            for i in outs:
                outputfile.write(i) 
