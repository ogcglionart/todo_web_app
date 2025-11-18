from flask import Blueprint, jsonify, session, redirect, render_template,url_for, request, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import Manager, ErrorMessage
from app.decorator.auth_decorator import login_required, validate_password_strength


auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for("auth_bp.login"))


@auth_bp.route('/signup', methods = ['GET', 'POST'])
@validate_password_strength
def signup():
    if "username" in session:
        return redirect(url_for("user_bp.home"))
    
    error_message = ErrorMessage()
    manager = Manager(error_message)
    
    signed_up_users = manager.get_users()
    
    if request.method == "POST":
        username = request.form.get("user_name").strip()
        password = request.form.get("password").strip()        
        hashed_password = generate_password_hash(password)
        user_already_exist = False

        if not username or not password:
            flash("Enter username and password")
            return redirect(url_for("auth_bp.signup"))
        

        if signed_up_users:    
            for user in signed_up_users:
                if user["username"] == username:
                    user_already_exist = True
            
        if user_already_exist:
            flash("User already exist please login")
            return redirect(url_for("auth_bp.login"))
        else:
            manager.add_users(username, hashed_password)
            flash(error_message.get_error())
            session["username"] = username
            return redirect(url_for("user_bp.home"))
    return render_template("sign_up.html")


@auth_bp.route('/login', methods = ['GET', 'POST'])
def login():
    if "username" in session:
        return redirect(url_for("user_bp.home"))
    
    manager = Manager(ErrorMessage())
    
    if request.method == "POST":
        username = request.form.get("user_name").strip()
        password = request.form.get("user_password").strip()
        manager.login_users(username, password)
        flash(manager.error.get_error())
        return redirect(url_for("user_bp.home"))
    
    return render_template("login.html", error = manager.error.get_error())


@auth_bp.route("/logout", methods= ['POST', 'GET'])
def logout():
    session.pop("username")
    return redirect(url_for("auth_bp.login"))