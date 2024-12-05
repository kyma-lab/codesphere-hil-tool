import pika
from predict import performPrediction
import os
import time
import json
import torch
from shared.config import TESTING, RABBITMQ_HOST
from shared.utils import (
    most_recent_version, 
    find_correct_modelpath,
    setup_logger
)
from BatchEntityAnalysis import predictWithRules
import datetime


def process_heartbeat(ch, method, properties, body):
    """
    Handles heartbeat requests by acknowledging the message and sending a timestamp back to the response queue.
    Used for the /api/health endpoint to check if any predictor workers are alive.
    """
    print("Acknowledging heartbeat request")

    # Create an acknowledgment timestamp
    ack_time = datetime.datetime.now().isoformat()

    # Send the acknowledgment back to the response queue specified in 'reply_to'
    if properties.reply_to:
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,  # Send response to reply_to queue
            body=ack_time,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id)
        )

    # Acknowledge the original message
    ch.basic_ack(delivery_tag=method.delivery_tag)

def process_prediction_request(ch, method, properties, body):
    """
    Callback function for handling prediction requests.
    Args:
        ch: The channel object for publishing annotated data.
        method: The method object containing delivery information.
        properties: The properties object containing message properties.
        body: The message body containing the payload (most important).
    Returns:
        None
    Raises:
        None
    """

    # declare channel for publishing annotated data
    channel = connection.channel()

    payload = json.loads(body.decode())

    logger.debug(f"Received and decoded prediction request with message payload: {payload}")

    tmpPaths = payload["tmpPaths"]
    userid = payload["userid"]
    random_uuids = payload["random_uuids"]
    modeltype = payload["modeltype"]

    logger.info(f"Received prediction request for {len(random_uuids)} tasks with modeltype {modeltype} and for user {userid}")


    if TESTING:
        time.sleep(5)
        logger.info(f"TESTING MODE enabled: Returning (fake) response for uuids {random_uuids}")
        channel.queue_declare(queue="annotated_data")

        payload = json.dumps({
            "uuid": random_uuid,
            "annotatedData": "testmode"
        })

        channel.basic_publish(
            exchange="",
            routing_key="annotated_data",
            body=payload,
        )


    if modeltype != "bilstm_crf" and modeltype != "rule-based" and modeltype != "xlm_r":
        logger.warning("Aborting: Modeltype not supported")
        return

    annotatedFiles = []

    start_total = time.time()
    for random_uuid, tmpPath in zip(random_uuids, tmpPaths):
        start = time.time()
        ## handle different models, perform actual prediction

        logger.info(f"Computing response for task with uuid {random_uuid}")

        if modeltype == "bilstm_crf":
            latestVersion = most_recent_version(userid, modeltype)
            modelpath = find_correct_modelpath(userid, modeltype, latestVersion)
            annotatedData = performPrediction(tmpPath, modelpath, userid)

        elif modeltype == "rule-based":
        
            annotatedData = predictWithRules(random_uuid, tmpPath)
        elif modeltype == "xlm_r":
            modelpath = "shared/base-models/xlm-r/best-model.pt"
            annotatedData = performPrediction(tmpPath, modelpath, userid)
        else:
            logger.warning("Aborting: Modeltype not supported")
            return
        
        end = time.time()
        logger.info(f"Prediction for task with uuid {random_uuid} took {end - start} seconds")

        annotatedFiles.append(annotatedData)

    end_total = time.time()
    logger.info(f"Total prediction time for {len(random_uuids)} tasks: {end_total - start_total} seconds")

    
    # validate if annotatedFiles has same length as uuids
    if len(annotatedFiles) != len(random_uuids):
        logger.warning("Number of results does not equal number of tasks received")


    # publish annotated data
    channel.queue_declare(queue="annotated_data")
    logger.info(f"Sending RabbitMQ response for task uuids {random_uuids}")

    payload = json.dumps({
        "random_uuids": random_uuids,
        "annotatedFiles": annotatedFiles
    })

    channel.basic_publish(
        exchange="",
        routing_key="annotated_data",
        body=payload,
    )

    for random_uuid in random_uuids:
        # delete content of tmp directory
        if os.path.exists(f"shared/tmp/{random_uuid}"):
            os.remove(f"shared/tmp/{random_uuid}/test.txt")
            os.remove(f"shared/tmp/{random_uuid}/train.txt")
            os.remove(f"shared/tmp/{random_uuid}/dev.txt")
            os.rmdir(f"shared/tmp/{random_uuid}")
    logger.debug(f"Deleted temporary files for tasks with uuids {random_uuids}")

    ch.basic_ack(delivery_tag=method.delivery_tag)



# Constants
PREDICTION_QUEUE = "prediction"
HEARTBEAT_QUEUE = "heartbeat_predictor"
LOG_FILE_PATH = './shared/logs/predictor.log'
MAX_RETRIES = 10

# Global variables
connection = None
logger = None

def setup_logging():
    global logger
    logger = setup_logger('predictor', LOG_FILE_PATH)
    logger.info('Starting prediction worker...')

def connect_to_rabbitmq():
    global connection
    for i in range(MAX_RETRIES):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        except pika.exceptions.AMQPConnectionError:
            logger.info(f"Failed to connect to RabbitMQ. Retrying... ({i + 1}/{MAX_RETRIES})")
            if i < MAX_RETRIES - 1:  # i is zero indexed
                time.sleep(10)  # wait for 10 seconds before trying to reconnect
            else:
                raise

def setup_channel():
    global connection
    channel = connection.channel()
    channel.queue_declare(queue=PREDICTION_QUEUE)
    channel.queue_declare(queue=HEARTBEAT_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    return channel

def start_consuming(channel):
    global connection
    channel.basic_consume(queue=PREDICTION_QUEUE, on_message_callback=process_prediction_request)
    channel.basic_consume(queue=HEARTBEAT_QUEUE, on_message_callback=process_heartbeat)
    channel.start_consuming()


def gpu_check():
    if torch.cuda.is_available():
        print("GPU is available.")
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Number of available GPUs: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
            print(f"Memory Allocated: {torch.cuda.memory_allocated(i)} bytes")
            print(f"Memory Cached: {torch.cuda.memory_reserved(i)} bytes")
    else:
        print("GPU is not available.")

def main():

    gpu_check()

    setup_logging()
    connect_to_rabbitmq()
    logger.info('Prediction worker is connected and ready to process prediction requests.')
    channel = setup_channel()
    start_consuming(channel)

if __name__ == "__main__":
    main()
