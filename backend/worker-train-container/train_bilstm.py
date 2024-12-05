# -*- coding: utf-8 -*-
import time
import flair
from flair.embeddings import WordEmbeddings, FlairEmbeddings, StackedEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
import shared.utils as utils
from shared.config import FLAIR_MAX_EPOCHS



def trainBILSTM(
    datapath, outputfolder, existing_model=False, existing_model_path=None
):
    """
Train a BILSTM model for named entity recognition.

:param datapath: The path to the dataset.
:param outputfolder: The folder to save the trained model.
:param existing_model: Flag indicating whether to load an existing model.
:param existing_model_path: The path to the existing model.
:return: The classification report of the trained model.
"""
    start_time = time.time()
    print("Training BILSTM model.")

    dataset = utils.loadCorpus(datapath)
    ner_dictionary = dataset.make_label_dictionary(label_type="ner")

    # 4. initialize embedding stack with Flair and GloVe
    embedding_types = [
        WordEmbeddings("de"),
        FlairEmbeddings("de-forward"),
        FlairEmbeddings("de-backward"),
    ]

    embeddings = StackedEmbeddings(embeddings=embedding_types)

    # 5. initialize sequence tagger

    if existing_model:
        tagger = SequenceTagger.load(existing_model_path)
    else:
        # TODO: load our base version here instead of starting from nothing
        tagger = SequenceTagger(
            hidden_size=256,
            dropout=0.25,
            embeddings=embeddings,
            tag_dictionary=ner_dictionary,
            tag_type="ner",
            use_rnn=True,
            use_crf=True,
        )

    # 6. initialize trainer
    trainer = ModelTrainer(tagger, dataset)

    # 7. start training
    trainer.train(
        outputfolder,
        embeddings_storage_mode="cpu",  # cpu for big datasets (more than 60,000 sentences), gpu otherwise (is faster)
        train_with_dev=True,
        learning_rate=0.2,
        mini_batch_size=16,
        patience=5,  # 5, akbik 2018
        max_epochs=FLAIR_MAX_EPOCHS,
    )  # 150, akbik 2018

    time_total = time.time() - start_time

    print("Done. Training time: " + str(time_total / 60) + " minutes")

    # Evaluate
    start_time = time.time()

    # TODO: maybe use best model here if available
    classifier = SequenceTagger.load(outputfolder + '/final-model.pt')
    flair.set_seed(123)

    #!: MAKE THIS TEST SET EXIST
    # training without including dev set, using dev set for optimization purposes
    results = classifier.evaluate(dataset.test, gold_label_type="ner")
    rep = results.classification_report

    #sentences, f1-macro, precision (macro), recall (macro), f1-micro, precision (micro), recall (micro), augmentation method, fraction, replacement percentage, replacement source, training time
    time_total = (time.time() - start_time)
    print("Done. Evaluation time: " + str(time_total / 60) + " minutes")

    return results.classification_report
