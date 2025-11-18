from flask import Blueprint, url_for, render_template, request, redirect,session
from app.decorator.auth_decorator import login_required
from app.models import ErrorMessage, Manager


trash_bp = Blueprint("trash_bp", __name__)


@trash_bp.route("/trash", methods = ["POST", "GET"])
@login_required
def trash():
    manager = Manager(ErrorMessage())

    all_trash = manager.get_trash()
    all_user = manager.get_users()
    current_user_trash = [trash for trash in all_trash for user in all_user if trash["user_id"] == user["id"]]
    default_message = "NO trash yet"

    return render_template("trash.html", trash= current_user_trash, message= default_message, dark_mode= manager.return_dark_mode())


@trash_bp.route("/delete_trash/<task_id>", methods = ["POST", "GET"])
@login_required
def delete_trash(task_id):
    manager = Manager(ErrorMessage())


    if request.method == "POST":
        manager.remove_from_trash("todo_trash", task_id)
    return redirect(url_for("trash_bp.trash"))


@trash_bp.route("/delete_all", methods = ["POST", "GET"])

@login_required
def delete_all():
    manager = Manager(ErrorMessage())
    users = manager.get_users()
    current_user = next((user for user in users if user["username"] == session["username"]), None)

    if request.method == "POST": 
        manager.delete_rows_by_user("todo_trash", current_user["id"])
    return redirect(url_for("trash_bp.trash"))


@trash_bp.route("/restore_trash/<task_id>", methods = ["POST", "GET"])
@login_required
def restore_trash(task_id):
    manager = Manager(ErrorMessage())

    if request.method == "POST":
        manager.restore_from_trash(task_id)
    return redirect(url_for("trash_bp.trash"))


@trash_bp.route("/restore_all", methods = ["POST", "GET"])
@login_required
def restore_all():
    manager = Manager(ErrorMessage())
    users = manager.get_users()
    current_user = next((user for user in users if user["username"] == session["username"]), None)

    if request.method == "POST":
        manager.restore_all_trash()
        manager.delete_rows_by_user("todo_trash", current_user["id"])
    return redirect(url_for("trash_bp.trash"))