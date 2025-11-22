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
            print(f"{e}")

        except MySQLdb.ProgrammingError as e:
            args[0].error.set_error(programmingErr=f"Programming error: {e}")
            print(f"{e}")

        except KeyError as e:
            args[0].error.set_error(keyErr=f"Key error: {e}")
            print(f"{e}")

        except Exception as e:
            args[0].error.set_error(exceptionErr=f"Unexpected error: {e}")
            print(f"{e}")

        finally:
            mysql.connection.commit()

    return wrapper
