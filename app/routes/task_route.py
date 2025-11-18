from flask import Blueprint,session,redirect,url_for,request, render_template, flash
from app.models import Manager, ErrorMessage, ProfilePic
from app.decorator.auth_decorator import login_required



task_bp = Blueprint("task_bp", __name__)

@task_bp.route("/add_task", methods= ["POST", "GET"])
@login_required
def add_task():
    manager = Manager(ErrorMessage())

    current_user = session["username"]
    all_tasks = manager.get_tasks()
    if "count" not in session:
        session['count'] = 0

    if request.method == "POST":
        task = request.form.get("task").strip()
        all_users = manager.get_users()
        current_user_id = next((user["id"] for user in all_users if user["username"] == session["username"]))

        if task:
            is_exist = any(tasks["task_text"] == task for tasks in all_tasks)

            session["task"] = task if not is_exist else "Please add a different task!, task exist already"
            session["count"] += 1 if not is_exist else 0
            manager.add_task(task, current_user_id)
        return redirect(url_for("task_bp.add_task"))

    message = F"👈🏿 Add a task to crush {current_user}"
    count_task = session['count']
    added_task = session.get("task", None)
    if not added_task:
        added_task = message
            
    return render_template("add-task.html",
                           tasks= added_task,
                           message= message,
                           current_user= current_user,
                           count_task= count_task,
                           default_count= 0,
                           dark_mode= manager.return_dark_mode())



#Route handles view Tasks requests
@task_bp.route("/view_task", methods = ["POST", "GET"])
@login_required
def view_task():
    manager = Manager(ErrorMessage())

    current_user = session.get("username", None)
    all_tasks = manager.get_tasks()
    users = manager.get_users()
    current_user_task = [task for task in all_tasks for user in users if task["user_id"] == user["id"] and user["username"] == current_user ]

    pending_task = [task['task_text'] for task in current_user_task if task['status'] == "pending"]  # Filters only pending tasks
    completed_task = [task['task_text'] for task in current_user_task if task['status'] == "completed"]    # Filters only completed tasks

    return render_template("view-task.html",
                           pending_task= pending_task,
                           completed_task= completed_task,
                           dark_mode= manager.return_dark_mode()
                           )

@task_bp.route("/pending_task", methods= ["POST", "Get"])
@login_required
def pending_task():
    manager = Manager(ErrorMessage())

    current_user = session.get("username", None)
    all_tasks = manager.get_tasks()
    users = manager.get_users()
    current_user_task = [task for task in all_tasks for user in users if task["user_id"] == user["id"] and user["username"] == current_user ]

    pending_tasks = [task for task in current_user_task if task['status'] == "pending"]
    default_message = "No task yet"

    return render_template('pending_tasks.html',
                            pending_tasks= pending_tasks, 
                            message=default_message, 
                            dark_mode= manager.return_dark_mode())

#Route to show completed tasks
@task_bp.route("/completed_task", methods= ["POST", "Get"])
@login_required
def completed_task():
    manager = Manager(ErrorMessage())

    all_tasks = manager.get_tasks()
    users = manager.get_users()
    current_user = next((user for user in users if user["username"] == session["username"]), None)
    current_user_task = [task for task in all_tasks if task["user_id"] == current_user["id"]]

    completed_tasks = [task for task in current_user_task if task['status'] == "completed"]
    default_message = "No task yet"

    return render_template('completed_tasks.html', 
                           completed_tasks= completed_tasks, 
                           message= default_message, 
                           dark_mode= manager.return_dark_mode())


@task_bp.route("/delete_task", methods= ["POST", "GET"])
@login_required
def delete_task():
    manager = Manager(ErrorMessage())

    default_message = "No task yet"

    all_users = manager.get_users()
    all_tasks = manager.get_tasks()

    current_user = [user for user in all_users if user["username"] == session["username"]]
    current_user_tasks = [task for task in all_tasks for user in current_user if task["user_id"] == user["id"]]

    return render_template('delete_task.html', 
                           tasks= current_user_tasks, 
                           message= default_message,
                           dark_mode= manager.return_dark_mode())



@task_bp.route("/delete/<task_id>", methods = ["POST", "GET"])
@login_required
def delete(task_id):
    manager = Manager(ErrorMessage())
    
    if request.method == "POST":
        all_task = manager.get_tasks()
        all_users = manager.get_users()

        current_user = next((user for user in all_users if user["username"] == session["username"]), None)
        current_user_task = [task for task in all_task if int(task["user_id"]) == int(current_user["id"])]
        task_status = next((task["status"] for task in current_user_task if int(task["user_id"]) == int(current_user["id"])), None)
        completed_at = next((task["completed_at"] for task in current_user_task if int(task["user_id"]) == int(current_user["id"])), None)
        print(completed_at)


        deleted_task = next((task["task_text"] for task in current_user_task if task["id"] == int(task_id)), None)
        if deleted_task:
            manager.add_trash("todo_trash",deleted_task, int(current_user["id"]), task_status, completed_at)
            manager.delete_task("todo_tasks", task_id)
        else:
            return "task not found", 404
    return redirect(url_for("task_bp.delete_task")) 


@task_bp.route("/clear_task", methods = ["POST", "GET"])
def clear_task():
    manager = Manager(ErrorMessage())

    all_task = manager.get_tasks()
    all_users = manager.get_users()
    current_user = next((user for user in all_users if user["username"] == session["username"]), None)
    current_user_task = [task for task in all_task if int(task["user_id"]) == int(current_user["id"])]

    default_message = "No task found!"

    if request.method == "POST":
        for task in current_user_task:
            manager.add_trash("todo_trash", task["task_text"], int(task["user_id"]), task["status"], task['completed_at'])
        manager.delete_rows_by_user("todo_tasks", int(current_user["id"]))
        flash('Tasks cleared successfully!.')
        return redirect(url_for("task_bp.clear_task"))
            

    return render_template('clear_task.html',
                            message= default_message, 
                            tasks= current_user_task,
                           dark_mode= manager.return_dark_mode())


@task_bp.route("/restore/<task_id>", methods= ["POST", "GET"])
@login_required
def restore(task_id):
    manager = Manager(ErrorMessage())
    
    if request.method == "POST":
        manager.restore_from_trash("todo_trash", task_id)
    return redirect(url_for("task_bp.trash"))


@task_bp.route("/mark_status", methods= ["POST", "GET"])
@login_required
def mark_status():
    manager = Manager(ErrorMessage())

    all_task = manager.get_tasks()
    all_users = manager.get_users()
    current_user = [user for user in all_users if user["username"] == session["username"]]
    current_user_tasks = [task for task in all_task for user in current_user if task["user_id"] == user["id"]]
    default_message = "No tasks yet!"


    if request.method == "POST":
        for task in current_user_tasks:
            key = f"status_{task['id']}"
            if key in request.form:
                new_status = request.form[key]
                manager.update_task_table("todo_tasks", "status", new_status, "id", int(task['id']))

                if new_status == "completed":
                    if task['status'] != 'completed':
                        manager.update_task_table("todo_tasks", "completed_at", "NOW()", "id", task['id'])
                else:
                    manager.update_task_table("todo_tasks", "completed_at", "still_pending", "id", task['id'])
        return redirect(url_for("user_bp.home"))
                    
    return render_template('mark_as_done.html', 
                           tasks= current_user_tasks, 
                           dark_mode= manager.return_dark_mode,
                           message= default_message)

