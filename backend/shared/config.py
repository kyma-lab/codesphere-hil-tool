import os

THRESHOLD = int(os.environ.get('THRESHOLD', '10000000'))
TRAINING_QUEUE_LIMIT = int(os.environ.get('TRAINING_QUEUE_LIMIT', '10'))
TRAINING_QUEUE_LIMIT_DURATION = int(os.environ.get('TRAINING_QUEUE_LIMIT_DURATION', '24'))
DISABLE_TRAINING = os.environ.get('DISABLE_TRAINING', 'False') == 'False'

# Disables actual training and prediction, only for testing purposes
TESTING = os.environ.get('TESTING', 'False') == 'True'

# For disbling CORS in production
ALLOW_CORS = os.environ.get('ALLOW_CORS', 'False') == 'True'


BASE_MODELS_PATH = os.environ.get('BASE_MODELS_PATH', 'shared/base-models')
USER_DATA_PATH = os.environ.get('USER_DATA_PATH', 'shared')
BASE_TMP_PATH = os.environ.get('BASE_TMP_PATH', 'shared/tmp')
# global app config variables

JWT_SECRET_KEY = os.environ.get('JWT_SECRET', 'defaultFallbackKey')
ADMIN_USER = os.environ.get('ADMIN_USER', '_defaultFallbackUsername_')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '_defaultFallbackPassword_')

MAX_PDF_COUNT = int(os.environ.get('MAX_PDF_COUNT', '3'))
MAX_PDF_SIZE = int(os.environ.get('MAX_PDF_SIZE', '5')) * 1024 * 1024 # in MB
PDF_EXTRACT_ENGINE = os.environ.get('PDF_EXTRACT_ENGINE', 'tesseract') # pdfminer or tesseract

# has to match with creds specified in docker-compose.yml
MONGO_HOST = os.environ.get('MONGO_HOST', 'mongodb_container')
MONGO_USER = os.environ.get('MONGO_USER', 'root')
MONGO_PWD = os.environ.get('MONGO_PWD', 'rootpassword')

DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'bilstm_crf') # rule-based or bilstm_crf

# Concerning Semantic Search
# Important: this has to be modified manually in : 
# - server-container/handlers/database/esearch.py 
# - server-container/handlers/database/querymodification.py
ELASTIC_HOST = os.environ.get('ELASTIC_HOST', 'https://elastic.simplex.fmi.uni-jena.de')

# Concerning Prediction Worker
SAVE_PREDICTIONS = os.environ.get('SAVE_PREDICTIONS', 'True') == 'True'

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')

FLERT_TRAINING_EPOCHS = int(os.environ.get('FLERT_TRAINING_EPOCHS', '20'))
FLAIR_MAX_EPOCHS = int(os.environ.get('FLAIR_MAX_EPOCHS', '150'))