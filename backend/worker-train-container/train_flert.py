# -*- coding: utf-8 -*-
import time
import shared.utils as utils
import flair
from flair.embeddings import TransformerWordEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from shared.config import BASE_MODELS_PATH, FLERT_TRAINING_EPOCHS


def trainTransformer(
    datapath, outputfolder, existing_model, existing_model_path
):
    """
Train a transformer-based sequence tagger using FLERT (Fine-tuned Language Embeddings for Named Entity Recognition and Text classification) approach.

:param datapath: The path to the dataset for training.
:param outputfolder: The folder to save the trained model.
:param existing_model: Flag indicating whether to use an existing model or not.
:param existing_model_path: The path to the existing model if `existing_model` is True.

:return: The classification report of the trained model.
"""
    start_time = time.time()

    TrainWithDev = True

    dataset = utils.loadCorpus(datapath)

    ner_dictionary = dataset.make_label_dictionary(label_type="ner")

    if existing_model:
        modelpath = existing_model_path
    else:
        modelpath = f"{BASE_MODELS_PATH}/xlm-roberta-large"

    # 4. initialize fine-tuneable transformer embeddings
    embeddings = TransformerWordEmbeddings(
        model=modelpath,
        layers="-1",
        subtoken_pooling="first",
        fine_tune=True,
        use_context=False,
    )

    # 5. initialize bare-bones sequence tagger (no CRF, no RNN, no reprojection)
    tagger = SequenceTagger(
        hidden_size=256,  # is required, doesnt do anything with use_rnn=False
        embeddings=embeddings,
        tag_dictionary=ner_dictionary,
        tag_type="ner",
        use_crf=False,
        use_rnn=False,
        reproject_embeddings=False,
    )

    # 6. initialize trainer
    trainer = ModelTrainer(tagger, dataset)

    # 7. run fine-tuning
    trainer.fine_tune(
        outputfolder,
        learning_rate=5.0e-6,  # following schweter et al
        mini_batch_size=16,
        max_epochs=FLERT_TRAINING_EPOCHS,
        train_with_dev=TrainWithDev,
    )

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
