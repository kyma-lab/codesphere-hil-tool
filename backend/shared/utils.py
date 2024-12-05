from datetime import datetime, timezone
import os
from flair.datasets import ColumnCorpus
import time
import json
from typing import List, Tuple
import shutil
import uuid
from pathlib import Path
import logging
from somajo import SoMaJo

from shared.config import THRESHOLD, TESTING, BASE_MODELS_PATH, USER_DATA_PATH, BASE_TMP_PATH
from shared.db import get_data_for_interval, get_date_end_for_model, insertOne
from shared.file import File

tokenizer = SoMaJo("de_CMC", split_sentences=True, split_camel_case=False)


class ReopenableFileHandler(logging.FileHandler):
    """
    A custom file handler that allows reopening the log file after a certain number of writes.
    Required because logrotate changes the file descriptor, so the file needs to be reopened.
    Detecting the change in file descriptor is not possible, so we reopen the file after a certain number of writes.
    This is not a good solution, but best we can do without rewriting / rethinking the entire logging system.

    Args:
        filename (str): The name of the log file.
        mode (str, optional): The mode in which the file is opened. Defaults to 'a'.
        encoding (str, optional): The encoding used for the file. Defaults to None.
        delay (bool, optional): Whether to delay file opening until the first log message is emitted. Defaults to False.
        check_interval (int, optional): The number of writes after which the file should be reopened. Defaults to 50.
    Methods:
        emit(record): Overrides the emit method of the base class to reopen the file after a certain number of writes.
        reopen_file(): Reopens the log file, regardless of its status.
    """

    def __init__(self, filename, mode='a', encoding=None, delay=False, check_interval=50):
        super().__init__(filename, mode, encoding, delay)
        self.check_interval = check_interval

        # todo: if we leave it like this, also add something that reopens it every minute, by using last-reopen timestamp
        # todo: if we leave it like this, buffer the last 50 log mesages and re-write them to the new file if it is reopened (might cause duplicates, but better than losing them)
        self.write_count = 0

    def emit(self, record):
        try:
            if self.write_count >= self.check_interval:
                self.reopen_file()
                self.write_count = 0
            super().emit(record)
            self.write_count += 1
        except Exception:
            self.handleError(record)

    def reopen_file(self):
        """ Reopen the log file, regardless of its status. """
        try:
            # Close the existing file stream
            if self.stream:
                self.stream.close()
            # Open a new file stream
            self.stream = self._open()
        except Exception as e:
            # Log any exception that occurs while reopening the file
            self.handleError(f"Error reopening log file: {e}")


def setup_logger(container_name, log_file):
    logger = logging.getLogger(container_name) # Use container name as logger name

    # todo: move this directory into the config file and make it configurable
    log_dir = "/app/shared/logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set to debug to see all log messages
    # Set to info to reduce the number of log messages
    logger.setLevel(logging.DEBUG)

    # need a custom file handler to re-open the files at fixed intervals
    # note: settting check interval to 50 will cause at most 50 log messages to be lost, on average 25
    handler = ReopenableFileHandler(log_file, check_interval=50)
    
    # Define the log format, including timestamp, log level, container name, and message
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

def create_temp_pred_data(data: List[File]) -> Tuple[List[Path], List[str]]:
    """
    Create temporary prediction data for each single IOB file in the given list.
    Useful, so that each dataset can be processed independently.

    Args:
        data (List[File]): A list of File objects containing data for prediction.
    Returns:
        Tuple[List[Path], List[UUID]]: A tuple containing two lists:
            - tmpPaths (List[Path]): A list of temporary file paths.
            - uuids (List[UUID]): A list of randomly generated UUIDs.
    Raises:
        None.
    """

    tmpPaths = []
    uuids = []

    for el in data:

        rand_uuid = uuid.uuid4()
        tmpPath = Path(BASE_TMP_PATH + f"/{rand_uuid}")
        make_sure_folder_exists(BASE_TMP_PATH)
        make_sure_folder_exists(tmpPath)
        create_empty_file(f"{tmpPath}/train.txt")
        create_empty_file(f"{tmpPath}/dev.txt")

        with open(f"{tmpPath}/test.txt", "w", encoding="utf-8") as f:
            f.write(el.get_content())

        tmpPaths.append(tmpPath)
        uuids.append(rand_uuid)

    return tmpPaths, uuids


# returns None on error
def find_correct_modelpath(userid: str, modeltype: str, version: int) -> str:
    """
    Finds the correct model path based on the given user ID, model type, and version.
    Taskes into available model version and model type. 
    Also handles availability of best-model and final-model options from Flair Framework.

    Args:
        userid (str): The user ID.
        modeltype (str): The model type.
        version (int): The version of the model.
    Returns:
        str: The path to the correct model.
    Raises:
        None
    Examples:
        >>> find_correct_modelpath("user123", "bilstm_crf", 1)
        '/Users/robinerd/Documents/work_offline/HIL_prototype/backend/shared/data_user123/trained_models/bilstm_crf/model_1/best-model.pt'
    """



    if version == 0:
        if modeltype == "bilstm_crf":
            modelpath = Path(BASE_MODELS_PATH + "/bilstm-crf/final-model.pt")
        elif modeltype == "flert":
            modelpath = Path(BASE_MODELS_PATH + "/xlm-roberta-large/")
        elif TESTING:
            modelpath = "testingpath"
    else:
        model_basepath = Path(USER_DATA_PATH + f"/data_{userid}/trained_models/{modeltype}/model_{version}")
        
        # neeed two versions because its not clear which one exists, prefer version1 if available
        path_version1 = f"{model_basepath}/best-model.pt"
        path_version2 = f"{model_basepath}/final-model.pt"

        if check_path_exists(path_version1):
            modelpath = path_version1
        elif check_path_exists(path_version2):
            modelpath = path_version2
        else:
            print("Modelpath not found: ", model_basepath)
            # old version training did not finish or is corrupted, try to find previous version
            print("Trying to find previous version...")
            return find_correct_modelpath(userid, modeltype, version - 1)

    if check_path_exists(modelpath):
        print("Modelpath found: ", modelpath)
        return modelpath
    else:
        print("Modelpath not found: ", modelpath)
        return None


def most_recent_version(userid: str, modeltype: str):
    """
    Returns the most recent version number of a trained model for a given user and model type.
    Will be 0 if no training has been performed yet (or no pretrained models found).

    Parameters:
    - userid (str): The user ID.
    - modeltype (str): The type of the model.
    Returns:
    - int: The most recent model version number.
    Raises:
    - None
    Example:
    >>> most_recent_version("user123", "bilstm_crf")
    3
    """

    max_model_number = 0

    directory_path = Path(USER_DATA_PATH + f"/data_{userid}/trained_models/{modeltype}/")

    if get_date_end_for_model(userid, modeltype) is None:
        # no training has been performed yet, get base version
        return 0

    if not os.path.exists(directory_path):
        # training has been performed according to DB, but no saved models available
        return 0


    # find highest available model version
    for filename in os.listdir(directory_path):
        if filename.startswith("model_"):
            try:
                model_number = int(filename[len("model_") :])
                max_model_number = max(max_model_number, model_number)
            except ValueError:
                pass  # Ignore filenames that don't match the format

    return max_model_number


def create_empty_file(path):
    """
    Creates an empty file at the specified path.
    Helper for create_temp_pred_data.

    Parameters:
    path (str): The path where the empty file will be created.
    Returns:
    None
    """

    with open(path, "w", encoding="utf-8") as f:
        f.write("")


def create_temp_training_data(
    userid: str, dateStart: datetime, dateEnd: datetime
):
    """
    Creates temporary training dataset for a given user based on a specified date range.
    Retrieves the data contributed in that interval and saves it to a temporary location.

    Args:
        userid (str): The ID of the user.
        dateStart (datetime): The start date of the data range.
        dateEnd (datetime): The end date of the data range.
    Returns:
        str: The randomly generated UUID associated with the temporary training data. Can be used to build the path to the temporary data.
    """
    
    data_list = get_data_for_interval(userid, dateStart, dateEnd)
    rand_uuid = uuid.uuid4()

    path = Path(USER_DATA_PATH + f"/data_{userid}/{rand_uuid}")
    make_sure_folder_exists(USER_DATA_PATH)
    make_sure_folder_exists(Path(USER_DATA_PATH + f"/data_{userid}"))
    make_sure_folder_exists(path)

    # TODO: maybe we should split this, to also have a dev set?
    # TODO: the test set should exist in the future!!
    # TODO: dev set is also useful for improving training

    with open(f"{path}/train.txt", "w", encoding="utf-8") as f:
        for data in data_list:
            f.write(data)

    # temporary: copy hard-coded test and dev sets in same location as base-models
    # dont know if using relative or absolute paths is better, probably abs
    src_path = Path(BASE_MODELS_PATH + "/dev.txt")
    shutil.copy(src_path, f"{path}/dev.txt")
    src_path = Path(BASE_MODELS_PATH + "/test.txt")
    shutil.copy(src_path, f"{path}/test.txt")

    return rand_uuid


def get_interval_to_train_on(
        userid: str, modelname: str
) -> (datetime, datetime): # type: ignore
    """
    Get the interval to train on for a given user ID and model name.
    Wrapper for get_date_end_for_model.

    Args:
        userid (str): The ID of the user.
        modelname (str): The name of the model.
    Returns:
        tuple: A tuple containing the start and end datetime objects representing the interval to train on.
    """
    

    dateStart = get_date_end_for_model(userid, modelname)
    dateEnd = datetime.now(timezone.utc)
    return dateStart, dateEnd


def check_data_sufficient(userid: str, dateStart: datetime, dateEnd: datetime):
    """
    Check if the data is sufficient for the given user ID and date range.
    Wrapper for count_annotated_tokens.

    Args:
        userid (str): The user ID.
        dateStart (datetime): The start date of the range.
        dateEnd (datetime): The end date of the range.
    Returns:
        bool: True if the data is sufficient, False otherwise.
    """

    count = count_annotated_tokens(userid, dateStart, dateEnd)
    return count > THRESHOLD


def add_to_storage(userid: str, data: str, title: str) -> int:
    # TODO: check if data already exists, annotations compatible?

    document = {
            "userId": userid,
            "timestamp": time.time(),
            "postedOn": datetime.now(timezone.utc).isoformat(),
            "title": title,
            "data": data,
        }

    insertOne(f"data_{userid}", document)

    return count_annotated_tokens_instring(document["data"])


def count_annotated_tokens(
        userid: str, dateStart: datetime, dateEnd: datetime) -> int:
    """
    Counts the number of annotated tokens available in the database, given a user and a specified date range.
    Useful to check if there is enough data to train a model.

    Parameters:
    - userid (str): The ID of the user.
    - dateStart (datetime): The start date of the interval.
    - dateEnd (datetime): The end date of the interval.
    Returns:
    - int: The total count of annotated tokens.
    """
    

    data_list = get_data_for_interval(userid, dateStart, dateEnd)

    total_count = 0
    for data in data_list:
        total_count += count_annotated_tokens_instring(data)

    return total_count


def count_annotated_tokens_instring(data: str) -> int:
    """
    Counts the number of annotated tokens in a given string.
    Helper function for count_annotated_tokens.

    Parameters:
    - data (str): The input string to count annotated tokens from.
    Returns:
    - int: The number of annotated tokens in the string.
    """

    lines = data.split("\n")
    annotated_count = 0

    for line in lines:
        line = line.strip()
        if line:
            parts = line.split(" ")
            if len(parts) == 2:
                _, label = parts
                if label != "O":
                    annotated_count += 1

    return annotated_count


def check_path_exists(path):
    """
    Check if a given path exists.
    Args:
        path (str): The path to check.
    Returns:
        bool: True if the path exists, False otherwise.
    """

    return os.path.exists(path)


def make_sure_folder_exists(path):
    """
    Creates a folder at the specified path if it does not already exist.
    Warning: does not create parent folders if they do not exist, only one single folder / layer.
    Parameters:
    path (str): The path of the folder to be created.
    Returns:
    None
    """
    if not os.path.exists(path):
        os.mkdir(path)


def make_sure_file_not_exists(path):
    """
    Removes the file at the given path if it exists.
    Parameters:
    path (str): The path to the file.
    Returns:
    None
    """

    if os.path.exists(path):
        os.remove(path)


def loadCorpus(path):
    """
    Load a corpus from the given path using the ColumnCorpus class from Flair.
    Args:
        path (str): The path to the corpus.
    Returns:
        ColumnCorpus: The loaded corpus object.
    """

    columns = {0: "text", 1: "ner"}
    return ColumnCorpus(
        path,
        columns,
        train_file="train.txt",
        test_file="test.txt",
        dev_file="dev.txt",
    )


def saveCorpus(train, dev, test, dirname, timestamp=True): 
    """
    Save the corpus data into separate text files.
    Expected format is a list of sentences, where each sentence is a list of tokens (e.g. from flair.datasets.ColumnCorpus).
    Parameters:
    - train (list): List of sentences for training data.
    - dev (list): List of sentences for development data.
    - test (list): List of sentences for testing data.
    - dirname (str): Name of the directory to save the corpus files.
    - timestamp (bool): Whether to append a timestamp to the directory name. Default is True.
    Returns:
    None
    """


    if timestamp:
        current_time = datetime.now(timezone.utc).strftime("%H_%M_%S")
        dirname = dirname + "_" + current_time
    try:
        os.makedirs("./" + dirname + "/")
    except FileExistsError:
        print("Directory ", dirname, " already exists, skipping...")
        return

    with open("./" + dirname + "/train.txt", "w", encoding="utf-8") as myfile:
        for sentence in train:
            for token in sentence:
                myfile.write(
                    token.text + " " + token.get_tag("ner").value + "\n"
                )
            myfile.write("\n")
    with open("./" + dirname + "/test.txt", "w", encoding="utf-8") as myfile:
        for sentence in test:
            for token in sentence:
                myfile.write(
                    token.text + " " + token.get_tag("ner").value + "\n"
                )
            myfile.write("\n")
    with open("./" + dirname + "/dev.txt", "w", encoding="utf-8") as myfile:
        for sentence in dev:
            for token in sentence:
                myfile.write(
                    token.text + " " + token.get_tag("ner").value + "\n"
                )
            myfile.write("\n")


def convertToString(dataset):
    """
    Converts a dataset into a string representation.
    Expects the format from flair.datasets.ColumnCorpus.

    Args:
        dataset (list): A list of sentences, where each sentence is a list of tokens.

    Returns:
        str: The string representation of the dataset, where each token is followed by its named entity recognition (NER) tag.

    Example:
        >>> dataset = [["Hello", "world", "!"], ["This", "is", "a", "test."]]
        >>> convertToString(dataset)
        'Hello O\nworld O\n! O\n\nThis O\nis O\na O\ntest. O\n\n'
    """

    result = ""

    for sentence in dataset:
        for token in sentence:
            result += token.text + " " + token.get_tag("ner").value + "\n"
        result += "\n"

    return result


def mark_data_as_processed(
    userid: str, modeltype: str, dataEnd: datetime
):
    """
    Marks the data as processed for a given user.
    Works by saving the timestamp up to which the data has been processed.
    Args:
        userid (str): The ID of the user.
        modeltype (str): The type of the model.
        dataEnd (datetime): The end date of the data.
    Returns:
        None
    """
    document = {
        "modeltype": modeltype,
        "date": dataEnd.isoformat(),
    }

    insertOne(f"list_{userid}", document)


def append_to_train_queue(userid: str):
    """
    Appends a user to the training queue.
    This serves as record to limit the number of tasks per user (balancing).
    Parameters:
    - userid (str): The ID of the user to be appended to the queue.
    Returns:
    None
    """

    insertOne("training_queue", {"user": userid, "date": datetime.now(timezone.utc)})




def sanitize_input(input_string):
    stripped = input_string.strip()

    return stripped


def check_bilstm_health():
    modelExists = os.path.exists("./shared/base-models/bilstm-crf/final-model.pt")

    if modelExists:
        return "Installed"

    return "Unavailable"


def check_xlmr_health():
    modelExists = os.path.exists("./shared/base-models/xlm-r/best-model.pt")

    if modelExists:
        return "Installed"

    return "Unavailable"


def tokenize(text):  # expects string as input
    tokenized_and_split = ""
    sentences = tokenizer.tokenize_text([text])
    
    result = []
    for sen in sentences:
        tokenized_sentence = []
        for token in sen:
            tokenized_sentence.append(str(token.text))
        result.append(tokenized_sentence)

    for sen in result:
        for tok in sen:
            tokenized_and_split += tok + "\n"
        tokenized_and_split += "\n"


    return tokenized_and_split