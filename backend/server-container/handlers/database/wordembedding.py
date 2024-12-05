import pandas as pd
import gensim
import json
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from HanTa import HanoverTagger as ht
from nltk.corpus import stopwords
from string import punctuation, digits
import time
from sentence_transformers import SentenceTransformer


# TODO: ADD directories of models and law documents

nltk.download("punkt")
nltk.download("stopwords")


def lemmatize(query):
    tagger = ht.HanoverTagger("morphmodel_ger.pgz")
    query = nltk.word_tokenize(query)
    lemmata = tagger.tag_sent(query, taglevel=1)
    lemmatized = ""
    n = 1
    lemmatized = [x[n] for x in lemmata]
    return lemmatized


def get_mean_vector(word2vec_model, words):
    # remove out-of-vocabulary words
    words = [word for word in words if word in word2vec_model.wv.key_to_index]
    if len(words) >= 1:
        return np.mean(word2vec_model.wv[words], axis=0)
    else:
        return []


# Trains and saves word vectors


def trainWordEmbedding():
    print("train model based on content!")
    input_directory = ""  # TODO: Add preprocessed laws directory
    df = pd.read_json(input_directory, orient="split")
    print(df)
    law_content = df.content
    print(law_content)

    model = gensim.models.Word2Vec(
        min_count=2, vector_size=500, workers=4, window=5, sg=0, epochs=150
    )  # CBOW
    model.build_vocab(law_content)
    model.train(law_content, total_examples=model.corpus_count, epochs=model.epochs)
    model.save("/word2vec_laws.model")  # TODO:Add directory

    print("model has been trained!")

    model = gensim.models.Word2Vec.load(
        "/word2vec_laws.model"
    )  # TODO:Add same directory

    word_vectors = model.wv
    word_vectors.save("/word2vec_laws.wordvectors")  # TODO:Add directory

    input_directory = ""  # TODO: Add textualized laws directory
    file = open(input_directory)
    lawdata = json.load(file)

    input_directory = ""  # TODO: Add preprocessed laws directory
    content_file = open(input_directory)
    contentdata = json.load(content_file)

    laws = []
    i = 0
    for a_law, a_content in zip(lawdata["data"], contentdata["data"]):
        if a_law["type"] == "law":
            i += 1
            print(i)

        this_content = a_content["content"]
        vector = get_mean_vector(model, this_content)
        if vector == []:
            continue
        vector = vector.tolist()
        if a_law["type"] == "law":
            processed = {
                "type": a_law["type"],
                "titleLong": a_law["titleLong"],
                "content": a_law["content"],
                "vector": vector,
            }
        else:
            processed = {
                "type": a_law["type"],
                "belongs to": a_law["belongs to"],
                "content": a_law["content"],
                "vector": vector,
            }
        laws.append(processed)

    output_directory = "/vectorized_word2vec_laws.json"  # TODO:Add directory
    with open(output_directory, "w") as file:
        json.dump({"data": laws}, file, indent=2)

    file.close()


def umlauts(text):
    tempVar = text

    tempVar = tempVar.replace("ä", "ae")
    tempVar = tempVar.replace("ö", "oe")
    tempVar = tempVar.replace("ü", "ue")
    tempVar = tempVar.replace("Ä", "Ae")
    tempVar = tempVar.replace("Ö", "Oe")
    tempVar = tempVar.replace("Ü", "Ue")
    tempVar = tempVar.replace("ß", "ss")

    return tempVar


def trainDocEmbedding():
    tokenized_law = []
    input_directory = ""  # TODO: Add preprocessed laws directory
    file = open(input_directory)
    lawdata = json.load(file)
    for a_law in lawdata["data"]:
        this_content = a_law["content"]
        tokenized_law.append(this_content)

    german_stop_words = stopwords.words("german")
    german_stop_words_to_use = []
    addition = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "§",
    ]
    for word in german_stop_words:
        german_stop_words_to_use.append(umlauts(word))
    german_stop_words_to_use.extend(addition)

    input_directory = ""  # TODO: Add textualized laws directory
    file = open(input_directory)
    lawdata = json.load(file)
    law_content = []
    tokenized_law = []
    i = 0
    for a_law in lawdata["data"]:
        if a_law["type"] == "law":
            i += 1
            print(i)
        this_content = a_law["content"]

        this_content = umlauts(this_content)
        this_content = " ".join((this_content.strip("\n").split()))
        remove_pun = str.maketrans("", "", punctuation)
        this_content = this_content.translate(remove_pun)
        remove_digits = str.maketrans("", "", digits)
        this_content = this_content.translate(remove_digits)
        this_content = [
            word
            for word in this_content.split()
            if word.lower() not in german_stop_words_to_use
        ]
        this_content = " ".join(this_content)

        this_content = " ".join(lemmatize(this_content))
        this_content = word_tokenize(this_content.lower())
        tokenized_law.append(this_content)
        processed = {"content": this_content}
        law_content.append(processed)

    output_directory = ""  # TODO: Add preprocessed laws directory
    with open(output_directory, "w") as file:
        json.dump({"data": law_content}, file, indent=2)

    tagged_data = [TaggedDocument(d, [i]) for i, d in enumerate(tokenized_law)]
    print("Tagged Documents!")

    # Train doc2vec model
    start_time = time.time()
    model = Doc2Vec(
        tagged_data,
        vector_size=500,
        window=5,
        alpha=0.025,
        min_alpha=0.0001,
        min_count=2,
        workers=4,
        dm=1,
        epochs=150,
    )  # Distributed Memory PV-DM
    model.build_vocab(tagged_data)
    model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)

    # Save trained doc2vec model
    model.save("")

    print("model saved!")
    model_time = time.time()

    model = Doc2Vec.load("")

    input_directory = ""  # TODO: Add preprocessed laws directory

    write_directory = ""  # TODO: Add textualized laws directory

    file = open(write_directory)
    lawdata = json.load(file)

    content_file = open(input_directory)
    contentdata = json.load(content_file)

    # Save vectors to JSON
    laws = []
    i = 0
    for a_law, a_content in zip(lawdata["data"], contentdata["data"]):
        if a_law["type"] == "law":
            i += 1
            print(i)

        this_content = a_content["content"]

        this_content = umlauts(this_content)
        this_content = " ".join((this_content.strip("\n").split()))
        remove_pun = str.maketrans("", "", punctuation)
        this_content = this_content.translate(remove_pun)
        remove_digits = str.maketrans("", "", digits)
        this_content = this_content.translate(remove_digits)
        this_content = [
            word
            for word in this_content.split()
            if word.lower() not in german_stop_words_to_use
        ]
        this_content = " ".join(this_content)
        this_content = " ".join(lemmatize(this_content))
        this_content = word_tokenize(this_content.lower())

        vector = model.infer_vector(this_content).tolist()
        if a_law["type"] == "law":
            processed = {
                "type": a_law["type"],
                "titleLong": a_law["titleLong"],
                "content": a_law["content"],
                "vector": vector,
            }
        else:
            processed = {
                "type": a_law["type"],
                "belongs to": a_law["belongs to"],
                "content": a_law["content"],
                "vector": vector,
            }
        laws.append(processed)

    output_directory = ""
    with open(output_directory, "w") as file:
        json.dump({"data": laws}, file, indent=2)

    file.close()
    print("Time it took for the model: ", (model_time - start_time))


# Preprocesses laws for downloaded BERT model and saves vectors for each document


def trainBert():
    input_directory = "norms_only.json"  # TODO: Add textualized laws directory
    file = open(input_directory)
    lawdata = json.load(file)
    model = SentenceTransformer(
        "sentence-transformers/distiluse-base-multilingual-cased-v1"
    )
    laws = []
    i = 0
    for a_law in lawdata["norms"]:
        vector = model.encode(a_law["content"])
        vector = vector.tolist()
        print(i)
        i += 1
        processed = {
            "jurabk": a_law["jurabk"],
            "enbez": a_law["enbez"],
            "title": a_law["title"],
            "content": a_law["content"],
            "link": a_law["link"],
            "vector": vector,
        }
        laws.append(processed)
    output_directory = "vectorized_norms.json"
    with open(output_directory, "w") as file:
        json.dump({"norms": laws}, file, indent=2)
    file.close()
