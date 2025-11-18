from flask import Blueprint, session, request, render_template, redirect,url_for
from app.models import Manager, ErrorMessage, ProfilePic
from app.decorator.auth_decorator import login_required


user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/home", methods= ["POST", "GET"])
@login_required
def home():
    manager = Manager(ErrorMessage())
    
    session.pop('task', None)
    session.pop('count', None)

    error_message = ErrorMessage()
    manager = Manager(error_message)
    dark_mode = manager.return_dark_mode()
    message = "Darkmode" if dark_mode != "enabled" else ""
    users = manager.get_users()
    current_user = next((user for user in users if user["username"] == session["username"]), None)

    return render_template("home.html",
                            user= current_user,
                            dark_mode= dark_mode,
                            message= message
                              )


@user_bp.route("/update_profile_pic", methods=["POST"])
@login_required
def update_profile_pic():
    if "profile-image" not in request.files:
        return {"status": "error", "message": "No file sent"}, 400

    file = request.files["profile-image"]
    profile_pic = ProfilePic()
    profile_pic.save_profile_pic(file)

    return {"status": "ok", "filename": file.filename}




@user_bp.route("/history", methods = ["POST", "GET"])
@login_required
def history():
    manager = Manager(ErrorMessage())

    all_task = manager.get_tasks()
    all_users = manager.get_users()

    current_user = next((user for user in all_users if user["username"] == session["username"]), None)
    current_user_task = [task for task in all_task if task["user_id"] == current_user["id"]]

    return render_template('history.html', 
                           tasks= current_user_task, 
                           dark_mode= manager.return_dark_mode())

    
@user_bp.route("/toggle_mode", methods=["POST"])
@login_required
def toggle_mode():
    data = request.get_json()
    mode = data.get("mode")

    manager = Manager(ErrorMessage())
    manager.update_task_table("todo_users", "darkmode", mode, "username", session["username"])

    return {"status": "ok"}


@user_bp.route("/manage_task", methods= ["POST", "GET"])
def manage_task():
    manager = Manager(ErrorMessage())
    return  render_template("manager.html",
                             dark_mode= manager.return_dark_mode()
                             )
             