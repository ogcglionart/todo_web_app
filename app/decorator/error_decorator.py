import MySQLdb
from app import mysql
from functools import wraps



def db_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MySQLdb.IntegrityError as e:
            args[0].error.set_error(integrityErr=f"Integrity error: {e}")

        except MySQLdb.ProgrammingError as e:
            args[0].error.set_error(programmingErr=f"Programming error: {e}")

        except KeyError as e:
            args[0].error.set_error(keyErr=f"Key error: {e}")

        except Exception as e:
            args[0].error.set_error(exceptionErr=f"Unexpected error: {e}")

        finally:
            mysql.connection.commit()

    return wrapper
