import os
import uuid
import pika
import shutil
import datetime
import json
import threading
from typing import List

from tempfile import NamedTemporaryFile

from flask_jwt_extended import JWTManager, create_access_token

from shared.db import insertOne, get_all_users, clear_database
from shared.config import JWT_SECRET_KEY, ADMIN_USER, ADMIN_PASSWORD, MAX_PDF_COUNT, MAX_PDF_SIZE, PDF_EXTRACT_ENGINE, DEFAULT_MODEL, RABBITMQ_HOST, USER_DATA_PATH, ALLOW_CORS, DISABLE_TRAINING
from shared.utils import add_to_storage, create_temp_pred_data, setup_logger, check_bilstm_health, check_xlmr_health, tokenize
from shared.file import File
from shared.validation import validateIOB, validateIOB_Testset, validate_input, validate_file_title_format, validate_file_content_format

from pdfminer.high_level import extract_text
import pytesseract
from pdf2image import convert_from_path



def server_health_handler(logger):
    """
    Handler function for the '/api/health' endpoint.
    Exposes information about the health status of the different components of the server.
    Can be seen by all users on the settings page in the frontend.
    
    Args:
        logger: The logger object used for logging information.
        
    Returns:
        A dictionary containing the health status of different components:
        - 'predictor': The response from the 'heartbeat_predictor' component.
        - 'trainer': The response from the 'heartbeat_trainer' component.
        - 'bilstm-crf': The response from the 'check_bilstm_health' function.
        - 'xlm-r': The response from the 'check_xlmr_health' function.
    """

    logger.info("Received GET request on /api/health")
    pred_response = send_heartbeat_request("heartbeat_predictor")
    train_response = send_heartbeat_request("heartbeat_trainer")
    bilstm_response = check_bilstm_health()
    xlmr_response = check_xlmr_health()

    return {'predictor': pred_response, 'trainer': train_response, 'bilstm-crf': bilstm_response, 'xlm-r': xlmr_response}

def clear_rabbitmq_handler(logger):
    """
    Handles an API endpoint that clears the RabbitMQ queues used in the application.
    Can be used by users with the role 'admin' to clear the queues in case of issues.

    Args:
    - logger: The logger object used for logging.

    Returns:
    - A tuple containing the status and the HTTP status code.
    - If the RabbitMQ queues are cleared successfully, the status will be "success" and the HTTP status code will be 200.
    - If an error occurs while clearing the RabbitMQ queues, the status will be "error" and the HTTP status code will be 400.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                RABBITMQ_HOST))
        channel = connection.channel()

        channel.queue_delete(queue='prediction')
        channel.queue_delete(queue='annotated_data')
        channel.queue_delete(queue="new_training")

        connection.close()
    
    except Exception as e:
        return "error", 400
    

    logger.info("RabbitMQ queues cleared by admin")

    return "success", 200

def reset_mongodb_handler(logger):
    """
    Handles an API endpoint that allows for the deletion all collected data in the mongoDB database.
    Deletes all users and their data from the database. Admin user is not deleted.
    Also deletes on-disk files stored in the user-data directory.

    Args:
        logger: The logger object for logging messages.

    Returns:
        A tuple containing the status and the HTTP status code.
        - If the database reset and file clearing is successful, returns ("success", 200).
        - If there is an error during the process, returns ("error", 400).
    """
    ok = clear_database()

    logger.info("mongoDB database reset by admin")

    if not ok:
        return "error", 400

    users = get_all_users()

    logger.debug("Attempting to clear user-files...")

    # todo: should make this safer
    for user in users:
        user_dir = os.path.join(USER_DATA_PATH, "data_" + user['username'])
        logger.debug(f"Clearing user-files for {user['username']}...")
        if os.path.exists(user_dir) and os.path.isdir(user_dir):
            shutil.rmtree(user_dir)

    # also remove the /tmp files
    tmp_dir = os.path.join(USER_DATA_PATH, "tmp")
    logger.debug("Clearing tmp-files...")
    if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)

    logger.debug("local user-files cleared by admin")

    return "success", 200



def handle_prediction_request(logger, data, userid):
    """
    Handles the API endpoint for making prediction requests to the server.
    The endpoint receives a userid, a list of files and a method to use for prediction.
    The files are tokenized and sent to the RabbitMQ queue for processing.
    The response is received asynchronously and returned to the client.

    Args:
        logger: The logger object for logging messages.
        data: The data containing the files to be processed.
        userid: The ID of the user making the request.  

    Returns:
        A tuple containing the status message, the HTTP status code, and the data to be returned to the client.
    
    """

    if userid is None:
        return "User not authenticated", 401, None
    
    fileList = [File(el['title'], tokenize(el['content'])) for el in data["files"]]


    # get method
    method = data["method"]

    if method != "bilstm_crf" and method != "rule-based" and method != "xlm_r":
        return "invalid method", 400, None

    logger.info(f"Received prediction request for {len(fileList)} files and method: {method}")

    # validate IOB format (created by our tokenizer, maybe not do this?)
    for file in fileList:
        violations = validateIOB_Testset(file.get_content())
        if violations != 0 :  # disable this check for testing
            logger.info(f"returned 400, found input file with invalid IOB format ({violations} violations).")
            return "invalid input  2", 400, None
    
    logger.info("Input passed IOB validation test.")


    # rate limit / user authentication?
    # should use/combine the relevant models automatically, no user choice
    logger.info("Sent prediction task to RabbitMQ.")
    
    # returns list of strings (iob annotated format)
    annotatedFileList = send_prediction_request(logger, userid, fileList, method)

    # convert List of Files objects to json and return it
    data = {"files": []}
    for file in annotatedFileList:
        data["files"].append({"title": file.get_title(), "content": file.get_content()})

    logger.info("Successfully returned predictions in HTTP response")

    return "success", 200, data


# todo: move out of this file
def send_prediction_request(logger, userid: str, data: List[File], modeltype: str):
    """
        Here we send the prediction request to the RabbitMQ queue and wait for the response.
        The response is then returned to the client.
        TODO: clean this up, make it more readable
    """
    tmpPaths, random_uuids = create_temp_pred_data(data)
    #print("Check 01")

    # send prediction task to RabbitMQ queue
    connection = establish_connection()
    channel = connection.channel()
    channel.queue_declare(queue="prediction")
    channel.queue_declare(queue="annotated_data")
    #print("Check 02")

    # prep for serialization
    random_uuids = [str(uuid) for uuid in random_uuids]
    tmpPaths = [str(tmpPath) for tmpPath in tmpPaths]

    message = {
        "tmpPaths": tmpPaths, # convert POSIX to string, for serialization
        "userid": userid,
        "random_uuids": random_uuids,
        "modeltype": modeltype,
    }

    #print("Check 03")

    message = json.dumps(message)

    channel.basic_publish(exchange="", routing_key="prediction", body=message)
    #print("Check 04")

    # callback, variables and lock for
    # handling result-message sent back from prediction task
    annotatedFiles = None
    lock = threading.Lock()
    #print("Check 05")

    # change this message format to a custom class
    def callback(ch, method, properties, body):
        #print("callback")

        nonlocal annotatedFiles

        # parse body as json
        payload = json.loads(body.decode())

        message_uuids = payload["random_uuids"]

        # check if all uuids match
        if sorted(message_uuids) == sorted(random_uuids):
            #logger.debug(f"UUID match for incoming response. Received annotated data for {len(payload['annotatedFiles'])} files.")

            # update global variable
            annotatedFiles = payload["annotatedFiles"]

            # update the content in the received File objects
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.close()
        else:
            #logger.debug(f"UUID mismatch, rejecting response! ({message_uuids} != {random_uuids})")
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="annotated_data", on_message_callback=callback)
    channel.start_consuming()
    #print("Check 06")

    # is necessary because flask doesnt support async
    with lock:
        #print("Check 07")

        # wait for the annotatedFiles to be updated
        while annotatedFiles is None:
            pass
        
        #print("Check 08")
        # once annotatedFiles are available, update the data and return it
        for i in range(len(data)):
            data[i].set_content(annotatedFiles[i])

        # reset annotatedFiles
        annotatedFiles = None

    #print("Check 09")
    connection.close()
    return data


def establish_connection():
    """
    Establishes a blocking connection to a RabbitMQ server.

    Returns:
        pika.BlockingConnection: A blocking connection to the RabbitMQ server.
    """
    return pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_HOST, heartbeat=0)
    )


def declare_queues(queue_name, channel):
    """
    Used for the heartbeat functionality with rabbitmq.
    Declare two queues on the provided channel.

    This function declares a durable queue named as passed and an exclusive, 
    unnamed queue. The unnamed queue is typically used for temporary purposes and will 
    be deleted when the connection that declared it closes.

    Args:
        channel: The channel on which to declare the queues.
    """
    channel.queue_declare(queue=queue_name, durable=True)
    result = channel.queue_declare(queue='', exclusive=True)
    return result.method.queue


def send_heartbeat_request_message(queue_name, channel, callback_queue, correlation_id):
    """
    Used for the heartbeat functionality with rabbitmq.
    Sends a heartbeat request message to the 'heartbeat_predictor' queue.

    Args:
        channel (pika.channel.Channel): The channel through which the message is sent.
        callback_queue (str): The name of the callback queue to receive the response.
        correlation_id (str): The unique identifier for the message to correlate responses.

    Returns:
        None
    """
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body='heartbeat',
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=correlation_id
        )
    )


def consume_response(channel, callback_queue, correlation_id, heartbeat_ack, response_received):
    """
    Used for the heartbeat functionality with rabbitmq.
    Consumes a response from a specified callback queue and processes the response with on_response.

    Notes:
        This function will stop consuming if no response is received within the timeout period.
    """

    def on_response(ch, method, properties, body, correlation_id, heartbeat_ack, response_received):
        if properties.correlation_id == correlation_id:
            heartbeat_ack.append(body.decode())
            ch.basic_ack(delivery_tag=method.delivery_tag)
            response_received.set()
            ch.stop_consuming()

    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=lambda ch, method, properties, body: on_response(
            ch, method, properties, body, correlation_id, heartbeat_ack, response_received
        )
    )
    try:
        # Problem: this will block the main thread for 2 seconds, not good, but ok for now
        channel.connection.process_data_events(time_limit=2)
        if not response_received.is_set():
            print("No response received within the timeout period.")
            channel.stop_consuming()
    except pika.exceptions.ConnectionClosedByBroker:
        print("Connection closed by broker.")
    except pika.exceptions.AMQPChannelError as err:
        print(f"AMQP Channel Error: {err}")
    except pika.exceptions.AMQPConnectionError:
        print("AMQP Connection Error")


def send_heartbeat_request(queue_name):
    """
    Used for the heartbeat functionality with rabbitmq.
    Sends a heartbeat request to a server and waits for a response.

    This function establishes a connection, declares necessary queues, and sends a heartbeat
    request message. It then waits for a response and returns the response if received, or
    an error message if no response is received.

    Returns:
        str: The response received from the server, or "Error" if no response is received.
    """
    connection = establish_connection()
    channel = connection.channel()
    callback_queue = declare_queues(queue_name, channel)
    correlation_id = str(uuid.uuid4())

    heartbeat_ack = []
    response_received = threading.Event()

    send_heartbeat_request_message(queue_name, channel, callback_queue, correlation_id)
    consume_response(channel, callback_queue, correlation_id, heartbeat_ack, response_received)
    connection.close()

    if not heartbeat_ack:
        return "Error"
    return heartbeat_ack[0]


def upload_handler(logger, files, content_length):
    """
        Handles the API endpoint for uploading PDF files to the server and extracting the text from them.
        The extracted text is returned to the client.
        There are limits on the number of files and the combined filesize that will be processed.
        Different extraction engines can be used, currently Tesseract and PDFMiner are supported.
        The extraction engine can be configured in the config file.
    """
    logger.info("Received POST request on /api/upload")

    if not files:
        logger.info("returned 400, no file part in request.")
        return "no file part", 400, {"texts": [], "filenames": []}

    # check that the number of pdfs is below 3
    if len(files) > MAX_PDF_COUNT:
        logger.info("returned 400, too many files.")
        return "too many files", 400, {"texts": [], "filenames": []}

    logger.info(f"Received extraction request containing {len(files)} files.")

    # check that combined filesize is below 19MB
    if content_length:
        content_length = int(content_length)
        logger.info("Approximate total file size: " + str(content_length))
        if content_length > MAX_PDF_SIZE:
            logger.info("returned 400, file too large.")
            return "combined filesize too large", 400, {"texts": [], "filenames": []}
    else:
        logger.info("returned 400, Content-Length header not provided.")
        return "provide content-length header", 400, {"texts": [], "filenames": []}
    
    # would make sense to move the check whether a file exists here too

    # check whether the file is a PDF
    for file in files.values():
        file_start = file.stream.read(4) # read the first 4 bytes, should contain PDF header
        file.stream.seek(0)  # reset file pointer to the beginning
        if file_start == b'%PDF':
            logger.info("Verfified that file is a PDF.")
        else:
            logger.info("returned 400, invalid filetype.")
            return "invalid filetype", 400, {"texts": [], "filenames": []}

    texts = []
    filenames = []
    for file in files.values():
        logger.debug(f"Checking file: {file.filename}")
        filenames.append(file.filename)

        if file.filename == "":
            logger.info("returned 400, no selected file.")
            return "no selected file", 400, {"texts": [], "filenames": []}

        # Save the file to a temporary file
        temp_file = NamedTemporaryFile(delete=False)
        file.save(temp_file.name)

        # Convert PDF to images
        images = convert_from_path(temp_file.name)

        # Extract text from images
        if PDF_EXTRACT_ENGINE == "tesseract":
            text = ""
            for i in range(len(images)):
                text += pytesseract.image_to_string(images[i], lang="deu")
            texts.append(text)
        elif PDF_EXTRACT_ENGINE == "pdfminer":
            text = extract_text(temp_file.name)
            texts.append(text)
        else:
            raise ValueError("Invalid engine")

        # Delete the temporary file
        os.unlink(temp_file.name)

    # return msg, status and extracted texts
    return "success", 200, {"texts": texts, "filenames": filenames}

def handle_contribution(logger, data, userid):
    """
    Handles the API endpoint where users can contribute annotated data to the database.
    The database is user-specific and once sufficient data is collected, the model is retrained.
    The model retraining feature is disabled by default.

    Args:
        logger: The logger object for logging messages.
        data: The data containing the files to be contributed.
        userid: The ID of the user making the contribution.

    Returns:
        A tuple containing a success message and a status code.

    Raises:
        None.
    """
    
    if DISABLE_TRAINING:
        return "Training is disabled", 503

    if userid is None:
        return "User not authenticated", 401

    # verify input parameters
    
    file_contents = [el['content'] for el in data["files"]]
    file_titles = [el['title'] for el in data["files"]]

    if len(file_contents) != len(file_titles):
        logger.info("returned 400, input length content and titles mismatch.")
        return "invalid input 3", 400

    # TODO: improve this check
    for title in file_titles:
        if not validate_file_title_format(title):
            logger.info("returned 400, input format of file title does not match criteria.")
            return "invalid input", 400

    # TODO: improve this check
    for content in file_contents:
        if not validate_file_content_format(content):
            logger.info("returned 400, input format of file content does not match criteria.")
            return "invalid input", 400
    
    modeltype = DEFAULT_MODEL  # is this flexible?

    # todo: handle users that work with rule-based model - maybe no training necessary? currently always still training the bilstm model

    # handle each of the documents
    for i in range(len(file_contents)):
        document = file_contents[i]

        violations = validateIOB(document, count=True, tab_separated=False)
        if violations != 0 :  # disable this check for testing
            logger.info("returned 400, input format does not comply with IOB standard.")
            return "invalid input", 400

        add_to_storage(userid, file_contents[i], file_titles[i])

    
    # send task to RabbitMQ queue
    logger.info("Contribution added to database.")
    connection = establish_connection()
    channel = connection.channel()
    channel.queue_declare(queue="new_training")
    channel.basic_publish(exchange="", routing_key="new_training", body=f"{userid},{modeltype}")
    connection.close()
    logger.info("Performed re-training check.")

    return "success", 200


def handle_bpmn_save(bpmn_xml, username):
    """
    Saves the BPMN XML content for a given username.
    This was relevant for the evaluation study, but is not used by the application itself.

    Args:
        bpmn_xml (str): The BPMN XML content to be saved.
        username (str): The username associated with the BPMN XML content.
    Returns:
        str: A message indicating the success or failure of the save operation.
    Raises:
        None
    """
    if not validate_input(username):
        return "Bad username", 400

    if username is None or bpmn_xml is None:
        return "Bad username or content", 400
    
    insertOne("bpmn", {"username": username, "bpmn_xml": bpmn_xml, "timestamp": datetime.datetime.now()})

    return "stored bpmn", 200


