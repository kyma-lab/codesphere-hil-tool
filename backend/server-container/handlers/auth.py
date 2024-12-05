from flask_jwt_extended import JWTManager, create_access_token
import bcrypt
import datetime
from datetime import timedelta
from typing import List
import json

from shared.validation import validate_input
from shared.db import insertOne, get_user_passwordhash, get_user_role, delete_user_from_db, get_all_users, clear_database, db_change_password


def handle_login(logger, username, password, jwt):
    """ 
        Logic for the login process is in here. 
        Hashed password is compared against hashed password in the database (bcrypt).
        If the password is correct, a JWT token is created and returned.
        JWT token is valid for 24 hours.
    """
    
    # https://github.com/pyca/bcrypt/
    # https://pypi.org/project/bcrypt/

    
    # Validate the user credentials
    # retrieved password hash from database (if not available, also return 401)
    hashed =  get_user_passwordhash(username)
    

    if hashed is None:
        logger.warning("Login failed: User not found")
        return "Bad username or password", 401, None
    
    role = get_user_role(username)

    # Check that an unhashed password matches one that has previously been hashed
    if bcrypt.checkpw(password.encode(), hashed):
        additional_claims = {"role": role}
        access_token = create_access_token(identity=username, additional_claims=additional_claims, expires_delta=timedelta(hours=24))

        #response.set_cookie('hil_access_token', access_token, httponly=True)
        logger.info(f"Login successful for user: {username}")
        return "Login successful", 200, access_token
    else:
        logger.warning("Login failed: Bad username or password")
        return "Bad username or password", 401, None


def handle_password_change(username, password):
    """ 
        Logic for changing the password for a user.
        Hashed password in the database is replaced with the new hashed password.
        Username is used as primary key.
    """
    
    if not validate_input(username):
        return "Bad username or password", 400
    
    if not validate_input(password):
        return "Bad username or password", 400

    if username is None or password is None:
        return "Bad username or password", 400
    
    # make sure user does not already exist
    pwhash = get_user_passwordhash(username)
    if pwhash is None:
        return "User does not exists", 400
    

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    db_change_password(username, hashed)

    return "Changed password", 200


def handle_logout(jwt_data):
    """ 
        Logic for logging out a user.
        JWT token is added to a blacklist. 
    """
    
    if 'jti' not in jwt_data:
        return "No token found", 400

    token = jwt_data['jti']
    insertOne("blacklisted_tokens", {"jti": token, "keep_until": datetime.datetime.now() + timedelta(hours=24)})

    # add maintenance task to remove old tokens from blacklist
    # todo: check if this is already implemented or not

    return "Logged out", 200