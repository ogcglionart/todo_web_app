from flask import redirect, url_for,session, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app import mysql
from app.decorator.error_decorator import db_error_handler
from setup_db import get_cursor
import MySQLdb
from typing import Any
import os



class ErrorMessage:
    def __init__(self):
        self.errors ={
            "integrityErr": "",
            "programmingErr": "",
            "exceptionErr": "",
            "keyErr": "",
            "noTextErr": "",
            "userNotFoundErr": "",
            "invalidInput": "",
            "userAlreadyExistErr": "",
            "taskAlreadyExistErr": ""
        }

    def set_error(self, **kwarg ):
        for key, value in kwarg.items():
            if key in self.errors:
                self.errors[key] = value
        
    def get_error(self) -> Any:
        return next((err for err in self.errors.values() if err != ""), "")
    
    def integrity_err(errCode: int, e) -> str:
        err_code = errCode
        if err_code == 1062:
            return "Username already exists. Please choose another one."
        elif err_code == 1452:
            return "The referenced user does not exist."
        elif err_code == 1048:
            return "A required field is missing."
        else:
            return f"Database integrity error: {e}"


class Manager:
    def __init__(self, error: ErrorMessage = ""):
        self.error = error 
        self.password = None
        self.username = None
        self.task_text = None
        self.feedback_text = None

        
    @staticmethod
    def check_in_session():
        if "username" in session:
            return redirect(url_for('user_bp.home'))
    @staticmethod
    def check_not_in_session():
        if "username" not in session:
            return redirect(url_for("auth_bp.login"))


    @db_error_handler
    def add_users(self,username, password):
        self.username = username
        self.password = password
        cursor = get_cursor()
        cursor.execute("INSERT INTO todo_users (username, password) VALUES (%s, %s)", (self.username, self.password))
        cursor.close()
        mysql.connection.commit()


    @staticmethod
    def get_users():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM todo_users")
        users = cursor.fetchall()
        cursor.close()
        mysql.connection.commit()
        return users
    
    @db_error_handler
    def update_task_table(self, table: str, to_update: str, setupdate: str, condition: str, set_condition):
        cursor = get_cursor()

        if setupdate == "NOW()":
            query = f"UPDATE {table} SET {to_update} = NOW() WHERE {condition} = %s"
            cursor.execute(query, (set_condition,))

        else:
            query = f"UPDATE {table} SET {to_update} = %s WHERE {condition} = %s"
            cursor.execute(query, (setupdate, set_condition))

        cursor.close()
        mysql.connection.commit()
        

    @db_error_handler
    def delete_task(self, table: str, task_id: int):
        cursor = get_cursor()
        cursor.execute(F"DELETE FROM {table} WHERE id= %s", (task_id,))
        cursor.close()
        mysql.connection.commit()

    @db_error_handler
    def delete_user(self, table: str, username: str):
        cursor = get_cursor()
        cursor.execute(F"DELETE FROM {table} WHERE username= %s", (username,))
        cursor.close()
        mysql.connection.commit()

    
    def login_users(self,username, password):
        username = username
        password = password
        all_users = self.get_users()

        if username and password:
            for user in all_users:
                if user["username"] == username and check_password_hash(user["password"], password):
                    session["username"] = username
                    break
                self.error.set_error(invalidInput= "invalid Username or Password")
        else:
            self.error.set_error(invalidInput= "Enter Username and Password")
    
    
    @db_error_handler
    def add_task(self,text, user_id, status= "pending", completed_at="still_pending" ):
        cursor = get_cursor()
        user_id = user_id
        self.task_text = text

        all_tasks = self.get_tasks()

        if not self.task_text:
            self.error.set_error(noTextFound= "please enter a task")
            return

        is_exist = any(task["task_text"] == self.task_text for task in all_tasks)

        if is_exist:
            self.error.set_error(taskAlreadyExistErr = "Task exits already! you can edit tasks in the edit menu")
        else:
            cursor.execute("INSERT INTO todo_tasks (user_id, task_text, status, completed_at) VALUES (%s, %s, %s, %s)", (user_id, self.task_text, status, completed_at))
            cursor.close()
            mysql.connection.commit()
        


    @db_error_handler
    def get_tasks(self):
        cursor = get_cursor()
        cursor.execute("SELECT * FROM todo_tasks")
        tasks = cursor.fetchall()
        cursor.close()
        mysql.connection.commit()
        return tasks
    
    @db_error_handler
    def get_trash(self):
        cursor = get_cursor()
        cursor.execute("SELECT * FROM todo_trash")
        trash = cursor.fetchall()
        cursor.close()
        mysql.connection.commit()
        return trash
    

    @db_error_handler
    def add_trash(self, table: str,  trash_task: str, user_id, status= "pending", completed_at = "still_pending"):
        text = trash_task
        if text:
            cursor = get_cursor()
            cursor.execute(f"INSERT INTO {table} (task_text, user_id, status, completed_at) VALUES ( %s, %s, %s, %s)", (text, user_id, status, completed_at))
            cursor.close()
            mysql.connection.commit()


    @db_error_handler
    def remove_from_trash(self,table: str, task_id: int):
        cursor = get_cursor()
        cursor.execute(f"DELETE FROM {table} WHERE id= %s", (task_id,))
        cursor.close()
        mysql.connection.commit()

    @db_error_handler
    def restore_from_trash(self,task_id):
        cursor = get_cursor()
        all_trash = self.get_trash()
        all_user = self.get_users()

        current_user = next((user for user in all_user if user["username"] == session["username"]))
        current_user_trash = [trash for trash in all_trash if trash["user_id"] == current_user["id"]]

        user_id_for_trash = next((trash["user_id"] for trash in current_user_trash if trash["id"] == int(task_id)), None)
        restored_trash = next((trash["task_text"] for trash in current_user_trash if trash["id"] == int(task_id)), None)
        status = next((trash["status"] for trash in current_user_trash if trash["id"] == int(task_id)), None)
        completed_at = next((trash["completed_at"] for trash in current_user_trash if trash["id"] == int(task_id)), None)

        self.add_task(restored_trash, user_id_for_trash, status, completed_at)
        self.remove_from_trash("todo_trash", task_id)
        cursor.close()
        mysql.connection.commit()


    @db_error_handler
    def restore_all_trash(self):
        all_trash = self.get_trash()
        all_user = self.get_users()

        current_user = [user for user in all_user if user["username"] == session["username"]]
        current_user_trash = [trash for trash in all_trash if trash["user_id"] == current_user[0]["id"]]

        for task in current_user_trash:
            self.add_task(task["task_text"], task["user_id"], task["status"], task["completed_at"])


    @db_error_handler
    def delete_rows_by_user(self, table: str, user_id: int):
        cursor = get_cursor()
        query = f"DELETE FROM {table} WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        cursor.close()
        mysql.connection.commit()


    @db_error_handler
    def add_feedbacks(self,texts):
        feedback_text = texts
        cursor = get_cursor()
        if feedback_text:
            cursor.execute(F"INSERT INTO todo_feedback {texts} VALUES (%s)", (feedback_text))
            cursor.close()
            mysql.connection.commit()
        else:
            self.error.set_error(invalidInput = "Enter a valid message to send feedback")

    def return_dark_mode(self):
        users = self.get_users()
        current_user = session["username"]
        for user in users:
            if user["username"] == current_user:
                return "enabled" if user["darkmode"] == "enabled" else ""
            
    def toggle_mode(self):
        users = self.get_users()

        for user in users:
            if user["username"] == session["username"]:
                mode = "enabled" if user["darkmode"] != "enabled" else "disabled"
                self.update_task_table("todo_users", "darkmode", mode, "username", user["username"])
                return {"status": "ok"}

            

class ProfilePic:
    def __init__(self):
        self.error = ErrorMessage()
        self.manager = Manager(self.error)
        self.allowed_extensions = {"png", "jpeg", "jpg", "webp"}
    
    def allowed_file(self,filename):
        return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in self.allowed_extensions
        
    @db_error_handler    
    def save_profile_pic(self, file):
        UPLOAD_FOLDER = os.path.join(current_app.root_path, 'static', 'uploads')
        current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        username = session["username"]
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        self.manager.update_task_table("todo_users", "profilepic", filename, "username", username)
        
        


