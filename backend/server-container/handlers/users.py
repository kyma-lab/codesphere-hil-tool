import bcrypt
import json

from shared.db import insertOne, get_user_passwordhash, get_user_role, delete_user_from_db, get_all_users, clear_database, db_change_password
from shared.config import ADMIN_USER, ADMIN_PASSWORD
from shared.validation import validate_input

def assert_initial_state(logger):
    """ 
        Makes sure that the default admin user exists.
    """
    
    # check if the user ADMIN_USER exists
    pwhash = get_user_passwordhash(ADMIN_USER)

    # check if the user ADMIN_USER has role admin
    role = get_user_role(ADMIN_USER)

    # by default, reset admin pw on every start
    resetAdmin = True

    if (resetAdmin) or (pwhash is None) or (role != "admin"):
        logger.info("Resetting admin user.")
        delete_user_from_db(ADMIN_USER)
        register_user(logger, ADMIN_USER, ADMIN_PASSWORD, "admin")
    else:
        logger.info("Admin user exists.")


def register_user(logger, username, password, role="user"):
    """ 
        Logic for registering a new user.
        Password is hashed using bcrypt and stored in the database.
        Usernames function as primary keys, have to be unique.
    """
    
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    pwhash = None
    pwhash = get_user_passwordhash(username)

    if pwhash is None:
        insertOne("users", {"username": username, "password_hash": hashed, "role": role})
    else:
        logger.info("User already exists, not registering")

def add_user_handler(logger, username, password, role):
    """ 
        Handler that exposes the register_user function as API endpoint.
        Wraps the register_user function with feedback for the webclient.
    """
    
    if not validate_input(username):
        return "Bad username", 400
    
    if not validate_input(password):
        return "Bad password", 400

    if not validate_input(role):
        return "Bad role", 400

    # make sure user does not already exist
    pwhash = get_user_passwordhash(username)
    if pwhash is not None:
        return "User already exists", 400

    register_user(logger, username, password, role)

    return "User added", 200

def get_users_handler():
    """ 
        Handler that exposes the get_all_users function as API endpoint.
        Returns all users in the database.
    """
    
    users = get_all_users()
    return users


def delete_user_handler(logger, username):
    """
    Handler that exposes the delete_user function as API endpoint.
    Deletes a user from the database. Username is used as primary key.
    Users with the role "admin" cannot be deleted.

    Args:
        logger (Logger): The logger object for logging messages.
        username (str): The username of the user to be deleted.

    Returns:
        str: A message indicating the result of the deletion operation.

    Raises:
        None
    """
    logger.info(f"Attempting to delete user: {username}")

    if username is None:
        return "Bad username", 400
    
    # abort if user already exists
    role = get_user_role(username)
    if role is None:
       return "Bad username", 400
    
    logger.info(f"User {username} has role: {role}")
    
    # do not allow deletion of admin
    if role == "admin":
        logger.warning("Cannot delete admin")
        return "Cannot delete admin", 400
    
    logger.info(f"Deleting user: {username}")
    ok = delete_user_from_db(username)

    if not ok:
        return "User not found", 400

    return "User deleted", 200