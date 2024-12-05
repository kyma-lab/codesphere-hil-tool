import pika
import time
from datetime import datetime, timezone
import concurrent.futures
import os
from train_flert import trainTransformer
from train_bilstm import trainBILSTM
from shared.config import TESTING, TRAINING_QUEUE_LIMIT, USER_DATA_PATH, BASE_MODELS_PATH, RABBITMQ_HOST
from shared.db import get_train_queue_count

from shared.utils import (
    append_to_train_queue,
    check_path_exists,
    check_data_sufficient,
    get_interval_to_train_on,
    create_temp_training_data,
    make_sure_folder_exists,
    mark_data_as_processed,
    most_recent_version,
    setup_logger
)


def process_heartbeat(ch, method, properties, body):
    """
    Handles heartbeat requests by acknowledging the message and sending a timestamp back to the response queue.
    Used for the /api/health endpoint to check if any predictor workers are alive.
    """
    print("Acknowledging heartbeat request")

    # Create an acknowledgment timestamp
    ack_time = datetime.now().isoformat()

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


def train(modeltype: str, userid: str, current_version: int, rand_uuid: str):
    """
    Train the model. Handles both BILSTM and FLERT models.
    Uses the base model if the current version is 0 (no previously trained model exists).
    Args:
        modeltype (str): The type of the model to train.
        userid (str): The user ID.
        current_version (int): The current version of the model.
        rand_uuid (str): The random UUID.
    Returns:
        bool: True if the model improved, False otherwise.
    """

    logger.debug(f"called train with modeltype {modeltype}, userid {userid}, current_version {current_version}, rand_uuid {rand_uuid}")

    if current_version == 0:
        logger.info("No existing model found. Training from scratch/base.")
        existing_model = False
        existing_model_path = None
    else:
        logger.info("Existing model found. Using it as starting point.")
        existing_model = True
        existing_model_pathv1 = f"{USER_DATA_PATH}/data_{userid}/trained_models/{modeltype}/model_{current_version}/final-model.pt"
        existing_model_pathv2 = f"{USER_DATA_PATH}/data_{userid}/trained_models/{modeltype}/model_{current_version}/best-model.pt"

        if check_path_exists(existing_model_pathv1):
            existing_model_path = existing_model_pathv1
        elif check_path_exists(existing_model_pathv2):
            existing_model_path = existing_model_pathv2
        else:
            logger.error("No model found, but there should be one. Code 101.")

    logger.info(f"Determined model path: {existing_model_path}")

    datapath = f"{USER_DATA_PATH}/data_{userid}/{rand_uuid}"
    logger.debug(f"datapath: {datapath}")

    outputpath = f"{USER_DATA_PATH}/data_{userid}/trained_models/{modeltype}/model_{current_version + 1}"
    logger.debug(f"outputpath: {outputpath}")


    logger.info(f"Training parameters: {modeltype}, {datapath}, {outputpath}, {existing_model}")

    # its not good to have different keywords here than in the prediction (XLM-R, BILSTM)
    # and its not good to have that as string in general
    if modeltype == "bilstm_crf":
        logger.info("Started training BILSTM model.")
        report = trainBILSTM(
            datapath,
            outputpath,
            existing_model,
            existing_model_path,
        )
    elif modeltype == "flert":
        logger.info("Started training FLERT model.")
        report = trainTransformer(
            datapath,
            outputpath,
            existing_model,
            existing_model_path,
        )
    else:
        logger.error("Model type not supported.")
        return
    

    # TODO: check if the model improved, return False if not
    csvrow = csvrow = [
        str(datetime.now(timezone.utc).isoformat()) + " UTC", 
        modeltype,
        userid,
        round(report['macro avg']['f1-score'],4),
        round(report['macro avg']['precision'],4), 
        round(report['macro avg']['recall'],4), 
        round(report['micro avg']['f1-score'],4), 
        round(report['micro avg']['precision'],4), 
        round(report['micro avg']['recall'],4)
        ]
    csvrow = [str(x) for x in csvrow]
    csvrow = ','.join(csvrow)

    with open(f'{BASE_MODELS_PATH}/training_log.csv','a') as fd:
        fd.write(csvrow + "\n")

    logger.info(f"Training finished. Model micro f1-score: {report['micro avg']['f1-score']}")

    # TODO: compare rep['micro avg']['f1-score]' with some value from the database (last value)

    return True


def check_new_training_possible(userid: str, modeltype: str):
    """
    Checks if a new training is possible for the given user ID and model type.
    Based on the number of available annotated tokens and the rate limit.
    Args:
        userid (str): The ID of the user.
        modeltype (str): The type of the model.
    Returns:
        None: If there are too many training tasks in the queue.
    """

    logger.info(
        f"Starting check of training possibility"
        f" for user {userid}"
        f" and model {modeltype}"
    )

    dataStart, dataStop = get_interval_to_train_on(userid, modeltype)
    logger.debug(f"Determined data interval to train on: {dataStart} - {dataStop}")

    dataSufficient = check_data_sufficient(userid, dataStart, dataStop)

    logger.debug(f"Sufficient new data for training is available: {dataSufficient}")

    # verify rate limit
    count = get_train_queue_count(userid)
    logger.info(f"User {userid} sent {count} training tasks to queue in last 24 hours.")

    if count > TRAINING_QUEUE_LIMIT:
        logger.warning(f"Not checking if training is possible because rate-limit for training is exceeded.")
        return

    if dataSufficient:

        # add entry (keep track, for rate limit)
        append_to_train_queue(userid)
        logger.debug(f"Added pending task to rate-limit tracker for user: {userid}")

        # if we are already currently finetuning
        # we wait until it is done before we start another one
        # we need to previous finished model to improve it (build on top of it)

        logger.info(f"New training possible for user {userid} and model {modeltype}. Preparing...")


        # this also places the test and dev data (whichever is desired)
        rand_uuid = create_temp_training_data(userid, dataStart, dataStop)


        make_sure_folder_exists(USER_DATA_PATH + f"/data_{userid}/trained_models")
        curr_version = most_recent_version(userid, modeltype)

        logger.info(f"Starting fine tuning thread for user {userid} and model {modeltype}, current version: {curr_version}")
    
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(train, modeltype, userid, curr_version, rand_uuid)
            model_improved = future.result()
    
        if not model_improved:
            logger.info("Newly trained model did not improve (but previous model is still overwritten).")
            # TODO: what to do now?
            pass

        # mark data used for fine-tuning as processed so its not used again
        mark_data_as_processed(userid, modeltype, dataStop)

        # delete temporary training data file if they exist
        if os.path.exists(USER_DATA_PATH + f"/data_{userid}/{rand_uuid}"):
            os.remove(USER_DATA_PATH + f"/data_{userid}/{rand_uuid}/test.txt")
            os.remove(USER_DATA_PATH + f"/data_{userid}/{rand_uuid}/train.txt")
            os.remove(USER_DATA_PATH + f"/data_{userid}/{rand_uuid}/dev.txt")
            os.rmdir(USER_DATA_PATH + f"/data_{userid}/{rand_uuid}")

    else:
        logger.info(f"New training not possible for user {userid} and model {modeltype}.")


def process_training_request(ch, method, properties, body):
    # parse message body
    user_id_cookie, modeltype = body.decode().split(",")

    # perform long-running task
    if TESTING:
        logger.info(f"TESTING MODE enabled: dummy training timeout for 120 seconds")
        time.sleep(120)
    else:
        logger.info(f"Training task received for user {user_id_cookie} and model {modeltype}")
        check_new_training_possible(user_id_cookie, modeltype)

    # acknowledge message
    ch.basic_ack(delivery_tag=method.delivery_tag)



# Constants
PREDICTION_QUEUE = "new_training"
HEARTBEAT_QUEUE = "heartbeat_trainer"
LOG_FILE_PATH = './shared/logs/trainer.log'
MAX_RETRIES = 10

# Global variables
connection = None
logger = None

def setup_logging():
    global logger
    logger = setup_logger('predictor', LOG_FILE_PATH)
    logger.info('Starting training worker...')

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
    channel.basic_consume(queue=PREDICTION_QUEUE, on_message_callback=process_training_request)
    channel.basic_consume(queue=HEARTBEAT_QUEUE, on_message_callback=process_heartbeat)
    channel.start_consuming()


def main():
    setup_logging()
    connect_to_rabbitmq()
    logger.info('Training worker is connected and ready to process training requests.')
    channel = setup_channel()
    start_consuming(channel)

if __name__ == "__main__":
    main()
