# -*- coding: utf-8 -*-
from flair.models import SequenceTagger  # type: ignore
from datetime import datetime, timezone
from shared.utils import saveCorpus, loadCorpus, convertToString
from tool_visuals import visualize
import time
import argparse
from pathlib import Path
from shared.config import SAVE_PREDICTIONS


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(
        usage="python3 predict.py datasets/somedataset XLM-R",
        description="this script creates loads a previously saved model " +
                    " and uses it to predict tags on a provided dataset," +
                    " \n it also automatically creates a static .html " +
                    " file that visualizes the performed annotation.\n The " +
                    "results are saved in code/predicted/_modelname_timestamp."
    )

    parser.add_argument("path")
    parser.add_argument("model")
    args = parser.parse_args()
    path = Path(args.path)
    model = str(args.model)

    if not path.exists():
        print("Path to input data doesn't exist")
        raise SystemExit(1)

    performPrediction(path, model)

    time_total = time.time() - start_time
    print("Done. Prediction time: " + str(time_total / 60) + " minutes")


def loadModel(path):
    """
    Load a model from the given path (Flair Framework).
    Args:
        path (str): The path to the model file.
    Returns:
        tagger: The loaded model.
    """

    start_time = time.time()
    tagger = SequenceTagger.load(path)
    end_time = time.time()
    print("Loading model took:", end_time - start_time)
    return tagger  # type: ignore


def loadData(path):
    """
    Load a dataset from the given path (Flair Framework).
    Args:
        path (str): The path to the dataset.
    Returns:
        dataset: The loaded dataset.
    """

    start_time = time.time()
    dataset = loadCorpus(path)
    dataset = dataset.test
    end_time = time.time()
    print("Loading corpus took:", end_time - start_time)
    return dataset


def predictTags(tagger, model, dataset, userid, save=True):
    """
    Predicts tags for a given dataset using a tagger model.
    Parameters:
    tagger (Tagger): The tagger model used for prediction.
    model: The model used for prediction.
    dataset: The dataset to be predicted.
    userid (str): The user ID associated with the predictions.
    save (bool, optional): Whether to save the predictions to a file. Defaults to True.
    Returns:
    The predicted dataset.
    """


    start_time = time.time()
    tagger.predict(dataset, verbose=True)
    end_time = time.time()
    print("Prediction took:", end_time - start_time)

    # save predictions to file in IOB2 format
    if save:
        saveCorpus([], [], dataset, "shared/predicted/" + userid, timestamp=True)

    return dataset


def createHTML(userid):
    """
    Create an HTML file that visualizes the predictions.
    Parameters:
    userid (str): The user ID.
    Returns:
    None
    """
    # note: this is unstable, can break if time difference is too large / small
    try:
        current_time = datetime.now(timezone.utc).strftime("%H_%M_%S")
        visualize(
            "shared/predicted/" + userid +"_"+ current_time + "/test.txt",
            "shared/predicted/" + userid +"_"+ current_time + "/test.html",
        )
    except Exception as e:
        print("Error creating HTML file: ", e)


def performPrediction(datapath, modelpath, userid):
    """
    Perform prediction using the given datapath, modelpath, and userid.
    Parameters:
    - datapath (str): The path to the data file.
    - modelpath (str): The path to the model file.
    - userid (str): The user ID.
    Returns:
    - str: The result of the prediction converted to a string.
    """

    dataset = loadData(datapath)
    tagger = loadModel(modelpath)
    result = predictTags(tagger, modelpath, dataset, userid, save=SAVE_PREDICTIONS)
    if SAVE_PREDICTIONS:
        createHTML(userid) # uses timestamp to identify files
    return convertToString(result)


if __name__ == "__main__":
    main()
