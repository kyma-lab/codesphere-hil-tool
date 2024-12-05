import os
from flair.data import Sentence
from flair.models import SequenceTagger
from tqdm import tqdm
import json
import helper

ner_tagger = SequenceTagger.load("flair/ner-german-legal")


# Using flair/ner-german-legal to construct patterns
# for SpaCy's EntityRuler


def match_handlungsgrundlage_and_hauptakteur(doc, epatterns):
    # sentence = Sentence(doc.text, use_tokenizer=False)
    sentence = Sentence(doc, use_tokenizer=False)
    ner_tagger.predict(sentence)

    for entity in sentence.get_spans('ner'):
        curtag = None
        if entity.tag == "INN":
            curtag = "Hauptakteur"
        elif entity.tag == "GS":
            curtag = "Handlungsgrundlage"
        if curtag is not None:

            wordsOfInstance = entity.text.split(' ')
            temp = []
            # print(wordsOfInstance)
            for i in wordsOfInstance:
                temp.append({"TEXT": i})
            pat = {"label": curtag,
                   "pattern": temp}
            if pat not in epatterns:
                epatterns.append(pat)

    return epatterns


def read_inputs(folder):
    epatterns = []
    for file in tqdm(os.listdir(folder)):
        file_path = folder + os.sep + file
        content = helper.read_file(file_path)
        epatterns = match_handlungsgrundlage_and_hauptakteur(content, epatterns)

    return epatterns


# folder_from = "/home/cunger/Documents/Canareno/balanced_corpus_annotation_ready"
<<<<<<< HEAD
folder_from = "/Users/cunger1/Documents/firstday/for_ner"
=======
folder_from = "/home/cunger/projects/model_comparison/Corpus/data/corpus_v2/dev"
>>>>>>> 648cc329bbd982db1156a168a386e060cce1f500
folder_to = "patternlists"
patterns = read_inputs(folder_from)

# verified: this produces .jsonl files
# in the correct format for SpaCy's EntityRuler
with open(folder_to + os.sep + "patterns.jsonl", 'w') as f:
    for entry in patterns:
        json.dump(entry, f)
        f.write('\n')


# uncomment if you want output on stdout
# print(patterns)


