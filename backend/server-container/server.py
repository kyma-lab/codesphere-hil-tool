from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# code shared across multiple containers
from shared.utils import setup_logger, sanitize_input

# for authentication
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt

# environment variables and databae access function
from shared.db import db_check_if_token_blacklisted
from shared.config import JWT_SECRET_KEY, ADMIN_USER, ADMIN_PASSWORD, MAX_PDF_COUNT, MAX_PDF_SIZE, PDF_EXTRACT_ENGINE, DEFAULT_MODEL, RABBITMQ_HOST, USER_DATA_PATH, ALLOW_CORS, DISABLE_TRAINING
import functools
import json

# code to handle endpoint requests
from handlers.other import clear_rabbitmq_handler, server_health_handler, reset_mongodb_handler, handle_prediction_request, upload_handler, handle_contribution, handle_bpmn_save
from handlers.auth import handle_login, handle_logout, handle_password_change
from handlers.users import add_user_handler, get_users_handler, delete_user_handler, assert_initial_state
from handlers.search import handle_search, handle_semantic_search
from handlers.logs import handle_get_logs

##################################################################3
############## INITIALIZE THE SERVER ##############################
##################################################################3

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
jwt = JWTManager(app)
logger = setup_logger('server', './shared/logs/server.log')
logger.info('Starting the server...')

# this is just for logging the current config, not used to access the properties
config = {
    "JWT_SECRET_KEY": JWT_SECRET_KEY,
    "ADMIN_USER": ADMIN_USER,
    "ADMIN_PASSWORD": ADMIN_PASSWORD,
    "MAX_PDF_COUNT": MAX_PDF_COUNT,
    "MAX_PDF_SIZE": MAX_PDF_SIZE,
    "PDF_EXTRACT_ENGINE": PDF_EXTRACT_ENGINE,
    "DEFAULT_MODEL": DEFAULT_MODEL,
    "RABBITMQ_HOST": RABBITMQ_HOST,
    "USER_DATA_PATH": USER_DATA_PATH,
    "ALLOW_CORS": ALLOW_CORS,
    "DISABLE_TRAINING": DISABLE_TRAINING
}

for key, value in config.items():
    logger.info(f"{key}: {value}")

#! disable CORS (disallow Cross Origin Resource Sharing in production)
if ALLOW_CORS:
    #CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['DEBUG'] = True
    logger.info("CORS enabled (development mode)")
else:
    logger.info("CORS disabled (production mode)")

# Register initial user (admin)
assert_initial_state(logger)

##################################################################3
############## ROUTE HANDLER MODIFIER #############################
##################################################################3

def admin_required(fn):
    """
    Decorator function that checks if the user has the 'admin' role.
    If the user does not have the 'admin' role, it returns a JSON response with a 401 Unauthorized status code.
    Otherwise, it calls the decorated function.

    Args:
        fn (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """
    ...
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims['role'] != 'admin':
            return jsonify({"msg": "Unauthorized"}), 401
        else:
            return fn(*args, **kwargs)
    return wrapper

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    """
    Check if the JWT token is in the blocklist.
    Does not have to be called explicitly, it is called by the JWTManager.

    Parameters:
    - jwt_header (dict): The header of the JWT token.
    - jwt_payload (dict): The payload of the JWT token.

    Returns:
    - bool: True if the token is blacklisted, False otherwise.
    """
    jti = jwt_payload['jti']
    is_blacklisted = db_check_if_token_blacklisted(jti)
    logger.debug(f"Checking if jwt token is still valid (not blacklisted): {not is_blacklisted}")
    return is_blacklisted 


##################################################################3
############## ROUTES #############################################
##################################################################3

@app.route('/api/delete_user', methods=['POST'])
@admin_required
def delete_user():
    """
    Delete a user from the server.
    Note: Already provided auth tokens will still be valid until it expires.

    Parameters:
    - username (str): The username of the user to be deleted.

    Returns:
    - str: The result of the delete operation.

    Raises:
    - Exception: If there is an error during the delete operation.
    """
    username = sanitize_input(request.json.get('username', None))
    return delete_user_handler(logger, username)


@app.route('/api/get_users', methods=['GET'])
@admin_required
def get_users():
    """
    Get list of users from the server.
    Those are the users that can login to the system.

    Returns:
        A JSON response containing the list of users and a status code.
    """
    users = get_users_handler()
    return jsonify({"users": users}), 200


@app.route('/api/health', methods=['GET'])
def check_server_health():
    """
    Endpoint to check the health status of the server.

    This endpoint handles GET requests to '/api/health' and returns the health status
    of various components of the server, including the predictor, trainer, bilstm-crf,
    and xlm-r model.

    Returns:
        Response: A JSON response containing the health status of the server components.
    """
    status = server_health_handler(logger)
    return jsonify({"system_status" : status}), 200


@app.route('/api/reset_rabbitmq', methods=['POST'])
@admin_required
def clear_rabbitmq():
    """
    Clears all pending tasks in the RabbitMQ server.
    This can disrupt the normal operation by causing an invalid state.
    Sometimes the docker-compose has to be restarted afterwards.

    Returns:
        str: (?)
    """
    logger.info("Received POST request on /api/reset_rabbitmq")
    return clear_rabbitmq_handler(logger)


@app.route('/api/reset_mongodb', methods=['POST'])
@admin_required
def reset_mongodb():
    """
    Clears all stored data for all users and delets their accounts.
    Only the admin-account will be kept.

    Returns:
        str: (?)
    """
    logger.info("Received POST request on /api/reset_mongodb")
    return reset_mongodb_handler(logger)


@app.route('/api/add_user', methods=['POST'])
@admin_required
def add_user():
    """
    Endpoint handles POST requests to add a new user to the system.
    The request should include the username and password of the user to be added.
    The user will be assigned the role of "user" by default.
    Minimal input sanitization + validation is performed.
    Usernames have to be unique.

    Returns:
        A JSON response containing a message and a status code.
    """
    logger.info("Received POST request on /api/add_user")
    username = sanitize_input(request.json.get('username', None))
    password = sanitize_input(request.json.get('password', None))
    role = "user"
    msg, code = add_user_handler(logger, username, password, role)
    return jsonify({"msg": msg}), code



@app.route('/api/logs', methods=['GET'])
@admin_required
def get_logs():
    """
    Endpoint that provides the most recent logs available for the server, trainer, and predictor.
    Reads the last 500 lines of the log files and returns them as a JSON response.
    Uses html.escape to prevent XSS attacks.

    Returns:
        A JSON response containing the logs and the status code.
    """
    logs, status = handle_get_logs()
    return jsonify({"logs": logs}), status


# temporary endpoint for conducting the study
@app.route('/api/bpmn', methods=['POST'])
@jwt_required()
def save_bpmn():
    """
    Endpoint that was relevant for the studyy.
    Here the BPMN XML created by the participants was saved to the database.

    Returns:
        A JSON response containing a message and a status code.
    """
    return jsonify({"msg": "This endpoint is disabled"}), 400

    bpmn_xml = sanitize_input(request.json.get('bpmn_xml', None))
    username = get_jwt_identity()
    msg, status = handle_bpmn_save(bpmn_xml, username)
    return jsonify({"msg": msg}), status

@app.route('/api/change_password', methods=['POST'])
@admin_required
def change_password():
    """
    Endpoint where the admin user can change the password of other users.
    Requires the username of the account whose password is to be changed, and
    the new password. The password is hashed using bcrypt before storing it in the database.

    Returns:
        A JSON response containing a message and a status code.
    """
    logger.info("Received POST request on /api/change_password")
    username = sanitize_input(request.json.get('username', None))
    password = sanitize_input(request.json.get('password', None))
    msg, status = handle_password_change(username, password)
    return jsonify({"msg": msg}), status


@app.route('/api/login', methods=['POST'])
def login():
    """
    Call here provides a valid JWT token if the login credentials are correct.
    The JWT token is required for accessing the other endpoints.
    It is valid for 24 hours.

    Parameters:
    - None

    Returns:
    - msg (str): The message indicating the result of the login attempt.
    - access_token (str): The access token generated upon successful login.

    Raises:
    - None
    """
    logger.info("Received POST request on /api/login")
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    msg, status, access_code = handle_login(logger, username, password, jwt)
    return jsonify({"msg": msg, "access_token": access_code}), status


@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Call here with a JWT token in the header invalidates the token by adding it to the blacklist.
    This is common practice for JWT tokens.

    Returns:
        dict: A dictionary containing the logout message.
        int: The HTTP status code.
    """
    jwt_data = get_jwt()
    msg, status = handle_logout(jwt_data)
    return jsonify({"msg": msg}), status

@app.route("/api/extract", methods=["POST"])
@jwt_required()
def upload():
    """
    Endpoint where PDFs can be posted to. The server will extract the text from the PDFs with OCR.
    Other methods for text extraction can be configured in the config file

    Returns a JSON response containing the message, extracted texts, and filenames.

    Parameters:
    - files: the PDF files to be processed (not a real parameter, but part of the request object)
    - content_length: The content length of the request (header, automatically added by the browser)

    # Note: The file size validation is NOT secure. It is only a basic check.

    Returns:
    - A JSON response containing the message, extracted texts, and filenames.
    """
    files = request.files
    content_length = request.headers.get('Content-Length')
    msg, status, container = upload_handler(logger, files, content_length)
    # very messy due to refactor
    return jsonify({"msg": msg, "texts": container["texts"], "filenames": container["filenames"]}), status


@app.route("/api/getpredictions", methods=["POST"])
@jwt_required()
def getpredictionss():
    """
    Endpoint for retrieving predictions. 
    Requires userid, the text data, and the model to be used for making predictions.
    It requires a valid JWT token for authentication.

    Parameters:
    - data (dict): JSON data containing the necessary information for making predictions.

    Returns:
    - msg (str): A message indicating the status of the prediction request.
    - files (list): The annotated files in IOB format
    - status (int): The HTTP status code.
    """
    logger.info("Received POST request on /api/getpredictions")
    data = request.get_json()
    userid = get_jwt_identity()
    msg, status, container = handle_prediction_request(logger, data, userid)
    # very messy due to refactor
    return jsonify({"msg": msg, "files": container["files"]}), status


@app.route("/api/contribute", methods=["POST"])
@jwt_required()
def process_contribution():
    """
    Endpoint where users can post the annotated data after they modified it.
    This automatically happens when proceeding to the bpmn-editor view (confirming annotations).
    The collected data is used to train the model once enough data is collected.
    This is disabled if training is disabled. It requires a valid JWT token for authentication.

    Parameters:
    - data (dict): JSON data containing the necessary information for making predictions.

    Returns:
    - msg (str): A message indicating the status of the contribution request.
    - status (int): The HTTP status code.
    """
    logger.info("Received POST request on /api/contribute")
    data = request.get_json()
    userid = get_jwt_identity()
    msg, status = handle_contribution(logger, data, userid)
    return jsonify({"msg": msg}), status


@app.route("/api/search/", methods=["GET"])
@jwt_required()
def search():
    """
    Endpoint that receives seach queries and performs a regular search.
    Requires elastic / kibana server that was set up beforehand.

    Returns:
        A JSON response containing a message, a list of search result objects and a status code.
    """
    # NOTE: currently untested after refactor, might be broken
    logger.info("Received GET request on /api/search")
    query = request.args.get("query")
    msg, status, results = handle_search(logger, query)
    # this refactor broke the functionality due to parameter name change (msg did not exist before and it was just the results list)
    # so one layer less in the response
    return jsonify({"msg": msg, "results": results}), status


@app.route("/api/search_semantic/", methods=["GET"])
@jwt_required()
def search_semantic():
    """
    Endpoint that receives seach queries and performs a semantic search.
    Requires elastic / kibana server that was set up beforehand.

    Returns:
        A JSON response containing a message, a list of search result objects and a status code.
    """
    # NOTE: currently untested after refactor, might be broken
    logger.info("Received GET request on /api/search_semantic")
    query = request.args.get("query")
    msg, status, results = handle_semantic_search(logger, query)
    # this refactor broke the functionality due to parameter name change (msg did not exist before and it was just the results list)
    # so one layer less in the response
    return jsonify({"msg": msg, "results": results}), status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8070, debug=True)
